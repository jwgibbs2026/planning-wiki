"""FastAPI app: the single front door for the merged site.

Serves three things from one origin:
  * /api/*  — the GeoJSON applications API
  * /map    — the Leaflet map UI (assets under /map/static)
  * /       — the built Quartz wiki (static HTML from config.WIKI_PUBLIC_DIR),
              with a shared top nav bar injected into each page

The nav bar is injected at serve time so the published wiki itself is never
modified; it survives Quartz rebuilds and SPA navigation.
"""
from __future__ import annotations

import json
import re
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import config, db

app = FastAPI(title="Gloucestershire Planning Dashboard", version="0.1.0")


# --- Shared top nav bar -----------------------------------------------------

def nav_bar(active: str) -> str:
    """Return the shared top nav bar HTML. `active` is 'guide', 'wiki' or 'map'."""
    guide_cur = ' aria-current="page"' if active == "guide" else ""
    wiki_cur = ' aria-current="page"' if active == "wiki" else ""
    map_cur = ' aria-current="page"' if active == "map" else ""
    return f"""
<div class="pmap-topbar">
  <span class="pmap-brand">Gloucestershire Planning</span>
  <nav class="pmap-tabs">
    <a href="/" data-router-ignore{guide_cur}>Toolkit Guide</a>
    <a href="/wiki" data-router-ignore{wiki_cur}>Planning Wiki</a>
    <a href="/map" data-router-ignore{map_cur}>Planning Map</a>
  </nav>
</div>
<style>
  .pmap-topbar {{
    position: sticky; top: 0; z-index: 10000;
    display: flex; align-items: center; gap: 1.25rem;
    padding: 0.5rem 1rem; background: #2d6a2d; color: #fff;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    box-shadow: 0 1px 4px rgba(0,0,0,.25);
  }}
  .pmap-brand {{ font-weight: 700; letter-spacing: .01em; }}
  .pmap-tabs {{ display: flex; gap: .25rem; }}
  .pmap-tabs a {{
    color: #fff; text-decoration: none; font-weight: 600;
    padding: .3rem .8rem; border-radius: 6px; line-height: 1;
  }}
  .pmap-tabs a:hover {{ background: rgba(255,255,255,.15); }}
  .pmap-tabs a[aria-current="page"] {{ background: rgba(255,255,255,.25); }}
</style>
"""


_BODY_RE = re.compile(rb"(<body[^>]*>)", re.IGNORECASE)
_HEAD_RE = re.compile(rb"(<head[^>]*>)", re.IGNORECASE)


def get_conn() -> sqlite3.Connection:
    return db.connect()


def _feature(row: sqlite3.Row) -> dict | None:
    """Build a GeoJSON Feature for an application (point, or boundary if present)."""
    props = {
        "id": row["id"],
        "authority": row["authority_name"],
        "ref": row["application_ref"],
        "description": row["description"],
        "address": row["address"],
        "received_date": row["received_date"],
        "decision_date": row["decision_date"],
        "status": row["status"],
        "official_url": row["official_url"],
        "planit_url": row["planit_url"],
        "boundary_status": row["boundary_status"],
        "indicative": row["boundary_status"] != "manually_verified",
    }
    geometry = None
    if row["boundary_geom"]:
        try:
            geometry = json.loads(row["boundary_geom"])
        except (ValueError, TypeError):
            geometry = None
    if geometry is None and row["point_geom"]:
        try:
            geometry = json.loads(row["point_geom"])
        except (ValueError, TypeError):
            geometry = None
    if geometry is None and row["latitude"] is not None:
        geometry = {"type": "Point", "coordinates": [row["longitude"], row["latitude"]]}
    if geometry is None:
        return None  # nothing mappable
    return {"type": "Feature", "geometry": geometry, "properties": props}


@app.get("/api/authorities")
def authorities() -> JSONResponse:
    conn = get_conn()
    try:
        rows = db.get_authorities(conn)
        return JSONResponse(
            [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "planit_name": r["planit_name"],
                    "register_url": r["official_register_url"],
                }
                for r in rows
            ]
        )
    finally:
        conn.close()


@app.get("/api/applications")
def applications(
    authority: str | None = Query(None, description="Authority name or PlanIt name"),
    status: str | None = Query(None),
    days: int | None = Query(None, description="Only apps received within N days"),
    bbox: str | None = Query(None, description="minLng,minLat,maxLng,maxLat"),
    limit: int = Query(5000, le=20000),
) -> JSONResponse:
    conn = get_conn()
    try:
        sql = [
            """
            SELECT a.*, au.name AS authority_name
            FROM applications a
            JOIN authorities au ON au.id = a.authority_id
            WHERE 1=1
            """
        ]
        params: list[object] = []
        if authority:
            sql.append("AND (au.name = ? OR au.planit_name = ?)")
            params += [authority, authority]
        if status:
            sql.append("AND a.status = ?")
            params.append(status)
        if days is not None:
            sql.append("AND a.received_date >= date('now', ?)")
            params.append(f"-{int(days)} days")
        if bbox:
            try:
                min_lng, min_lat, max_lng, max_lat = (float(x) for x in bbox.split(","))
            except ValueError:
                raise HTTPException(400, "bbox must be 'minLng,minLat,maxLng,maxLat'")
            sql.append(
                "AND a.longitude BETWEEN ? AND ? AND a.latitude BETWEEN ? AND ?"
            )
            params += [min_lng, max_lng, min_lat, max_lat]
        sql.append("ORDER BY a.received_date DESC LIMIT ?")
        params.append(limit)

        rows = conn.execute("\n".join(sql), params).fetchall()
        features = [f for f in (_feature(r) for r in rows) if f]
        return JSONResponse(
            {"type": "FeatureCollection", "features": features}
        )
    finally:
        conn.close()


@app.get("/api/applications/{app_id}")
def application_detail(app_id: int) -> JSONResponse:
    conn = get_conn()
    try:
        row = conn.execute(
            """
            SELECT a.*, au.name AS authority_name
            FROM applications a JOIN authorities au ON au.id = a.authority_id
            WHERE a.id = ?
            """,
            (app_id,),
        ).fetchone()
        if not row:
            raise HTTPException(404, "application not found")
        return JSONResponse(dict(row))
    finally:
        conn.close()


# --- Map UI (assets under /map/static to avoid clashing with the wiki) ------

@app.get("/map", include_in_schema=False)
@app.get("/map/", include_in_schema=False)
def map_page() -> HTMLResponse:
    html = (config.WEB_DIR / "index.html").read_bytes()
    injected = _BODY_RE.sub(lambda m: m.group(1) + nav_bar("map").encode(), html, count=1)
    return HTMLResponse(injected)


class _NoCacheStatic(StaticFiles):
    """Serve map assets with revalidation so edits show up without a hard refresh."""

    def is_not_modified(self, *args, **kwargs) -> bool:  # always re-send
        return False

    async def get_response(self, path, scope):
        resp = await super().get_response(path, scope)
        resp.headers["Cache-Control"] = "no-cache, must-revalidate"
        return resp


app.mount("/map/static", _NoCacheStatic(directory=str(config.WEB_DIR)), name="map-static")


# --- Toolkit Guide (the landing tab, served at the site root) ---------------

@app.get("/", include_in_schema=False)
@app.get("/guide", include_in_schema=False)
@app.get("/guide/", include_in_schema=False)
def guide_page() -> HTMLResponse:
    html = (config.WEB_DIR / "guide.html").read_bytes()
    injected = _BODY_RE.sub(lambda m: m.group(1) + nav_bar("guide").encode(), html, count=1)
    return HTMLResponse(injected)


# --- Wiki (built Quartz static site), nav bar injected ----------------------
#
# The guide owns the site root, so the wiki home lives at /wiki while every
# wiki content page keeps its real root path (e.g. /biodiversity-.../sssi) via
# the catch-all below. The home's links are './'-relative, so a <base href="/">
# keeps them resolving against the root regardless of the /wiki URL.

@app.get("/wiki", include_in_schema=False)
@app.get("/wiki/", include_in_schema=False)
def wiki_home() -> HTMLResponse:
    index = config.WIKI_PUBLIC_DIR / "index.html"
    if not index.is_file():
        raise HTTPException(
            503,
            "Wiki not built. Run `npx quartz build` in the quartz folder, or set "
            "PLANNING_WIKI_PUBLIC_DIR. The map is available at /map.",
        )
    html = index.read_bytes()
    html = _HEAD_RE.sub(lambda m: m.group(1) + b'<base href="/">', html, count=1)
    injected = _BODY_RE.sub(lambda m: m.group(1) + nav_bar("wiki").encode(), html, count=1)
    return HTMLResponse(injected)

def _resolve_wiki_file(rel_path: str):
    """Map a request path to a file inside WIKI_PUBLIC_DIR (or None).

    Mirrors Quartz's clean-URL scheme: '' -> index.html, 'foo' -> foo/index.html
    (falling back to foo.html), 'a/b.css' -> a/b.css. Guards against traversal.
    """
    root = config.WIKI_PUBLIC_DIR.resolve()
    if not root.is_dir():
        return None
    rel = rel_path.strip("/")
    base = (root / rel).resolve()
    # Prevent escaping the public dir.
    if base != root and root not in base.parents:
        return None

    candidates = []
    if rel == "":
        candidates.append(root / "index.html")
    elif base.suffix:
        candidates.append(base)
    else:
        candidates.append(base / "index.html")
        candidates.append(base.with_suffix(".html"))
    for c in candidates:
        if c.is_file():
            return c
    return None


@app.get("/{path:path}", include_in_schema=False)
def wiki(path: str):
    target = _resolve_wiki_file(path)
    if target is None:
        if not config.WIKI_PUBLIC_DIR.is_dir():
            raise HTTPException(
                503,
                "Wiki not built. Run `npx quartz build` in the quartz folder, or set "
                "PLANNING_WIKI_PUBLIC_DIR. The map is available at /map.",
            )
        raise HTTPException(404, "Not found")

    if target.suffix.lower() in (".html", ".htm"):
        html = target.read_bytes()
        injected = _BODY_RE.sub(lambda m: m.group(1) + nav_bar("wiki").encode(), html, count=1)
        return HTMLResponse(injected)
    return FileResponse(target)

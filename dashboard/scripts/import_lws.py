"""Import a user-supplied Local Wildlife Sites GeoJSON into the map layers.

LWS data is not open data (held by GWT / GCER), so it is supplied as a file.
This script reprojects it to WGS84 if needed, clips it to the Gloucestershire
boundary (the borders.geojson produced by fetch_layers.py), simplifies it, keeps
just the site name, and writes planning_dashboard/web/layers/LWS layer.geojson.

Usage:
  python dashboard/scripts/import_lws.py "C:\\path\\to\\LWS layer.geojson"
  python dashboard/scripts/import_lws.py SRC --src-crs EPSG:27700
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import mapping, shape
from shapely.ops import transform as shp_transform, unary_union

LAYERS_DIR = Path(__file__).resolve().parent.parent / "planning_dashboard" / "web" / "layers"
BORDERS = LAYERS_DIR / "borders.geojson"
OUT = LAYERS_DIR / "LWS layer.geojson"
SIMPLIFY_TOL = 0.00004  # ~4.5m, matches fetch_layers.py

NAME_KEYS = ["sitename", "SITENAME", "name", "NAME", "Name", "LWS_NAME", "SITE_NAME"]


def _name_of(props: dict) -> str | None:
    for k in NAME_KEYS:
        if props.get(k):
            return str(props[k])
    return None


def _to_polygonal(geom):
    if geom.is_empty:
        return None
    t = geom.geom_type
    if t in ("Polygon", "MultiPolygon"):
        polys = geom
    elif t == "GeometryCollection":
        parts = [g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")]
        if not parts:
            return None
        polys = unary_union(parts)
    else:
        return None
    polys = polys.simplify(SIMPLIFY_TOL, preserve_topology=True)
    return None if polys.is_empty else polys


def _detect_crs(gj: dict, sample_geom: dict) -> str:
    crs = (((gj.get("crs") or {}).get("properties") or {}).get("name") or "")
    if "27700" in crs:
        return "EPSG:27700"
    if "4326" in crs or "CRS84" in crs:
        return "EPSG:4326"
    # Heuristic from coordinate magnitude (BNG eastings are in the 10^5 range).
    c = sample_geom["coordinates"]
    while isinstance(c[0], list):
        c = c[0]
    return "EPSG:27700" if abs(c[0]) > 1000 else "EPSG:4326"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="Path to the LWS GeoJSON file")
    ap.add_argument("--src-crs", help="Override source CRS (e.g. EPSG:27700)")
    args = ap.parse_args(argv)

    src = Path(args.source)
    if not src.is_file():
        print(f"Source not found: {src}")
        return 1
    if not BORDERS.is_file():
        print(f"Missing {BORDERS}. Run fetch_layers.py first to create the boundary.")
        return 1

    gj = json.loads(src.read_text(encoding="utf-8-sig"))
    feats = gj.get("features", [])
    if not feats:
        print("No features in source.")
        return 1

    src_crs = args.src_crs or _detect_crs(gj, feats[0]["geometry"])
    print(f"Source CRS: {src_crs}  ({len(feats)} features)")

    # Gloucestershire boundary (WGS84) from borders.geojson.
    borders = json.loads(BORDERS.read_text(encoding="utf-8"))
    boundary = unary_union([shape(f["geometry"]) for f in borders["features"]]).buffer(0)

    if src_crs != "EPSG:4326":
        tr = Transformer.from_crs(src_crs, "EPSG:4326", always_xy=True)
        reproj = lambda g: shp_transform(lambda x, y, z=None: tr.transform(x, y), g)  # noqa: E731
    else:
        reproj = lambda g: g  # noqa: E731

    out = []
    dropped_outside = 0
    for f in feats:
        geom = f.get("geometry")
        if not geom:
            continue
        try:
            g = reproj(shape(geom)).buffer(0)
        except Exception:
            continue
        if not g.intersects(boundary):
            dropped_outside += 1
            continue
        clipped = _to_polygonal(g.intersection(boundary))
        if clipped is None:
            continue
        out.append({
            "type": "Feature",
            "properties": {"name": _name_of(f.get("properties", {}))},
            "geometry": mapping(clipped),
        })

    OUT.write_text(json.dumps({"type": "FeatureCollection", "features": out}), encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print(f"Wrote {OUT.name}: {len(out)} sites in Gloucestershire "
          f"({dropped_outside} outside dropped, {kb:.0f} kB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

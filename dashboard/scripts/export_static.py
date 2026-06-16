"""Export the map data to static files for static hosting (e.g. Netlify).

Writes two files into planning_dashboard/web/:
  * applications.geojson — every mappable application as a GeoJSON FeatureCollection
  * authorities.json     — the authority list used by the filter dropdown

The static map (web/app.js) loads these once and filters in the browser, so the
site needs no running server. Re-run this and redeploy to refresh the map data:

    python scripts/export_static.py
"""
from __future__ import annotations

import json
from pathlib import Path

from planning_dashboard import db
from planning_dashboard.api import _feature

WEB = Path(__file__).resolve().parent.parent / "planning_dashboard" / "web"


def main() -> None:
    conn = db.connect()
    try:
        rows = conn.execute(
            """
            SELECT a.*, au.name AS authority_name
            FROM applications a
            JOIN authorities au ON au.id = a.authority_id
            ORDER BY a.received_date DESC
            """
        ).fetchall()
        features = [f for f in (_feature(r) for r in rows) if f]
        fc = {"type": "FeatureCollection", "features": features}

        auth_rows = db.get_authorities(conn)
        authorities = [{"name": r["name"], "planit_name": r["planit_name"]} for r in auth_rows]
    finally:
        conn.close()

    (WEB / "applications.geojson").write_text(
        json.dumps(fc, separators=(",", ":")), encoding="utf-8"
    )
    (WEB / "authorities.json").write_text(
        json.dumps(authorities, separators=(",", ":")), encoding="utf-8"
    )
    print(f"Wrote {len(features)} features and {len(authorities)} authorities to {WEB}")


if __name__ == "__main__":
    main()

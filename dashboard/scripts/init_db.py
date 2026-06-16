"""Initialise the database: create the schema and seed the seven authorities.

Also re-checks the seeded PlanIt names against the live /api/areas list and
warns (does not fail) on any mismatch.

Usage:  python dashboard/scripts/init_db.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planning_dashboard import config, db  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("init_db")


def verify_planit_names() -> None:
    """Best-effort check that each seeded planit_name is a real PlanIt authority.

    Done by a tiny applications query per authority (the same endpoint the
    importer uses), which directly validates the name we rely on.
    """
    try:
        import requests
    except Exception as exc:  # noqa: BLE001
        log.warning("PlanIt name verification skipped: %s", exc)
        return

    session = requests.Session()
    session.headers.update({"User-Agent": config.USER_AGENT})
    for a in config.AUTHORITIES:
        try:
            resp = session.get(
                f"{config.PLANIT_BASE_URL}/applics/json",
                params={"auth": a.planit_name, "no_kin": "true", "recent": 365, "pg_sz": 1},
                timeout=60,
            )
            resp.raise_for_status()
            rec = (resp.json().get("records") or [{}])[0]
            area = rec.get("area_name")
            if area == a.planit_name:
                log.info("  OK  %-32s -> PlanIt '%s'", a.name, a.planit_name)
            elif area:
                log.warning(
                    "  ??  %-32s -> expected '%s' but PlanIt returned '%s'",
                    a.name, a.planit_name, area,
                )
            else:
                log.warning(
                    "  ??  %-32s -> PlanIt '%s' returned no records (verify name)",
                    a.name, a.planit_name,
                )
        except Exception as exc:  # noqa: BLE001 - advisory only
            log.warning("  ??  %-32s -> check failed: %s", a.name, exc)


def main() -> int:
    conn = db.connect()
    spatial = db.spatialite_available(conn)
    log.info(
        "Database: %s  (SpatiaLite extension: %s)",
        config.DB_PATH,
        "loaded" if spatial else "not available - using GeoJSON text fallback",
    )
    db.init_schema(conn)
    n = db.seed_authorities(conn)
    log.info("Schema created. %d authorities seeded.", n)
    verify_planit_names()
    log.info("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

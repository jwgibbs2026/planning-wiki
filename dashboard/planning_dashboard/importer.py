"""Daily importer: pull recent/changed applications from PlanIt and upsert them.

Per-authority isolation: each authority is imported inside its own try/except so
a single failing authority is logged and skipped without aborting the whole run.
Existing boundary data is never clobbered by a metadata refresh.
"""
from __future__ import annotations

import argparse
import logging
import sqlite3

from . import config, db
from .planit import PlanItClient, days_ago_iso, normalize_record, utc_now_iso

log = logging.getLogger(__name__)

# Columns updated on every refresh. boundary_geom / boundary_status are pointedly
# excluded so Phase 4 extraction results survive a metadata re-import.
_UPSERT_SQL = """
INSERT INTO applications (
    authority_id, application_ref, description, address,
    received_date, validated_date, decision_date, status,
    official_url, planit_url, latitude, longitude, point_geom,
    last_checked_at, source
) VALUES (
    :authority_id, :application_ref, :description, :address,
    :received_date, :validated_date, :decision_date, :status,
    :official_url, :planit_url, :latitude, :longitude, :point_geom,
    :last_checked_at, :source
)
ON CONFLICT(authority_id, application_ref) DO UPDATE SET
    description     = excluded.description,
    address         = excluded.address,
    received_date   = excluded.received_date,
    validated_date  = excluded.validated_date,
    decision_date   = excluded.decision_date,
    status          = excluded.status,
    official_url    = excluded.official_url,
    planit_url      = excluded.planit_url,
    latitude        = COALESCE(excluded.latitude, applications.latitude),
    longitude       = COALESCE(excluded.longitude, applications.longitude),
    point_geom      = COALESCE(excluded.point_geom, applications.point_geom),
    last_checked_at = excluded.last_checked_at,
    source          = excluded.source
"""


def import_authority(
    conn: sqlite3.Connection,
    authority: sqlite3.Row,
    client: PlanItClient,
    *,
    days: int | None = None,
    force_backfill: bool = False,
) -> dict:
    """Import one authority. Returns a small stats dict."""
    authority_id = authority["id"]
    watermark = None if force_backfill else db.get_sync_watermark(conn, authority_id)

    if watermark:
        # PlanIt's changed_start accepts date only (YYYY-MM-DD); re-fetching the
        # whole watermark day is harmless because upserts are idempotent.
        since_date = watermark[:10]
        kwargs = {"changed_start": since_date}
        mode = f"incremental since {since_date}"
    else:
        backfill = days if days is not None else config.BACKFILL_DAYS
        kwargs = {"recent": backfill}
        mode = f"backfill last {backfill} days"

    log.info("Importing %s (%s) [%s]", authority["name"], authority["planit_name"], mode)

    now = utc_now_iso()
    count = 0
    max_changed = watermark
    for rec in client.fetch_applications(authority["planit_name"], **kwargs):
        row = normalize_record(rec)
        if not row.get("application_ref"):
            continue
        row["authority_id"] = authority_id
        row["last_checked_at"] = now
        conn.execute(_UPSERT_SQL, row)
        count += 1
        lc = row.get("last_changed")
        if lc and (max_changed is None or lc > max_changed):
            max_changed = lc
    conn.commit()
    db.set_sync_state(conn, authority_id, max_changed)
    log.info("  %s: %d applications upserted", authority["name"], count)
    return {"authority": authority["name"], "count": count, "mode": mode}


def import_all(
    conn: sqlite3.Connection,
    *,
    only: str | None = None,
    days: int | None = None,
    force_backfill: bool = False,
) -> list[dict]:
    """Import every seeded authority (or just ``only`` by name/planit_name)."""
    client = PlanItClient()
    results: list[dict] = []
    for authority in db.get_authorities(conn):
        if only and only.lower() not in (
            authority["name"].lower(),
            authority["planit_name"].lower(),
        ):
            continue
        try:
            results.append(
                import_authority(
                    conn, authority, client, days=days, force_backfill=force_backfill
                )
            )
        except Exception as exc:  # noqa: BLE001 - isolate per-authority failures
            log.exception("Authority %s failed: %s", authority["name"], exc)
            results.append(
                {"authority": authority["name"], "error": str(exc), "count": 0}
            )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import PlanIt applications into the DB")
    parser.add_argument(
        "--authority", help="Only import this authority (name or PlanIt name)"
    )
    parser.add_argument(
        "--days", type=int, help="Backfill window in days (overrides default)"
    )
    parser.add_argument(
        "--force-backfill",
        action="store_true",
        help="Ignore the sync watermark and re-fetch the backfill window",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose logging"
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    conn = db.connect()
    db.init_schema(conn)
    if db.seed_authorities(conn) == 0:
        log.error("No authorities seeded; aborting.")
        return 1

    results = import_all(
        conn,
        only=args.authority,
        days=args.days,
        force_backfill=args.force_backfill,
    )
    total = sum(r.get("count", 0) for r in results)
    errors = [r for r in results if r.get("error")]
    log.info("Done. %d applications across %d authorities.", total, len(results))
    if errors:
        log.warning("%d authorities failed: %s", len(errors), [e["authority"] for e in errors])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""PlanIt API client (https://www.planit.org.uk/api/).

All knowledge of the PlanIt request/response shape is isolated here:

* :class:`PlanItClient` paginates ``/applics/`` with polite delays and
  exponential backoff on HTTP 429 / 5xx.
* :func:`normalize_record` maps one PlanIt record onto our ``applications`` row
  shape (a plain dict), independent of the network so it is unit-testable.
"""
from __future__ import annotations

import json
import logging
import time
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone

import requests

from . import config

log = logging.getLogger(__name__)

PAGE_SIZE = 300  # PlanIt's maximum page size
MAX_RETRIES = 5


class PlanItError(RuntimeError):
    pass


class PlanItClient:
    def __init__(
        self,
        base_url: str = config.PLANIT_BASE_URL,
        delay: float = config.REQUEST_DELAY,
        user_agent: str = config.USER_AGENT,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.delay = delay
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def _get(self, path: str, params: dict) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        backoff = 2.0
        for attempt in range(1, MAX_RETRIES + 1):
            resp = self.session.get(url, params=params, timeout=60)
            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt == MAX_RETRIES:
                    raise PlanItError(
                        f"{resp.status_code} from PlanIt after {attempt} attempts: {url}"
                    )
                wait = backoff ** attempt
                log.warning(
                    "PlanIt %s (attempt %d/%d) -> backing off %.1fs",
                    resp.status_code, attempt, MAX_RETRIES, wait,
                )
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        raise PlanItError("unreachable")

    def fetch_applications(
        self,
        auth: str,
        *,
        recent: int | None = None,
        changed_start: str | None = None,
    ) -> Iterator[dict]:
        """Yield raw PlanIt application records for an authority.

        Use ``recent`` (days) for a backfill, or ``changed_start`` (ISO date/
        datetime) for an incremental sync of only changed records. Results are
        paginated transparently.
        """
        params: dict[str, object] = {
            "auth": auth,
            "no_kin": "true",  # this authority only, exclude sub-areas
            "pg_sz": PAGE_SIZE,
        }
        if changed_start:
            params["changed_start"] = changed_start
        elif recent is not None:
            params["recent"] = recent

        page = 1
        seen = 0
        while True:
            params["page"] = page
            data = self._get("applics/json", params)
            records = data.get("records", [])
            if not records:
                break
            for rec in records:
                yield rec
            seen += len(records)
            total = data.get("total", seen)
            if seen >= total or len(records) < PAGE_SIZE:
                break
            page += 1
            time.sleep(self.delay)


def _first(rec: dict, *keys: str):
    for k in keys:
        v = rec.get(k)
        if v not in (None, ""):
            return v
    return None


def normalize_record(rec: dict) -> dict:
    """Map a raw PlanIt record onto our ``applications`` row fields.

    Returns a dict keyed by our column names (minus authority_id, which the
    importer resolves). ``planit_name`` carries the PlanIt ``area_name`` so the
    importer can attach it to the right authority.
    """
    location = rec.get("location")
    lat = lng = None
    point_geom = None
    if isinstance(location, dict) and location.get("type") == "Point":
        coords = location.get("coordinates") or []
        if len(coords) == 2:
            lng, lat = float(coords[0]), float(coords[1])
            point_geom = json.dumps(location)
    if lat is None and rec.get("location_y") is not None:
        lat = float(rec["location_y"])
        lng = float(rec["location_x"])
        point_geom = json.dumps({"type": "Point", "coordinates": [lng, lat]})

    address = rec.get("address")
    postcode = rec.get("postcode")
    if address and postcode and postcode not in address:
        address = f"{address}, {postcode}"

    return {
        "application_ref": _first(rec, "uid", "name", "reference"),
        "planit_name": rec.get("area_name"),
        "description": rec.get("description"),
        "address": address,
        "received_date": rec.get("start_date"),
        "validated_date": rec.get("consulted_date"),
        "decision_date": rec.get("decided_date"),
        "status": rec.get("app_state"),
        "official_url": rec.get("url"),
        "planit_url": rec.get("link"),
        "latitude": lat,
        "longitude": lng,
        "point_geom": point_geom,
        "last_changed": rec.get("last_changed"),
        "source": "planit",
    }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def days_ago_iso(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()

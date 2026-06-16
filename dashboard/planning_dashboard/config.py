"""Configuration and the seed list of Gloucestershire planning authorities.

Settings are read from environment variables (optionally loaded from a local
``.env`` file) with safe defaults so the app runs with zero configuration.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:  # optional; the app works without python-dotenv installed
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is a convenience only
    pass

# dashboard/ folder (parent of this package)
BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = Path(__file__).resolve().parent / "web"


def _path(env: str, default: str) -> Path:
    raw = os.getenv(env, default)
    p = Path(raw)
    return p if p.is_absolute() else (BASE_DIR / p)


DB_PATH: Path = _path("PLANNING_DB_PATH", "data/planning.sqlite")

# The built Quartz wiki (static HTML) served at the site root. Override with
# PLANNING_WIKI_PUBLIC_DIR. If the directory is missing, the wiki simply isn't
# served (the map still works at /map).
WIKI_PUBLIC_DIR: Path = Path(
    os.getenv("PLANNING_WIKI_PUBLIC_DIR", r"C:\Users\jwgib\Documents\quartz-5\public")
)

BACKFILL_DAYS: int = int(os.getenv("PLANNING_BACKFILL_DAYS", "90"))
REQUEST_DELAY: float = float(os.getenv("PLANNING_REQUEST_DELAY", "1.0"))
USER_AGENT: str = os.getenv(
    "PLANNING_USER_AGENT",
    "GlosPlanningWiki/0.1 (private; local use)",
)

PLANIT_BASE_URL = "https://www.planit.org.uk/api"


@dataclass(frozen=True)
class AuthoritySeed:
    name: str  # human-readable name used in the UI
    planit_name: str  # PlanIt `area_name` / `auth` value
    official_register_url: str  # the council's public planning register landing page


# The seven monitored authorities. `planit_name` values were observed live; the
# init step re-checks them against GET /api/areas/json and warns on mismatch.
AUTHORITIES: list[AuthoritySeed] = [
    AuthoritySeed(
        "Gloucester City Council",
        "Gloucester",
        "https://publicaccess.gloucester.gov.uk/online-applications/",
    ),
    AuthoritySeed(
        "Cheltenham Borough Council",
        "Cheltenham",
        "https://publicaccess.cheltenham.gov.uk/online-applications/",
    ),
    AuthoritySeed(
        "Gloucestershire County Council",
        "Gloucestershire",
        "https://www.gloucestershire.gov.uk/planning/",
    ),
    AuthoritySeed(
        "Tewkesbury Borough Council",
        "Tewkesbury",
        "https://publicaccess.tewkesbury.gov.uk/online-applications/",
    ),
    AuthoritySeed(
        "Forest of Dean District Council",
        "Forest of Dean",
        "https://publicaccess.fdean.gov.uk/online-applications/",
    ),
    AuthoritySeed(
        "Stroud District Council",
        "Stroud",
        "https://publicaccess.stroud.gov.uk/online-applications/",
    ),
    AuthoritySeed(
        "Cotswold District Council",
        "Cotswold",
        "https://publicaccess.cotswold.gov.uk/online-applications/",
    ),
]

# Allowed values for applications.boundary_status (enforced by a CHECK constraint).
BOUNDARY_STATUSES = (
    "none",
    "candidate_document_found",
    "extracted_unchecked",
    "manually_verified",
    "failed",
)

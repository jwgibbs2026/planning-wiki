"""SQLite database layer.

Geometry is stored as GeoJSON *text* in ``point_geom`` / ``boundary_geom`` plus
plain ``latitude`` / ``longitude`` numeric columns. This keeps Phase 1 working on
any platform (notably Windows) without the native SpatiaLite extension. We still
*attempt* to load ``mod_spatialite`` so spatial SQL is available when present;
the result is reported via :func:`spatialite_available` but nothing depends on it.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS authorities (
    id                    INTEGER PRIMARY KEY,
    name                  TEXT NOT NULL UNIQUE,
    planit_name           TEXT NOT NULL UNIQUE,
    official_register_url TEXT
);

CREATE TABLE IF NOT EXISTS applications (
    id              INTEGER PRIMARY KEY,
    authority_id    INTEGER NOT NULL REFERENCES authorities(id),
    application_ref TEXT NOT NULL,
    description     TEXT,
    address         TEXT,
    received_date   TEXT,
    validated_date  TEXT,
    decision_date   TEXT,
    status          TEXT,
    official_url    TEXT,
    planit_url      TEXT,
    latitude        REAL,
    longitude       REAL,
    point_geom      TEXT,           -- GeoJSON Point
    boundary_geom   TEXT,           -- GeoJSON Polygon/MultiPolygon (Phase 4)
    boundary_status TEXT NOT NULL DEFAULT 'none'
        CHECK (boundary_status IN
            ('none','candidate_document_found','extracted_unchecked',
             'manually_verified','failed')),
    last_checked_at TEXT,
    source          TEXT NOT NULL DEFAULT 'planit',
    UNIQUE (authority_id, application_ref)
);
CREATE INDEX IF NOT EXISTS idx_applications_authority ON applications(authority_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_received ON applications(received_date);

CREATE TABLE IF NOT EXISTS documents (
    id                        INTEGER PRIMARY KEY,
    application_id            INTEGER NOT NULL REFERENCES applications(id),
    title                     TEXT,
    document_type_guess       TEXT,
    document_url              TEXT,
    local_file_path           TEXT,
    date_published            TEXT,
    classification_confidence REAL,
    is_candidate_location_plan INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_documents_application ON documents(application_id);

CREATE TABLE IF NOT EXISTS boundary_extractions (
    id              INTEGER PRIMARY KEY,
    document_id     INTEGER NOT NULL REFERENCES documents(id),
    method          TEXT,
    geojson         TEXT,
    confidence      REAL,
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    verified_by_user INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_extractions_document ON boundary_extractions(document_id);

-- Per-authority incremental-sync watermark (max last_changed seen).
CREATE TABLE IF NOT EXISTS sync_state (
    authority_id INTEGER PRIMARY KEY REFERENCES authorities(id),
    last_changed TEXT,
    last_run_at  TEXT
);
"""


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a connection with sensible pragmas and row access by name."""
    path = Path(db_path) if db_path else config.DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def spatialite_available(conn: sqlite3.Connection) -> bool:
    """Best-effort attempt to load mod_spatialite; never raises."""
    try:
        conn.enable_load_extension(True)
        for name in ("mod_spatialite", "mod_spatialite.dll", "libspatialite"):
            try:
                conn.load_extension(name)
                return True
            except sqlite3.OperationalError:
                continue
    except (AttributeError, sqlite3.OperationalError):
        # enable_load_extension is disabled in some Python builds.
        pass
    finally:
        try:
            conn.enable_load_extension(False)
        except (AttributeError, sqlite3.OperationalError):
            pass
    return False


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def seed_authorities(conn: sqlite3.Connection) -> int:
    """Insert/update the seven seeded authorities. Returns the row count."""
    rows = [
        (a.name, a.planit_name, a.official_register_url) for a in config.AUTHORITIES
    ]
    conn.executemany(
        """
        INSERT INTO authorities (name, planit_name, official_register_url)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            planit_name = excluded.planit_name,
            official_register_url = excluded.official_register_url
        """,
        rows,
    )
    conn.commit()
    return conn.execute("SELECT COUNT(*) FROM authorities").fetchone()[0]


def get_authorities(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM authorities ORDER BY name"
    ).fetchall()


def get_sync_watermark(conn: sqlite3.Connection, authority_id: int) -> str | None:
    row = conn.execute(
        "SELECT last_changed FROM sync_state WHERE authority_id = ?", (authority_id,)
    ).fetchone()
    return row["last_changed"] if row else None


def set_sync_state(
    conn: sqlite3.Connection, authority_id: int, last_changed: str | None
) -> None:
    conn.execute(
        """
        INSERT INTO sync_state (authority_id, last_changed, last_run_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(authority_id) DO UPDATE SET
            last_changed = COALESCE(excluded.last_changed, sync_state.last_changed),
            last_run_at = excluded.last_run_at
        """,
        (authority_id, last_changed),
    )
    conn.commit()

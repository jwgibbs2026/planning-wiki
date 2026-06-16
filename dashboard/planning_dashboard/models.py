"""Lightweight row dataclasses used across the app.

The PlanIt-record -> applications-row mapping lives in :mod:`planit` (function
``normalize_record``) so all API-shape knowledge stays in one place.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Authority:
    id: int
    name: str
    planit_name: str
    official_register_url: str | None = None


@dataclass
class Application:
    authority_id: int
    application_ref: str
    description: str | None = None
    address: str | None = None
    received_date: str | None = None
    validated_date: str | None = None
    decision_date: str | None = None
    status: str | None = None
    official_url: str | None = None
    planit_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    point_geom: str | None = None  # GeoJSON text
    boundary_geom: str | None = None
    boundary_status: str = "none"
    last_checked_at: str | None = None
    source: str = "planit"

"""Unit tests for the PlanIt record -> applications-row mapping.

Sample mirrors a real record observed from /api/applics/json (Cotswold).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planning_dashboard.classify.title_rules import (  # noqa: E402
    classify_title,
    is_candidate_location_plan,
)
from planning_dashboard.planit import normalize_record  # noqa: E402

SAMPLE = {
    "name": "Cotswold/26/01825/TCONR",
    "uid": "26/01825/TCONR",
    "reference": None,
    "area_name": "Cotswold",
    "address": "Friars Garth Church Lane Evenlode Moreton-In-Marsh",
    "postcode": "GL56 0NY",
    "description": "T1 leyland cypress - Fell",
    "start_date": "2026-06-11",
    "consulted_date": "2026-06-20",
    "decided_date": None,
    "app_state": "Undecided",
    "app_type": "Trees",
    "url": "https://publicaccess.cotswold.gov.uk/online-applications/foo",
    "link": "https://www.planit.org.uk/planapplic/Cotswold/26-01825-TCONR",
    "location": {"type": "Point", "coordinates": [-1.679223, 51.959553]},
    "location_x": -1.679223,
    "location_y": 51.959553,
    "last_changed": "2026-06-15T07:46:30.357161",
}


def test_normalize_core_fields():
    row = normalize_record(SAMPLE)
    assert row["application_ref"] == "26/01825/TCONR"
    assert row["planit_name"] == "Cotswold"
    assert row["description"] == "T1 leyland cypress - Fell"
    assert row["received_date"] == "2026-06-11"
    assert row["validated_date"] == "2026-06-20"
    assert row["decision_date"] is None
    assert row["status"] == "Undecided"
    assert row["source"] == "planit"


def test_normalize_official_url_is_council_not_planit():
    row = normalize_record(SAMPLE)
    assert "publicaccess.cotswold.gov.uk" in row["official_url"]
    assert "planit.org.uk" in row["planit_url"]


def test_normalize_geometry():
    row = normalize_record(SAMPLE)
    assert row["latitude"] == 51.959553
    assert row["longitude"] == -1.679223
    assert '"Point"' in row["point_geom"]


def test_normalize_appends_postcode():
    row = normalize_record(SAMPLE)
    assert row["address"].endswith("GL56 0NY")


def test_geometry_falls_back_to_location_xy():
    rec = dict(SAMPLE, location=None)
    row = normalize_record(rec)
    assert row["latitude"] == 51.959553
    assert row["point_geom"] is not None


def test_title_rules():
    assert classify_title("Proposed Site Location Plan.pdf") == "Site Location Plan"
    assert classify_title("Block Plan 1:500") == "Block Plan"
    assert classify_title("Heritage Statement") is None
    assert is_candidate_location_plan("Location Plan")
    assert not is_candidate_location_plan("Design and Access Statement")

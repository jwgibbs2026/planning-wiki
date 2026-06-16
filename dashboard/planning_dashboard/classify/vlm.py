"""Phase 3 scaffold: Claude vision classification of a planning drawing (STUB).

Inspired by i-dot-ai/planning-drawing-validator. Given a rendered image of a
drawing page, ask a vision-capable Claude model whether it is actually a
location/site plan and which kind, returning a structured result with confidence.

Not wired up in Phase 1/2. Requires the `anthropic` package and ANTHROPIC_API_KEY.
Recommended model id: claude-opus-4-8 (or another current vision-capable Claude).
"""
from __future__ import annotations

from dataclasses import dataclass

DRAWING_TYPES = (
    "Site Location Plan",
    "Location Plan",
    "Block Plan",
    "Existing Site Plan",
    "Proposed Site Plan",
    "Other",
)


@dataclass
class ClassificationResult:
    is_location_plan: bool
    drawing_type: str
    confidence: float
    notes: str | None = None


def classify_drawing(image_path: str, model: str = "claude-opus-4-8") -> ClassificationResult:
    raise NotImplementedError(
        "Phase 3: render the drawing and call a vision-capable Claude model here."
    )

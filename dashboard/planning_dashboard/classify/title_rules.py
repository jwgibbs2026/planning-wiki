"""Keyword-based classification of planning-document titles (implemented).

Identifies documents whose titles suggest they are candidates for red-line
boundary extraction. Document *types* mirror the i-dot-ai planning-drawing-
validator categories. This is deliberately conservative: a positive here only
marks a PDF as a *candidate*; Phase 3 VLM classification confirms the drawing.
"""
from __future__ import annotations

import re

# Ordered most-specific first; first match wins.
_TYPE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("Site Location Plan", re.compile(r"\bsite\s+location\s+plan\b", re.I)),
    ("Location Plan", re.compile(r"\blocation\s+plan\b", re.I)),
    ("Block Plan", re.compile(r"\bblock\s+plan\b", re.I)),
    ("Existing Site Plan", re.compile(r"\bexisting\s+site\s+plan\b", re.I)),
    ("Proposed Site Plan", re.compile(r"\bproposed\s+site\s+plan\b", re.I)),
    ("Site Plan", re.compile(r"\bsite\s+plan\b", re.I)),
]

# Types that are candidates for red-line boundary extraction.
_CANDIDATE_TYPES = {
    "Site Location Plan",
    "Location Plan",
    "Block Plan",
    "Existing Site Plan",
    "Proposed Site Plan",
    "Site Plan",
}


def classify_title(title: str | None) -> str | None:
    """Return a best-guess document type from a title, or None."""
    if not title:
        return None
    for type_name, pattern in _TYPE_PATTERNS:
        if pattern.search(title):
            return type_name
    return None


def is_candidate_location_plan(title: str | None) -> bool:
    """True if the title suggests a document worth attempting extraction on."""
    return classify_title(title) in _CANDIDATE_TYPES

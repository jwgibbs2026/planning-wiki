"""Drawing-classification package.

* :mod:`title_rules` (implemented) -- cheap keyword detection of candidate
  location/site plans from document titles; usable as soon as Phase 2 scraping
  produces document titles.
* :mod:`vlm` (Phase 3 stub) -- Claude vision classification of the actual drawing.
"""
from .title_rules import classify_title, is_candidate_location_plan  # noqa: F401

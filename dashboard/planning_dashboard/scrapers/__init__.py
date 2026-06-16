"""Phase 2 scaffold: per-council document scrapers.

Nothing here runs in Phase 1. The design goal is modularity: each authority has
its own scraper registered against :data:`REGISTRY`, all sharing the polite
fetching helpers in :mod:`planning_dashboard.scrapers.base`. A broken council
scraper must never break the others or the importer.
"""
from .base import REGISTRY, BaseDocumentScraper, DocumentMeta  # noqa: F401

"""Phase 2 scaffold: per-council scraper overrides.

Each Gloucestershire authority gets its own subclass so portal quirks are fixed
in isolation. Most are expected to inherit the generic IdoxPublicAccessScraper;
Gloucestershire County Council may differ and is flagged for its own handling.

To implement in Phase 2, give each class a real ``fetch_document_list`` (or simply
inherit the iDox one) and register it, e.g.::

    @register("Cotswold")
    class CotswoldScraper(IdoxPublicAccessScraper):
        pass

Nothing here is wired up in Phase 1.
"""
from ..idox import IdoxPublicAccessScraper  # noqa: F401

# planit_name -> expected portal family (for Phase 2 reference).
COUNCIL_PORTALS = {
    "Gloucester": "idox",
    "Cheltenham": "idox",
    "Tewkesbury": "idox",
    "Forest of Dean": "idox",
    "Stroud": "idox",
    "Cotswold": "idox",
    "Gloucestershire": "unknown",  # county register differs - confirm in Phase 2
}

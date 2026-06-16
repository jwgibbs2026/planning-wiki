"""Phase 2 scaffold: generic iDox / PublicAccess document-list scraper (STUB).

Most Gloucestershire portals run iDox PublicAccess (publicaccess.<council>.gov.uk),
whose application page exposes a "Documents" tab at
``...applicationDetails.do?activeTab=documents&keyVal=...``.

When implemented (Phase 2) this will, politely:
  1. resolve the documents tab URL from an application's official_url,
  2. parse the document table rows (title, date, download link),
  3. tag candidate location/site plans via classify.title_rules,
returning DocumentMeta records. requests+BeautifulSoup first; Playwright only if
a portal requires JavaScript.
"""
from __future__ import annotations

from .base import BaseDocumentScraper, DocumentMeta


class IdoxPublicAccessScraper(BaseDocumentScraper):
    name = "idox"
    requires_javascript = False

    def fetch_document_list(self, official_url: str) -> list[DocumentMeta]:
        raise NotImplementedError(
            "Phase 2: implement iDox PublicAccess documents-tab scraping here."
        )

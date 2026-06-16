"""Phase 2 scaffold: scraper interface + politeness helpers (NOT yet implemented).

Reference pattern: tpximpact/wearefuturegov planning-viability-doc-scraper, which
walks an iDox/PublicAccess "Documents" tab and lists candidate PDFs. We do NOT
assume it works out of the box for Gloucestershire portals — each council gets a
modular scraper that can be fixed in isolation.

Constraints baked in for when this is implemented:
  * respect robots.txt and rate limits (see RateLimiter / robots_allows)
  * store document METADATA and links only -- never republish drawings
"""
from __future__ import annotations

import time
import urllib.robotparser
from abc import ABC, abstractmethod
from dataclasses import dataclass
from urllib.parse import urlparse

from .. import config


@dataclass
class DocumentMeta:
    title: str
    document_url: str
    document_type_guess: str | None = None
    date_published: str | None = None
    is_candidate_location_plan: bool = False


class RateLimiter:
    """Simple per-host minimum-interval limiter."""

    def __init__(self, min_interval: float = config.REQUEST_DELAY) -> None:
        self.min_interval = min_interval
        self._last: dict[str, float] = {}

    def wait(self, url: str) -> None:
        host = urlparse(url).netloc
        now = time.monotonic()
        elapsed = now - self._last.get(host, 0.0)
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last[host] = time.monotonic()


def robots_allows(url: str, user_agent: str = config.USER_AGENT) -> bool:
    """Check a URL against the site's robots.txt (fails open on error)."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:  # noqa: BLE001 - if robots unreadable, proceed cautiously
        return True
    return rp.can_fetch(user_agent, url)


class BaseDocumentScraper(ABC):
    """Subclass per council. Implemented in Phase 2."""

    name: str = "base"
    requires_javascript: bool = False  # set True to use Playwright

    def __init__(self, rate_limiter: RateLimiter | None = None) -> None:
        self.rate_limiter = rate_limiter or RateLimiter()

    @abstractmethod
    def fetch_document_list(self, official_url: str) -> list[DocumentMeta]:
        """Return candidate documents for an application's official page."""
        raise NotImplementedError


# authority planit_name -> scraper class. Populated by council modules in Phase 2.
REGISTRY: dict[str, type[BaseDocumentScraper]] = {}


def register(planit_name: str):
    def _wrap(cls: type[BaseDocumentScraper]) -> type[BaseDocumentScraper]:
        REGISTRY[planit_name] = cls
        return cls

    return _wrap

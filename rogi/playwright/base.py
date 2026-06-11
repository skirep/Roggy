"""Abstract base class for supermarket Playwright scrapers."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

logger = logging.getLogger(__name__)


class BaseSupermarket(ABC):
    """
    All supermarket scrapers must inherit from this class.

    Subclasses implement :meth:`search` and optionally :meth:`add_to_basket`.

    IMPORTANT: :meth:`checkout` is intentionally NOT implemented in base class.
    Any checkout flow MUST be initiated only after explicit user confirmation.
    """

    name: str = "base"
    base_url: str = ""

    def __init__(self, headless: bool = True) -> None:
        self._headless = headless
        self._playwright: Optional[Any] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Launch browser."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self._headless)
        self._context = await self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        logger.info("Browser started for %s", self.name)

    async def stop(self) -> None:
        """Close browser."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Browser stopped for %s", self.name)

    async def __aenter__(self) -> "BaseSupermarket":
        await self.start()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.stop()

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for *query* on the supermarket website.

        Returns a list of dicts with at minimum:
          - name: str
          - price: float
          - unit: str
          - url: str
          - image_url: str (optional)
        """

    async def add_to_basket(self, product_url: str) -> bool:
        """
        Add a product to the online basket.

        Returns True on success.  Default implementation raises NotImplementedError.
        """
        raise NotImplementedError(f"{self.name} does not support add_to_basket yet.")

    # ------------------------------------------------------------------
    # Protected helpers
    # ------------------------------------------------------------------

    async def _new_page(self) -> Page:
        if self._context is None:
            raise RuntimeError("Browser not started. Call start() or use as context manager.")
        return await self._context.new_page()

    async def _safe_text(self, page: Page, selector: str, default: str = "") -> str:
        """Return inner text of first matching element, or *default*."""
        try:
            el = page.locator(selector).first
            return (await el.inner_text()).strip()
        except Exception:
            return default

    async def _safe_attr(self, page: Page, selector: str, attr: str, default: str = "") -> str:
        """Return an attribute of first matching element, or *default*."""
        try:
            el = page.locator(selector).first
            val = await el.get_attribute(attr)
            return val or default
        except Exception:
            return default

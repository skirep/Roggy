"""Shopping agent – searches and compares products via Playwright supermarket automation."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..database.models import ShoppingListModel
from ..database.repository import Repository

logger = logging.getLogger(__name__)


class ShoppingAgent:
    """
    Orchestrates product search and basket management across supermarkets.

    Actual browsing is delegated to supermarket-specific scrapers in
    rogi/playwright/supermarkets/.  This agent handles business logic:
    merging results, persisting lists, and enforcing the "confirm before
    checkout" rule.
    """

    def __init__(self, repo: Repository) -> None:
        self._repo = repo
        self._supermarkets: Dict[str, Any] = {}

    def register_supermarket(self, name: str, scraper: Any) -> None:
        """Register a supermarket scraper (BaseSupermarket subclass)."""
        self._supermarkets[name.lower()] = scraper
        logger.info("Registered supermarket scraper: %s", name)

    def available_supermarkets(self) -> List[str]:
        return list(self._supermarkets.keys())

    # ------------------------------------------------------------------
    # Search & compare
    # ------------------------------------------------------------------

    async def search(
        self,
        query: str,
        supermarket: Optional[str] = None,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search for a product across one or all registered supermarkets."""
        targets = (
            {supermarket.lower(): self._supermarkets[supermarket.lower()]}
            if supermarket and supermarket.lower() in self._supermarkets
            else self._supermarkets
        )
        results: List[Dict[str, Any]] = []
        for name, scraper in targets.items():
            try:
                items = await scraper.search(query, max_results=max_results)
                for item in items:
                    item["supermarket"] = name
                results.extend(items)
            except Exception as exc:
                logger.warning("Search failed for %s: %s", name, exc)
        return results

    async def compare(self, product_name: str) -> List[Dict[str, Any]]:
        """Return price comparison for *product_name* across all supermarkets."""
        results = await self.search(product_name, max_results=3)
        return sorted(results, key=lambda r: r.get("price", float("inf")))

    # ------------------------------------------------------------------
    # Shopping list management (never auto-checkout)
    # ------------------------------------------------------------------

    def create_list_from_items(
        self,
        name: str,
        items: List[Dict[str, Any]],
    ) -> ShoppingListModel:
        """Persist a shopping list with status='pending' (awaits user confirmation)."""
        total = sum(it.get("price", 0) * it.get("quantity", 1) for it in items)
        shopping = ShoppingListModel(name=name, items=items, total_cost=total, status="pending")
        list_id = self._repo.save_shopping_list(shopping)
        shopping.id = list_id
        logger.info("Shopping list '%s' saved (id=%s). Awaiting user confirmation.", name, list_id)
        return shopping

    def confirm_list(self, list_id: int) -> None:
        """Mark a shopping list as confirmed by the user (still not ordered)."""
        self._repo.update_shopping_status(list_id, "confirmed")
        logger.info("Shopping list %s confirmed by user.", list_id)

    def mark_ordered(self, list_id: int) -> None:
        """
        Mark a list as ordered.

        This should only be called AFTER explicit user confirmation.
        ROGI never calls this automatically.
        """
        self._repo.update_shopping_status(list_id, "ordered")
        logger.info("Shopping list %s marked as ordered.", list_id)

    def get_list(self, list_id: int) -> Optional[ShoppingListModel]:
        return self._repo.get_shopping_list(list_id)

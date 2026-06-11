"""
Example supermarket scraper – serves as a template for real implementations.

To add a new supermarket:
1. Create a new file in rogi/playwright/supermarkets/, e.g. mercadona.py
2. Subclass BaseSupermarket
3. Implement the `search` method
4. Register it in the ShoppingAgent via agent.register_supermarket("mercadona", MercadonaScraper())
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from ..base import BaseSupermarket

logger = logging.getLogger(__name__)


class ExampleSupermarket(BaseSupermarket):
    """
    Demonstration scraper that returns mock data.

    Replace with real selectors for an actual supermarket.
    """

    name = "example"
    base_url = "https://example-supermarket.com"

    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Return mock search results.

        A real implementation would:
        1. Open a page in the browser
        2. Navigate to the search URL
        3. Wait for product cards to load
        4. Extract name, price, unit, url from each card
        """
        logger.info("[ExampleSupermarket] Searching for '%s' (mock)", query)
        mock_results = [
            {
                "name": f"{query} – Brand A",
                "price": 1.99,
                "unit": "kg",
                "url": f"{self.base_url}/products/brand-a",
                "image_url": "",
            },
            {
                "name": f"{query} – Brand B",
                "price": 2.49,
                "unit": "kg",
                "url": f"{self.base_url}/products/brand-b",
                "image_url": "",
            },
        ]
        return mock_results[:max_results]

    async def add_to_basket(self, product_url: str) -> bool:
        """
        Add the product at *product_url* to the basket.

        A real implementation would:
        1. Navigate to product_url
        2. Click the "Add to basket" button
        3. Verify the basket counter increased

        NOTE: This never proceeds to checkout without explicit user confirmation.
        """
        logger.info("[ExampleSupermarket] add_to_basket called for %s (mock)", product_url)
        return True

"""Tests for Playwright supermarket base and example scraper."""

from __future__ import annotations

import pytest

from rogi.playwright.supermarkets.example_supermarket import ExampleSupermarket


class TestExampleSupermarket:
    @pytest.mark.asyncio
    async def test_search_returns_results(self) -> None:
        scraper = ExampleSupermarket()
        results = await scraper.search("milk", max_results=5)
        assert isinstance(results, list)
        assert len(results) <= 5
        for item in results:
            assert "name" in item
            assert "price" in item

    @pytest.mark.asyncio
    async def test_add_to_basket_mock(self) -> None:
        scraper = ExampleSupermarket()
        ok = await scraper.add_to_basket("https://example-supermarket.com/products/test")
        assert ok is True

    def test_name_and_url(self) -> None:
        scraper = ExampleSupermarket()
        assert scraper.name == "example"
        assert scraper.base_url.startswith("https://")

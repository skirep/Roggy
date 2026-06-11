"""Tests for ROGI agents (non-network, mock-based)."""

from __future__ import annotations

import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rogi.database.models import PantryItemModel, EmailModel
from rogi.database.repository import Repository
from rogi.agents.ollama_client import OllamaClient
from rogi.agents.conversational_agent import ConversationalAgent
from rogi.agents.shopping_agent import ShoppingAgent


@pytest.fixture
def repo() -> Repository:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    r = Repository(db_path=db_path)
    r.connect()
    yield r
    r.close()


@pytest.fixture
def mock_ollama() -> OllamaClient:
    client = MagicMock(spec=OllamaClient)
    client.chat = AsyncMock(return_value="Test reply from ROGI.")
    client.generate = AsyncMock(return_value="Generated text.")
    return client


class TestConversationalAgent:
    @pytest.mark.asyncio
    async def test_pantry_context_injected(self, repo: Repository, mock_ollama: OllamaClient) -> None:
        repo.upsert_pantry_item(PantryItemModel(name="Tomatoes", quantity=3, unit="unit"))
        agent = ConversationalAgent(repo=repo, ollama=mock_ollama)
        reply = await agent.answer("What food do I have?")
        assert reply == "Test reply from ROGI."
        # Ensure chat was called with context containing pantry data
        call_args = mock_ollama.chat.call_args
        messages = call_args[1]["messages"] if call_args[1] else call_args[0][0]
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
        assert "Tomatoes" in user_msg

    @pytest.mark.asyncio
    async def test_email_context_injected(self, repo: Repository, mock_ollama: OllamaClient) -> None:
        repo.upsert_email(EmailModel(
            message_id="<1>",
            account="gmail",
            sender="boss@work.com",
            subject="Urgent: Report needed",
            is_important=True,
            category="important",
        ))
        agent = ConversationalAgent(repo=repo, ollama=mock_ollama)
        await agent.answer("Do I have any important emails?")
        call_args = mock_ollama.chat.call_args
        messages = call_args[1]["messages"] if call_args[1] else call_args[0][0]
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
        assert "Urgent: Report needed" in user_msg


class TestShoppingAgent:
    def test_create_list_pending(self, repo: Repository) -> None:
        agent = ShoppingAgent(repo=repo)
        items = [{"name": "Milk", "quantity": 2, "unit": "L", "price": 1.5}]
        sl = agent.create_list_from_items("Test list", items)
        assert sl.status == "pending"
        assert sl.id is not None

    def test_confirm_list(self, repo: Repository) -> None:
        agent = ShoppingAgent(repo=repo)
        sl = agent.create_list_from_items("Confirm test", [])
        agent.confirm_list(sl.id)  # type: ignore[arg-type]
        fetched = repo.get_shopping_list(sl.id)  # type: ignore[arg-type]
        assert fetched is not None
        assert fetched.status == "confirmed"

    def test_register_supermarket(self, repo: Repository) -> None:
        agent = ShoppingAgent(repo=repo)
        mock_scraper = MagicMock()
        agent.register_supermarket("TestMart", mock_scraper)
        assert "testmart" in agent.available_supermarkets()

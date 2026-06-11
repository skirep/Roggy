"""Conversational agent – answers natural-language questions using DB context."""

from __future__ import annotations

import json
import logging
from datetime import date
from typing import Dict, List, Optional

from ..database.repository import Repository
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are ROGI, a helpful personal AI assistant running on a local Windows device.
You have access to:
- Pantry contents and expiry dates
- Email summaries and classifications
- Meal plans and history
- Shopping lists
- Family preferences and memory

Answer questions concisely and helpfully.
When relevant, use the provided context data.
If you don't know something, say so honestly.
"""


class ConversationalAgent:
    """Answers user questions by injecting database context into Ollama prompts."""

    def __init__(self, repo: Repository, ollama: OllamaClient) -> None:
        self._repo = repo
        self._ollama = ollama

    async def answer(self, question: str) -> str:
        """Answer a question using DB context + Ollama."""
        context = self._build_context(question)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ]
        return await self._ollama.chat(messages=messages, temperature=0.5)

    # ------------------------------------------------------------------
    # Context builders
    # ------------------------------------------------------------------

    def _build_context(self, question: str) -> str:
        """Select relevant context snippets based on question keywords."""
        q_lower = question.lower()
        parts: List[str] = []

        # Pantry context
        if any(kw in q_lower for kw in ["food", "pantry", "have", "eat", "expire", "dinner", "meal", "cook"]):
            parts.append(self._pantry_context())

        # Email context
        if any(kw in q_lower for kw in ["email", "mail", "invoice", "appointment", "message"]):
            parts.append(self._email_context())

        # Shopping context
        if any(kw in q_lower for kw in ["buy", "shop", "purchase", "list", "supermarket"]):
            parts.append(self._shopping_context())

        # Memory context
        if any(kw in q_lower for kw in ["family", "prefer", "like", "dislike", "habit"]):
            parts.append(self._memory_context())

        if not parts:
            # General fallback: add pantry + email summary
            parts = [self._pantry_context(), self._email_context()]

        return "\n\n".join(parts)

    def _pantry_context(self) -> str:
        items = self._repo.get_pantry()
        if not items:
            return "[Pantry: empty]"
        expiring = self._repo.get_expiring_pantry(days=7)
        lines = [f"- {i.name}: {i.quantity} {i.unit}" + (f" (expires {i.expiry_date})" if i.expiry_date else "") for i in items[:30]]
        ctx = "PANTRY:\n" + "\n".join(lines)
        if expiring:
            exp_names = ", ".join(i.name for i in expiring)
            ctx += f"\nExpiring within 7 days: {exp_names}"
        return ctx

    def _email_context(self) -> str:
        emails = self._repo.get_emails(limit=10)
        if not emails:
            return "[Emails: none stored]"
        lines = [f"- [{e.category}] {e.sender}: {e.subject}" for e in emails]
        return "RECENT EMAILS:\n" + "\n".join(lines)

    def _shopping_context(self) -> str:
        lists = self._repo.list_shopping_lists(status="pending")
        if not lists:
            return "[Shopping: no pending lists]"
        sl = lists[0]
        items = sl.items[:20]
        lines = [f"- {it.get('name', '?')}: {it.get('quantity', '?')} {it.get('unit', '')}" for it in items]
        return f"PENDING SHOPPING LIST ({sl.name}):\n" + "\n".join(lines)

    def _memory_context(self) -> str:
        family = self._repo.get_family()
        prefs = self._repo.get_food_preferences()
        parts: List[str] = []
        if family:
            parts.append("FAMILY: " + ", ".join(f"{m.name} ({m.role})" for m in family))
        if prefs:
            pref_lines = [f"- {p.preference_type}: {p.item}" + (f" ({p.member})" if p.member else "") for p in prefs[:20]]
            parts.append("FOOD PREFERENCES:\n" + "\n".join(pref_lines))
        return "\n".join(parts) if parts else "[Memory: no data]"

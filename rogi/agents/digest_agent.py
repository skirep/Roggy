"""Daily digest agent – generates and delivers the morning summary."""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import List

from ..database.models import DigestModel
from ..database.repository import Repository
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class DigestAgent:
    """Assembles the morning digest from all data sources."""

    def __init__(self, repo: Repository, ollama: OllamaClient) -> None:
        self._repo = repo
        self._ollama = ollama

    async def generate(self, target_date: date | None = None) -> str:
        """Generate a full morning digest for *target_date* (defaults to today)."""
        if target_date is None:
            target_date = date.today()

        sections: List[str] = [
            f"# 🌅 ROGI Morning Digest — {target_date.strftime('%A, %d %B %Y')}",
            "",
        ]

        sections.append(await self._email_section())
        sections.append(self._pantry_section())
        sections.append(self._shopping_section())
        sections.append(await self._meal_suggestion_section())

        content = "\n".join(sections)

        digest = DigestModel(
            digest_date=target_date,
            content=content,
            sent_telegram=False,
        )
        self._repo.save_digest(digest)
        return content

    # ------------------------------------------------------------------
    # Private section builders
    # ------------------------------------------------------------------

    async def _email_section(self) -> str:
        emails = self._repo.get_emails(limit=20)
        if not emails:
            return "## 📧 Emails\nNo emails on record.\n"

        important = [e for e in emails if e.is_important]
        invoices = [e for e in emails if e.is_invoice]
        appointments = [e for e in emails if e.is_appointment]

        lines = ["## 📧 Emails"]
        if important:
            lines.append(f"🔴 **Important ({len(important)}):**")
            for e in important[:5]:
                lines.append(f"  - {e.sender}: {e.subject}")
        if invoices:
            lines.append(f"🧾 **Invoices ({len(invoices)}):**")
            for e in invoices[:5]:
                lines.append(f"  - {e.sender}: {e.subject}")
        if appointments:
            lines.append(f"📅 **Appointments ({len(appointments)}):**")
            for e in appointments[:5]:
                lines.append(f"  - {e.sender}: {e.subject}")
        if not (important or invoices or appointments):
            lines.append(f"  {len(emails)} emails — nothing urgent.")

        try:
            ai_summary = await self._ollama.generate(
                prompt=(
                    "In 2 sentences, summarise these recent emails:\n"
                    + "\n".join(f"- {e.subject}" for e in emails[:15])
                ),
                temperature=0.3,
            )
            lines.append(f"\n*AI Summary:* {ai_summary}")
        except Exception as exc:
            logger.warning("AI email summary failed: %s", exc)

        return "\n".join(lines) + "\n"

    def _pantry_section(self) -> str:
        expiring = self._repo.get_expiring_pantry(days=7)
        all_items = self._repo.get_pantry()
        lines = ["## 🥫 Pantry"]
        lines.append(f"Total items: {len(all_items)}")
        if expiring:
            lines.append(f"⚠️ **Expiring within 7 days:**")
            for item in expiring:
                lines.append(f"  - {item.name}: {item.quantity} {item.unit} (expires {item.expiry_date})")
        else:
            lines.append("✅ No items expiring soon.")
        return "\n".join(lines) + "\n"

    def _shopping_section(self) -> str:
        lists = self._repo.list_shopping_lists(status="pending")
        if not lists:
            return "## 🛒 Shopping\nNo pending shopping lists.\n"
        lines = ["## 🛒 Shopping"]
        for sl in lists[:3]:
            lines.append(f"📋 **{sl.name}** ({len(sl.items)} items, ~€{sl.total_cost:.2f})")
        return "\n".join(lines) + "\n"

    async def _meal_suggestion_section(self) -> str:
        items = self._repo.get_pantry()
        if not items:
            return "## 🍽️ Meal Suggestions\nPantry is empty — please add items.\n"

        ingredient_list = ", ".join(i.name for i in items[:20])
        try:
            suggestion = await self._ollama.generate(
                prompt=(
                    f"I have these ingredients: {ingredient_list}.\n"
                    "Suggest 3 simple meals for today (breakfast, lunch, dinner) in bullet points."
                ),
                temperature=0.6,
            )
        except Exception as exc:
            logger.warning("Meal suggestion failed: %s", exc)
            suggestion = "Unable to generate suggestions (Ollama unavailable)."

        return f"## 🍽️ Meal Suggestions\n{suggestion}\n"

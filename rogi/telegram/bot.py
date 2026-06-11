"""Telegram bot for ROGI – handles messages and delivers the daily digest."""

from __future__ import annotations

import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class RogiBot:
    """
    Minimal Telegram Bot API wrapper.

    Uses the Bot API directly via httpx without polling — suited for
    notification-only and webhook usage patterns.

    For interactive two-way conversation, integrate python-telegram-bot
    or aiogram and register the handlers from rogi/telegram/handlers.py.
    """

    def __init__(self, token: str, chat_id: str) -> None:
        self._token = token
        self._chat_id = chat_id
        self._api_base = f"https://api.telegram.org/bot{token}"

    # ------------------------------------------------------------------
    # Core send
    # ------------------------------------------------------------------

    async def send_message(
        self,
        text: str,
        chat_id: Optional[str] = None,
        parse_mode: str = "Markdown",
        disable_notification: bool = False,
    ) -> bool:
        """Send *text* to *chat_id* (defaults to the configured chat)."""
        target = chat_id or self._chat_id
        payload = {
            "chat_id": target,
            "text": text,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification,
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(f"{self._api_base}/sendMessage", json=payload)
                resp.raise_for_status()
                logger.info("Telegram message sent to %s", target)
                return True
        except Exception as exc:
            logger.error("Telegram send failed: %s", exc)
            return False

    async def send_digest(self, digest_text: str) -> bool:
        """Split and send a long digest in chunks (Telegram limit: 4096 chars)."""
        MAX_LEN = 4000
        chunks = [digest_text[i : i + MAX_LEN] for i in range(0, len(digest_text), MAX_LEN)]
        success = True
        for chunk in chunks:
            ok = await self.send_message(chunk)
            if not ok:
                success = False
        return success

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    async def is_healthy(self) -> bool:
        """Verify the bot token is valid by calling getMe."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self._api_base}/getMe")
                data = resp.json()
                return data.get("ok", False)
        except Exception:
            return False

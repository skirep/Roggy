"""
Telegram message handlers for ROGI interactive mode.

These handlers are designed to be wired into python-telegram-bot or aiogram.
The functions receive a message text and return a reply string, keeping them
easily testable without a live Telegram connection.
"""

from __future__ import annotations

import logging
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)

# Type alias for the answer function (accepts a question, returns a reply)
AnswerFn = Callable[[str], Awaitable[str]]


async def handle_message(text: str, answer_fn: AnswerFn) -> str:
    """
    Route an incoming Telegram message to the appropriate handler.

    Parameters
    ----------
    text:
        Raw message text from the user.
    answer_fn:
        Async callable (e.g. ConversationalAgent.answer) that takes a
        question string and returns the assistant reply.
    """
    text = text.strip()
    if not text:
        return "Please send a message."

    # Command routing
    if text.startswith("/start"):
        return (
            "👋 *Hello! I'm ROGI — your ROG Intelligent Assistant.*\n\n"
            "I can help you with:\n"
            "• 🥫 Pantry — *What food do I have?*\n"
            "• 📧 Emails — *Any important emails?*\n"
            "• 🍽️ Meals — *What should I cook today?*\n"
            "• 🛒 Shopping — *What should I buy?*\n\n"
            "Just ask me anything!"
        )

    if text.startswith("/help"):
        return (
            "📚 *ROGI Commands*\n\n"
            "/start — Introduction\n"
            "/help — This message\n"
            "/pantry — Show pantry contents\n"
            "/expiring — Show items expiring soon\n"
            "/digest — Request today's digest\n\n"
            "Or just ask me a question in plain language!"
        )

    # Delegate everything else to the conversational agent
    try:
        return await answer_fn(text)
    except Exception as exc:
        logger.error("Handler error: %s", exc)
        return "Sorry, something went wrong. Please try again."

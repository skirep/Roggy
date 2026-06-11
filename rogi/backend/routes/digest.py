"""Daily digest API routes."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends

from ..main import get_app_state, AppState

router = APIRouter()


def _state() -> AppState:
    return get_app_state()


@router.get("/today")
async def get_today_digest(state: AppState = Depends(_state)) -> dict:
    digest = state.repo.get_digest(date.today())
    if digest:
        return {"date": str(digest.digest_date), "content": digest.content}
    return {"date": str(date.today()), "content": None}


@router.post("/generate")
async def generate_digest(
    background_tasks: BackgroundTasks,
    target_date: Optional[str] = None,
    send_telegram: bool = False,
    state: AppState = Depends(_state),
) -> dict:
    """Generate (and optionally send via Telegram) the daily digest."""
    from ..config import get_settings
    from ...telegram.bot import RogiBot

    parsed_date = date.fromisoformat(target_date) if target_date else date.today()

    async def _generate() -> None:
        content = await state.digest_agent.generate(target_date=parsed_date)
        if send_telegram:
            settings = get_settings()
            if settings.telegram_bot_token and settings.telegram_chat_id:
                bot = RogiBot(
                    token=settings.telegram_bot_token,
                    chat_id=settings.telegram_chat_id,
                )
                await bot.send_digest(content)

    background_tasks.add_task(_generate)
    return {"status": "generating", "date": str(parsed_date)}

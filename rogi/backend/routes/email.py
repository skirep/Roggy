"""Email API routes."""

from __future__ import annotations

import json
import logging
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from ..main import get_app_state, AppState
from ...database.models import EmailModel

router = APIRouter()
logger = logging.getLogger(__name__)


def _state() -> AppState:
    return get_app_state()


@router.get("/", response_model=List[EmailModel])
async def list_emails(
    limit: int = 50,
    category: Optional[str] = None,
    account: Optional[str] = None,
    state: AppState = Depends(_state),
) -> List[EmailModel]:
    return state.repo.get_emails(limit=limit, category=category, account=account)


@router.get("/summary")
async def daily_summary(state: AppState = Depends(_state)) -> dict:
    summary = await state.email_agent.generate_daily_summary()
    return {"summary": summary}


@router.post("/fetch")
async def trigger_fetch(
    background_tasks: BackgroundTasks,
    state: AppState = Depends(_state),
) -> dict:
    """Trigger IMAP fetch in the background for all configured accounts."""
    from ..config import get_settings
    settings = get_settings()

    async def _fetch_all() -> None:
        accounts: list = []
        if settings.imap_accounts:
            try:
                accounts = json.loads(settings.imap_accounts)
            except json.JSONDecodeError:
                logger.error("Invalid IMAP_ACCOUNTS JSON")

        for acc in accounts:
            emails = state.email_agent.fetch_imap(
                host=acc["host"],
                port=int(acc.get("port", 993)),
                username=acc["username"],
                password=acc["password"],
                account_label=acc.get("label", acc["username"]),
                use_ssl=acc.get("ssl", True),
            )
            await state.email_agent.process_and_store(emails)

    background_tasks.add_task(_fetch_all)
    return {"status": "fetch triggered"}

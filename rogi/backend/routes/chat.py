"""Conversational chat API route."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..main import get_app_state, AppState

router = APIRouter()


def _state() -> AppState:
    return get_app_state()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/", response_model=ChatResponse)
async def chat(body: ChatRequest, state: AppState = Depends(_state)) -> ChatResponse:
    """Answer a natural-language question using ROGI's conversational agent."""
    reply = await state.conv_agent.answer(body.message)
    return ChatResponse(reply=reply)

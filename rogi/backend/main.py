"""
ROGI FastAPI application.

Run with:
    uvicorn rogi.backend.main:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..database.repository import Repository
from ..agents.ollama_client import OllamaClient
from ..agents.email_agent import EmailAgent
from ..agents.conversational_agent import ConversationalAgent
from ..agents.digest_agent import DigestAgent
from ..agents.shopping_agent import ShoppingAgent
from .config import get_settings
from .routes import pantry, meals, email, memory, shopping, digest, chat

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application state container (injected into route dependencies)
# ---------------------------------------------------------------------------


class AppState:
    def __init__(self) -> None:
        settings = get_settings()
        self.repo = Repository(db_path=settings.database_path)
        self.ollama = OllamaClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
        )
        self.email_agent = EmailAgent(repo=self.repo, ollama=self.ollama)
        self.conv_agent = ConversationalAgent(repo=self.repo, ollama=self.ollama)
        self.digest_agent = DigestAgent(repo=self.repo, ollama=self.ollama)
        self.shopping_agent = ShoppingAgent(repo=self.repo)


_state: AppState | None = None


def get_app_state() -> AppState:
    if _state is None:
        raise RuntimeError("Application not initialised.")
    return _state


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global _state
    _state = AppState()
    _state.repo.connect()
    logger.info("ROGI backend started.")
    yield
    _state.repo.close()
    logger.info("ROGI backend stopped.")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ROGI – ROG Intelligent Assistant",
        description="Local-first AI assistant backend API",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(pantry.router, prefix="/api/pantry", tags=["pantry"])
    app.include_router(meals.router, prefix="/api/meals", tags=["meals"])
    app.include_router(email.router, prefix="/api/email", tags=["email"])
    app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
    app.include_router(shopping.router, prefix="/api/shopping", tags=["shopping"])
    app.include_router(digest.router, prefix="/api/digest", tags=["digest"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "model": settings.ollama_model}

    return app


app = create_app()

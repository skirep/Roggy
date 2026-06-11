"""Shopping API routes."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..main import get_app_state, AppState
from ...database.models import ShoppingListModel

router = APIRouter()


def _state() -> AppState:
    return get_app_state()


class SearchQuery(BaseModel):
    query: str
    supermarket: Optional[str] = None
    max_results: int = 10


class CreateListRequest(BaseModel):
    name: str
    items: List[Dict[str, Any]]


@router.get("/supermarkets")
async def list_supermarkets(state: AppState = Depends(_state)) -> dict:
    return {"supermarkets": state.shopping_agent.available_supermarkets()}


@router.post("/search")
async def search_products(
    body: SearchQuery,
    state: AppState = Depends(_state),
) -> dict:
    results = await state.shopping_agent.search(
        query=body.query,
        supermarket=body.supermarket,
        max_results=body.max_results,
    )
    return {"results": results}


@router.post("/compare")
async def compare_products(query: str, state: AppState = Depends(_state)) -> dict:
    results = await state.shopping_agent.compare(query)
    return {"results": results}


@router.get("/lists", response_model=List[ShoppingListModel])
async def list_shopping_lists(
    status: Optional[str] = None,
    state: AppState = Depends(_state),
) -> List[ShoppingListModel]:
    return state.repo.list_shopping_lists(status=status)


@router.post("/lists", response_model=ShoppingListModel)
async def create_shopping_list(
    body: CreateListRequest,
    state: AppState = Depends(_state),
) -> ShoppingListModel:
    return state.shopping_agent.create_list_from_items(name=body.name, items=body.items)


@router.post("/lists/{list_id}/confirm")
async def confirm_list(list_id: int, state: AppState = Depends(_state)) -> dict:
    sl = state.repo.get_shopping_list(list_id)
    if sl is None:
        raise HTTPException(status_code=404, detail="List not found.")
    state.shopping_agent.confirm_list(list_id)
    return {"confirmed": list_id}

"""Pantry API routes."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..main import get_app_state, AppState
from ...database.models import PantryItemModel

router = APIRouter()


def _state() -> AppState:
    return get_app_state()


class PantryItemIn(BaseModel):
    name: str
    quantity: float
    unit: str = "unit"
    category: Optional[str] = None
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None


@router.get("/", response_model=List[PantryItemModel])
async def list_pantry(state: AppState = Depends(_state)) -> List[PantryItemModel]:
    return state.repo.get_pantry()


@router.get("/expiring", response_model=List[PantryItemModel])
async def expiring_pantry(
    days: int = 7,
    state: AppState = Depends(_state),
) -> List[PantryItemModel]:
    return state.repo.get_expiring_pantry(days=days)


@router.get("/{name}", response_model=PantryItemModel)
async def get_item(name: str, state: AppState = Depends(_state)) -> PantryItemModel:
    item = state.repo.get_pantry_item(name)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item '{name}' not found.")
    return item


@router.put("/{name}", response_model=PantryItemModel)
async def upsert_item(
    name: str,
    body: PantryItemIn,
    state: AppState = Depends(_state),
) -> PantryItemModel:
    item = PantryItemModel(name=name, **body.model_dump())
    state.repo.upsert_pantry_item(item)
    return state.repo.get_pantry_item(name)  # type: ignore[return-value]


@router.delete("/{name}")
async def delete_item(name: str, state: AppState = Depends(_state)) -> dict:
    state.repo.delete_pantry_item(name)
    return {"deleted": name}

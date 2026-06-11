"""Memory API routes (food preferences, family, favorite products, shopping habits)."""

from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Depends

from ..main import get_app_state, AppState
from ...database.models import (
    FamilyMemberModel,
    FavoriteProductModel,
    FoodPreferenceModel,
    ShoppingHabitModel,
)

router = APIRouter()


def _state() -> AppState:
    return get_app_state()


# ---------- Food preferences ----------

@router.get("/preferences", response_model=List[FoodPreferenceModel])
async def list_preferences(state: AppState = Depends(_state)) -> List[FoodPreferenceModel]:
    return state.repo.get_food_preferences()


@router.post("/preferences", response_model=FoodPreferenceModel)
async def add_preference(
    body: FoodPreferenceModel,
    state: AppState = Depends(_state),
) -> FoodPreferenceModel:
    state.repo.add_food_preference(body)
    return body


# ---------- Family members ----------

@router.get("/family", response_model=List[FamilyMemberModel])
async def list_family(state: AppState = Depends(_state)) -> List[FamilyMemberModel]:
    return state.repo.get_family()


@router.put("/family/{name}", response_model=FamilyMemberModel)
async def upsert_family(
    name: str,
    body: FamilyMemberModel,
    state: AppState = Depends(_state),
) -> FamilyMemberModel:
    body.name = name
    state.repo.upsert_family_member(body)
    return body


# ---------- Favorite products ----------

@router.get("/products", response_model=List[FavoriteProductModel])
async def list_favorites(state: AppState = Depends(_state)) -> List[FavoriteProductModel]:
    return state.repo.get_favorite_products()


@router.post("/products", response_model=FavoriteProductModel)
async def add_favorite(
    body: FavoriteProductModel,
    state: AppState = Depends(_state),
) -> FavoriteProductModel:
    state.repo.add_favorite_product(body)
    return body


# ---------- Shopping habits ----------

@router.get("/habits", response_model=Dict[str, str])
async def list_habits(state: AppState = Depends(_state)) -> Dict[str, str]:
    return state.repo.get_all_shopping_habits()


@router.put("/habits/{key}")
async def set_habit(
    key: str,
    value: str,
    state: AppState = Depends(_state),
) -> dict:
    state.repo.set_shopping_habit(key, value)
    return {"key": key, "value": value}

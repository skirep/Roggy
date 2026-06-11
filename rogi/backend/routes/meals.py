"""Meal plan API routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..main import get_app_state, AppState
from ...database.models import MealHistoryModel, MealPlanModel

router = APIRouter()


def _state() -> AppState:
    return get_app_state()


@router.get("/latest", response_model=Optional[MealPlanModel])
async def get_latest_plan(state: AppState = Depends(_state)) -> Optional[MealPlanModel]:
    return state.repo.get_latest_meal_plan()


class MealHistoryIn(BaseModel):
    meal_date: str
    meal_type: str
    recipe_name: str
    people: int = 2
    user_rating: Optional[int] = None
    family_feedback: Optional[str] = None


@router.post("/history")
async def add_meal_history(
    body: MealHistoryIn,
    state: AppState = Depends(_state),
) -> dict:
    from datetime import date
    entry = MealHistoryModel(
        meal_date=date.fromisoformat(body.meal_date),
        meal_type=body.meal_type,
        recipe_name=body.recipe_name,
        people=body.people,
        user_rating=body.user_rating,
        family_feedback=body.family_feedback,
    )
    state.repo.save_meal_history(entry)
    return {"saved": True}

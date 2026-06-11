"""Pydantic data models for ROGI database entities."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PantryItemModel(BaseModel):
    id: Optional[int] = None
    name: str
    quantity: float
    unit: str = "unit"
    category: Optional[str] = None
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EmailModel(BaseModel):
    id: Optional[int] = None
    message_id: Optional[str] = None
    account: str
    sender: Optional[str] = None
    subject: Optional[str] = None
    body_snippet: Optional[str] = None
    received_at: Optional[datetime] = None
    category: Optional[str] = None
    is_invoice: bool = False
    is_appointment: bool = False
    is_important: bool = False
    summary: Optional[str] = None
    processed_at: Optional[datetime] = None


class MealPlanModel(BaseModel):
    id: Optional[int] = None
    week_start: date
    people: int = 2
    plan_json: str
    created_at: Optional[datetime] = None


class MealHistoryModel(BaseModel):
    id: Optional[int] = None
    meal_date: date
    meal_type: str
    recipe_name: str
    people: int = 2
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    family_feedback: Optional[str] = None
    created_at: Optional[datetime] = None


class ShoppingListModel(BaseModel):
    id: Optional[int] = None
    name: str
    items: List[Dict[str, Any]] = Field(default_factory=list)
    total_cost: float = 0.0
    status: str = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FoodPreferenceModel(BaseModel):
    id: Optional[int] = None
    preference_type: str  # like | dislike | allergy | restriction
    item: str
    member: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


class FamilyMemberModel(BaseModel):
    id: Optional[int] = None
    name: str
    role: str = "adult"  # adult | child | pet
    age: Optional[int] = None
    dietary_notes: Optional[str] = None
    created_at: Optional[datetime] = None


class FavoriteProductModel(BaseModel):
    id: Optional[int] = None
    product_name: str
    brand: Optional[str] = None
    supermarket: Optional[str] = None
    notes: Optional[str] = None
    last_seen_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class ShoppingHabitModel(BaseModel):
    id: Optional[int] = None
    habit_key: str
    habit_value: str
    updated_at: Optional[datetime] = None


class DigestModel(BaseModel):
    id: Optional[int] = None
    digest_date: date
    content: str
    sent_telegram: bool = False
    created_at: Optional[datetime] = None

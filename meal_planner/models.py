"""Data models for the Weekly Meal Planner."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Set


@dataclass
class Recipe:
    """Represents a single recipe."""

    name: str
    meal_type: str  # breakfast | lunch | snack | dinner
    ingredients: Dict[str, float]  # {ingredient: quantity_per_person}
    ingredient_units: Dict[str, str]  # {ingredient: unit}
    cost_per_person: float  # estimated cost in currency units
    prep_time_minutes: int
    tags: Set[str] = field(default_factory=set)
    # e.g. {"healthy", "high-protein", "vegetarian", "vegan", "low-cost", "kids-friendly"}
    servings_base: int = 1  # recipe designed for this many people
    calories_per_person: int = 0
    protein_per_person: float = 0.0  # grams

    def scale(self, people: int) -> "Recipe":
        """Return a new Recipe scaled to the given number of people."""
        factor = people / self.servings_base
        scaled = Recipe(
            name=self.name,
            meal_type=self.meal_type,
            ingredients={k: v * factor for k, v in self.ingredients.items()},
            ingredient_units=dict(self.ingredient_units),
            cost_per_person=self.cost_per_person,
            prep_time_minutes=self.prep_time_minutes,
            tags=set(self.tags),
            servings_base=people,
            calories_per_person=self.calories_per_person,
            protein_per_person=self.protein_per_person,
        )
        return scaled

    def total_cost(self, people: int) -> float:
        return self.cost_per_person * people

    def ingredient_names(self) -> Set[str]:
        return set(self.ingredients.keys())


@dataclass
class PantryItem:
    """Represents an item currently in the pantry."""

    name: str
    quantity: float
    unit: str
    expiry_date: Optional[date] = None

    def is_expired(self, ref_date: Optional[date] = None) -> bool:
        if self.expiry_date is None:
            return False
        ref = ref_date or date.today()
        return self.expiry_date < ref


@dataclass
class UserPreferences:
    """Encapsulates user dietary preferences and constraints."""

    people: int = 2
    dietary_restrictions: Set[str] = field(default_factory=set)
    # e.g. {"vegetarian", "vegan", "gluten-free", "dairy-free"}
    excluded_ingredients: Set[str] = field(default_factory=set)
    max_prep_time_minutes: Optional[int] = None
    weekly_budget: Optional[float] = None
    preferred_tags: Set[str] = field(default_factory=set)
    # tags to favour: {"healthy", "high-protein", "low-cost"}
    children_count: int = 0
    adults_count: int = 2

    def total_people(self) -> int:
        return self.adults_count + self.children_count


@dataclass
class MealSlot:
    """A single meal slot within a day."""

    meal_type: str  # breakfast | lunch | snack | dinner
    recipe: Recipe
    pantry_items_used: Dict[str, float] = field(default_factory=dict)
    # {ingredient: quantity_covered_by_pantry}
    items_to_buy: Dict[str, float] = field(default_factory=dict)
    # {ingredient: quantity_to_purchase}

    def ingredient_units(self) -> Dict[str, str]:
        return self.recipe.ingredient_units


@dataclass
class DayPlan:
    """Meal plan for a single day."""

    day_index: int  # 0=Monday … 6=Sunday
    date: date
    breakfast: Optional[MealSlot] = None
    lunch: Optional[MealSlot] = None
    snack: Optional[MealSlot] = None
    dinner: Optional[MealSlot] = None

    def meals(self) -> Dict[str, Optional[MealSlot]]:
        return {
            "breakfast": self.breakfast,
            "lunch": self.lunch,
            "snack": self.snack,
            "dinner": self.dinner,
        }

    def all_recipes(self) -> List[Recipe]:
        slots = [self.breakfast, self.lunch, self.snack, self.dinner]
        return [s.recipe for s in slots if s is not None]

    def day_name(self) -> str:
        names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return names[self.day_index % 7]


@dataclass
class ShoppingItem:
    """An item on the shopping list."""

    name: str
    quantity: float
    unit: str
    estimated_cost: float = 0.0


@dataclass
class ShoppingList:
    """A consolidated shopping list for the week."""

    items: List[ShoppingItem] = field(default_factory=list)
    total_cost: float = 0.0

    def add(self, name: str, quantity: float, unit: str, cost_per_unit: float = 0.0) -> None:
        for item in self.items:
            if item.name == name and item.unit == unit:
                extra_cost = quantity * cost_per_unit
                item.quantity += quantity
                item.estimated_cost += extra_cost
                self.total_cost += extra_cost
                return
        cost = quantity * cost_per_unit
        self.items.append(ShoppingItem(name=name, quantity=quantity, unit=unit, estimated_cost=cost))
        self.total_cost += cost

    def sorted_items(self) -> List[ShoppingItem]:
        return sorted(self.items, key=lambda i: i.name)


@dataclass
class MealPlan:
    """A complete weekly meal plan."""

    week_start: date
    days: List[DayPlan]
    people: int
    shopping_list: ShoppingList = field(default_factory=ShoppingList)
    total_estimated_cost: float = 0.0

    def day_by_index(self, index: int) -> Optional[DayPlan]:
        for d in self.days:
            if d.day_index == index:
                return d
        return None


@dataclass
class MealHistory:
    """A recorded meal history entry stored in SQLite."""

    id: Optional[int]
    meal_date: date
    meal_type: str
    recipe_name: str
    people: int
    user_rating: Optional[int] = None  # 1-5
    family_feedback: Optional[str] = None
    created_at: Optional[str] = None

"""Core meal planning algorithm for the Weekly Meal Planner."""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Dict, List, Optional, Set

from .database import Database
from .models import (
    DayPlan,
    MealPlan,
    MealSlot,
    Recipe,
    ShoppingList,
    UserPreferences,
)
from .pantry import PantryManager
from .recipes import RECIPES, get_recipes_by_type

# ---------------------------------------------------------------------------
# Ingredient price estimates (per unit/kg/L) used for shopping cost calculation
# ---------------------------------------------------------------------------
INGREDIENT_PRICE: Dict[str, float] = {
    # produce
    "banana": 0.20,
    "apple": 0.30,
    "berries": 4.00,
    "avocado": 1.00,
    "lemon": 0.30,
    "lime": 0.30,
    "tomato": 1.50,
    "cherry_tomatoes": 2.00,
    "lettuce": 1.20,
    "spinach": 2.00,
    "carrot": 0.80,
    "celery": 1.00,
    "onion": 0.60,
    "garlic": 0.50,
    "potato": 0.70,
    "zucchini": 1.20,
    "bell_pepper": 1.00,
    "broccoli": 1.50,
    "mushrooms": 3.00,
    "cucumber": 0.80,
    "basil": 1.50,
    "cilantro": 0.80,
    "dill": 1.00,
    "ginger": 2.00,
    # dairy & eggs
    "eggs": 0.25,  # per unit
    "milk": 1.00,  # per L
    "butter": 8.00,  # per kg
    "cheese": 10.00,  # per kg
    "parmesan": 15.00,  # per kg
    "mozzarella": 8.00,  # per kg
    "greek_yogurt": 4.00,  # per kg
    "sour_cream": 3.00,  # per kg
    # grains & bakery
    "bread": 0.15,  # per slice
    "flour": 1.00,  # per kg
    "pasta": 1.50,  # per kg
    "noodles": 1.80,  # per kg
    "rice": 1.20,  # per kg
    "arborio_rice": 2.00,  # per kg
    "oats": 1.50,  # per kg
    "granola": 4.00,  # per kg
    "crackers": 3.00,  # per kg
    "croutons": 2.50,  # per kg
    "breadcrumbs": 1.50,  # per kg
    "tortilla": 0.30,  # per unit
    "baking_powder": 2.00,  # per kg
    # proteins
    "chicken_breast": 8.00,  # per kg
    "ground_beef": 7.00,  # per kg
    "ground_turkey": 7.50,  # per kg
    "salmon": 15.00,  # per kg
    "white_fish": 10.00,  # per kg
    "shrimp": 14.00,  # per kg
    "tuna": 5.00,  # per kg (canned)
    "tofu": 3.50,  # per kg
    # legumes
    "chickpeas": 1.50,  # per kg (canned)
    "red_lentils": 2.00,  # per kg
    "black_beans": 1.20,  # per kg (canned)
    "kidney_beans": 1.20,  # per kg (canned)
    # pantry staples
    "olive_oil": 6.00,  # per L
    "sesame_oil": 5.00,  # per L
    "soy_sauce": 2.00,  # per L
    "white_wine": 5.00,  # per L
    "vegetable_broth": 1.50,  # per L
    "tomato_sauce": 2.00,  # per kg
    "coconut_milk": 2.00,  # per L
    "mayonnaise": 3.00,  # per kg
    "caesar_dressing": 4.00,  # per L
    "peanut_butter": 4.00,  # per kg
    "hummus": 5.00,  # per kg
    "honey": 6.00,  # per kg
    "sugar": 1.00,  # per kg
    "salt": 0.50,  # per kg
    "curry_powder": 5.00,  # per kg
    "cumin": 5.00,  # per kg
    "taco_seasoning": 8.00,  # per kg
    "sesame_seeds": 6.00,  # per kg
    # nuts & seeds
    "mixed_nuts": 12.00,  # per kg
}

MEAL_TYPES = ["breakfast", "lunch", "snack", "dinner"]


class MealPlanner:
    """Generates weekly meal plans respecting pantry, preferences, and history."""

    def __init__(self, db: Database, pantry: PantryManager) -> None:
        self._db = db
        self._pantry = pantry

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_week(
        self,
        preferences: UserPreferences,
        week_start: Optional[date] = None,
        mode: str = "default",
    ) -> MealPlan:
        """
        Generate a complete 7-day meal plan.

        Parameters
        ----------
        preferences:
            User preferences (people, restrictions, budget, etc.).
        week_start:
            Monday of the target week.  Defaults to next Monday if not given.
        mode:
            Planning mode: "default" | "low-cost" | "healthy" |
            "high-protein" | "pantry-only".
        """
        if week_start is None:
            today = date.today()
            days_until_monday = (7 - today.weekday()) % 7 or 7
            week_start = today + timedelta(days=days_until_monday)

        recent_recipes = set(self._db.get_recent_recipes(days=14))
        pantry_dict = self._pantry.as_dict()

        days: List[DayPlan] = []
        # Track ingredients already scheduled this week for reuse bonus
        week_ingredients: Set[str] = set()

        for day_idx in range(7):
            day_date = week_start + timedelta(days=day_idx)
            slots: Dict[str, Optional[MealSlot]] = {}

            for meal_type in MEAL_TYPES:
                recipe = self._pick_recipe(
                    meal_type=meal_type,
                    preferences=preferences,
                    recent_recipes=recent_recipes,
                    week_ingredients=week_ingredients,
                    pantry_dict=pantry_dict,
                    mode=mode,
                )
                if recipe is None:
                    slots[meal_type] = None
                    continue

                # Scale to the actual number of people
                scaled = recipe.scale(preferences.total_people())

                # Compute pantry coverage and what needs to be bought
                pantry_used: Dict[str, float] = {}
                to_buy: Dict[str, float] = {}
                for ing, qty in scaled.ingredients.items():
                    unit = scaled.ingredient_units.get(ing, "unit")
                    covered = self._pantry.coverage(ing, qty, unit)
                    if covered > 0:
                        pantry_used[ing] = covered
                    remaining = qty - covered
                    if remaining > 0:
                        to_buy[ing] = remaining

                slots[meal_type] = MealSlot(
                    meal_type=meal_type,
                    recipe=scaled,
                    pantry_items_used=pantry_used,
                    items_to_buy=to_buy,
                )
                recent_recipes.add(recipe.name)
                week_ingredients.update(recipe.ingredient_names())

            day_plan = DayPlan(
                day_index=day_idx,
                date=day_date,
                breakfast=slots.get("breakfast"),
                lunch=slots.get("lunch"),
                snack=slots.get("snack"),
                dinner=slots.get("dinner"),
            )
            days.append(day_plan)

        shopping = self._build_shopping_list(days, preferences.total_people())
        total_cost = shopping.total_cost

        return MealPlan(
            week_start=week_start,
            days=days,
            people=preferences.total_people(),
            shopping_list=shopping,
            total_estimated_cost=total_cost,
        )

    def save_plan_to_history(self, plan: MealPlan) -> None:
        """Persist a meal plan's meals to history so future plans avoid repeats."""
        for day in plan.days:
            for meal_type, slot in day.meals().items():
                if slot is not None:
                    self._db.record_meal(
                        meal_date=day.date,
                        meal_type=meal_type,
                        recipe_name=slot.recipe.name,
                        people=plan.people,
                    )

    # ------------------------------------------------------------------
    # Recipe selection
    # ------------------------------------------------------------------

    def _pick_recipe(
        self,
        meal_type: str,
        preferences: UserPreferences,
        recent_recipes: Set[str],
        week_ingredients: Set[str],
        pantry_dict: Dict,
        mode: str,
    ) -> Optional[Recipe]:
        """Score and select the best recipe for a given meal slot."""
        candidates = get_recipes_by_type(meal_type)

        # Apply hard filters
        candidates = self._apply_hard_filters(candidates, preferences, mode)

        if not candidates:
            # Relax mode filter but keep hard dietary/exclusion filters
            candidates = get_recipes_by_type(meal_type)
            candidates = self._apply_hard_filters(candidates, preferences, mode=None)

        if not candidates:
            return None

        # Score and sort
        scored = [
            (self._score(r, recent_recipes, week_ingredients, pantry_dict, preferences, mode), r)
            for r in candidates
        ]
        scored.sort(key=lambda x: x[0], reverse=True)

        # Add some randomness: pick from the top-3 to avoid determinism
        top_n = scored[: min(3, len(scored))]
        _, chosen = random.choice(top_n)
        return chosen

    def _apply_hard_filters(
        self,
        candidates: List[Recipe],
        preferences: UserPreferences,
        mode: Optional[str],
    ) -> List[Recipe]:
        """Remove recipes that violate hard constraints."""
        result: List[Recipe] = []
        for r in candidates:
            # Dietary restrictions: recipe must have all required tags
            if preferences.dietary_restrictions:
                if not preferences.dietary_restrictions.issubset(r.tags):
                    continue

            # Excluded ingredients
            if preferences.excluded_ingredients:
                if r.ingredient_names() & {i.lower() for i in preferences.excluded_ingredients}:
                    continue

            # Cooking time
            if preferences.max_prep_time_minutes is not None:
                if r.prep_time_minutes > preferences.max_prep_time_minutes:
                    continue

            # Budget – rough per-person cost check
            if preferences.weekly_budget is not None:
                # 21 meals per week, very rough per-meal budget
                per_meal_budget = preferences.weekly_budget / (7 * len(MEAL_TYPES))
                if r.cost_per_person * preferences.total_people() > per_meal_budget * 1.5:
                    continue

            # Mode filters
            if mode == "pantry-only":
                # Recipe must be entirely coverable from pantry
                if not self._fully_in_pantry(r, preferences.total_people()):
                    continue

            result.append(r)
        return result

    def _fully_in_pantry(self, recipe: Recipe, people: int) -> bool:
        scaled = recipe.scale(people)
        for ing, qty in scaled.ingredients.items():
            unit = scaled.ingredient_units.get(ing, "unit")
            if self._pantry.coverage(ing, qty, unit) < qty:
                return False
        return True

    def _score(
        self,
        recipe: Recipe,
        recent_recipes: Set[str],
        week_ingredients: Set[str],
        pantry_dict: Dict,
        preferences: UserPreferences,
        mode: Optional[str],
    ) -> float:
        """Return a numeric score – higher is better."""
        score = 0.0

        # Penalize recently used recipes
        if recipe.name in recent_recipes:
            score -= 20.0

        # Bonus for ingredient overlap with what's already scheduled this week
        overlap = recipe.ingredient_names() & week_ingredients
        score += len(overlap) * 3.0

        # Bonus for pantry ingredients already available
        for ing in recipe.ingredient_names():
            if ing.lower() in pantry_dict:
                score += 2.0

        # Mode bonuses
        if mode == "healthy" and "healthy" in recipe.tags:
            score += 10.0
        if mode == "high-protein" and "high-protein" in recipe.tags:
            score += 10.0
        if mode == "low-cost" and "low-cost" in recipe.tags:
            score += 10.0
        if mode == "low-cost":
            score -= recipe.cost_per_person  # penalise expensive recipes

        # Kids-friendly bonus when children are present
        if preferences.children_count > 0 and "kids-friendly" in recipe.tags:
            score += 5.0

        # Preferred tags bonus
        for tag in preferences.preferred_tags:
            if tag in recipe.tags:
                score += 5.0

        # Slight random noise for variety
        score += random.uniform(0, 1)

        return score

    # ------------------------------------------------------------------
    # Shopping list builder
    # ------------------------------------------------------------------

    def _build_shopping_list(self, days: List[DayPlan], people: int) -> ShoppingList:
        """Consolidate all items-to-buy across the week."""
        shopping = ShoppingList()
        for day in days:
            for slot in day.meals().values():
                if slot is None:
                    continue
                for ing, qty in slot.items_to_buy.items():
                    unit = slot.ingredient_units().get(ing, "unit")
                    price_per_unit = INGREDIENT_PRICE.get(ing, 1.0)
                    shopping.add(ing, qty, unit, price_per_unit)
        return shopping

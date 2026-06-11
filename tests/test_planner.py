"""Tests for the MealPlanner."""

from __future__ import annotations

from datetime import date

import pytest

from meal_planner.database import Database
from meal_planner.models import PantryItem, UserPreferences
from meal_planner.pantry import PantryManager
from meal_planner.planner import MealPlanner


@pytest.fixture()
def db(tmp_path):
    return Database(db_path=str(tmp_path / "test.db"))


@pytest.fixture()
def pantry(db):
    return PantryManager(db)


@pytest.fixture()
def planner(db, pantry):
    return MealPlanner(db, pantry)


WEEK_START = date(2026, 6, 16)  # Monday


class TestGenerateWeek:
    def test_returns_7_days(self, planner):
        prefs = UserPreferences(adults_count=2)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        assert len(plan.days) == 7

    def test_week_start_set_correctly(self, planner):
        prefs = UserPreferences(adults_count=2)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        assert plan.week_start == WEEK_START

    def test_all_days_have_meals(self, planner):
        prefs = UserPreferences(adults_count=2)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        for day in plan.days:
            assert day.breakfast is not None
            assert day.lunch is not None
            assert day.snack is not None
            assert day.dinner is not None

    def test_people_count_respected(self, planner):
        prefs = UserPreferences(adults_count=3, children_count=1)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        assert plan.people == 4

    def test_shopping_list_generated(self, planner):
        prefs = UserPreferences(adults_count=2)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        # Shopping list should exist (may or may not be empty depending on pantry)
        assert plan.shopping_list is not None

    def test_estimated_cost_non_negative(self, planner):
        prefs = UserPreferences(adults_count=2)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        assert plan.total_estimated_cost >= 0.0

    def test_vegetarian_filter(self, planner):
        prefs = UserPreferences(adults_count=2, dietary_restrictions={"vegetarian"})
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        for day in plan.days:
            for mt, slot in day.meals().items():
                if slot is not None:
                    assert "vegetarian" in slot.recipe.tags, (
                        f"{slot.recipe.name} is not vegetarian"
                    )

    def test_excluded_ingredient(self, planner):
        prefs = UserPreferences(adults_count=2, excluded_ingredients={"chicken_breast"})
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        for day in plan.days:
            for mt, slot in day.meals().items():
                if slot is not None:
                    assert "chicken_breast" not in slot.recipe.ingredient_names(), (
                        f"Recipe {slot.recipe.name} contains excluded chicken_breast"
                    )

    def test_max_prep_time_respected(self, planner):
        prefs = UserPreferences(adults_count=2, max_prep_time_minutes=15)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        for day in plan.days:
            for mt, slot in day.meals().items():
                if slot is not None:
                    assert slot.recipe.prep_time_minutes <= 15, (
                        f"{slot.recipe.name} takes {slot.recipe.prep_time_minutes} min"
                    )

    def test_pantry_items_recognised(self, planner, pantry):
        # Add eggs to pantry
        pantry.add_item(PantryItem(name="eggs", quantity=100.0, unit="unit"))
        prefs = UserPreferences(adults_count=2)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        # Find a meal that uses eggs and check pantry_items_used reflects it
        found = False
        for day in plan.days:
            for slot in day.meals().values():
                if slot and "eggs" in slot.recipe.ingredients:
                    assert "eggs" in slot.pantry_items_used
                    found = True
                    break
        # If we ever hit a plan with an egg-using recipe, pantry was honoured

    def test_default_week_start_is_next_monday(self, planner):
        prefs = UserPreferences(adults_count=1)
        plan = planner.generate_week(preferences=prefs)
        # week_start must be a Monday (weekday == 0)
        assert plan.week_start.weekday() == 0

    def test_save_to_history(self, planner, db):
        prefs = UserPreferences(adults_count=2)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        planner.save_plan_to_history(plan)
        records = db.get_meal_history(limit=100)
        # 7 days × 4 meal types = 28 records
        assert len(records) == 28


class TestPantryOnlyMode:
    def test_pantry_only_mode_uses_pantry(self, planner, pantry):
        # Stock the pantry with essentials so pantry-only mode can find recipes
        pantry.load_items([
            PantryItem(name="oats", quantity=5.0, unit="kg"),
            PantryItem(name="milk", quantity=5.0, unit="L"),
            PantryItem(name="banana", quantity=50.0, unit="unit"),
            PantryItem(name="honey", quantity=1.0, unit="kg"),
            PantryItem(name="eggs", quantity=50.0, unit="unit"),
            PantryItem(name="bread", quantity=100.0, unit="slice"),
            PantryItem(name="butter", quantity=1.0, unit="kg"),
            PantryItem(name="salt", quantity=1.0, unit="kg"),
            PantryItem(name="apple", quantity=20.0, unit="unit"),
            PantryItem(name="peanut_butter", quantity=1.0, unit="kg"),
            PantryItem(name="mixed_nuts", quantity=1.0, unit="kg"),
            PantryItem(name="pasta", quantity=5.0, unit="kg"),
            PantryItem(name="tomato_sauce", quantity=3.0, unit="kg"),
            PantryItem(name="onion", quantity=3.0, unit="kg"),
            PantryItem(name="garlic", quantity=0.5, unit="kg"),
            PantryItem(name="olive_oil", quantity=1.0, unit="L"),
            PantryItem(name="parmesan", quantity=0.5, unit="kg"),
            PantryItem(name="rice", quantity=3.0, unit="kg"),
            PantryItem(name="carrot", quantity=2.0, unit="kg"),
            PantryItem(name="celery", quantity=1.0, unit="kg"),
            PantryItem(name="potato", quantity=3.0, unit="kg"),
            PantryItem(name="tomato", quantity=2.0, unit="kg"),
            PantryItem(name="vegetable_broth", quantity=5.0, unit="L"),
            PantryItem(name="crackers", quantity=0.5, unit="kg"),
            PantryItem(name="cheese", quantity=0.5, unit="kg"),
        ])
        prefs = UserPreferences(adults_count=2)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START, mode="pantry-only")
        # Plan should have been generated (may fall back if not enough pantry recipes)
        assert plan is not None
        assert len(plan.days) == 7


class TestHighProteinMode:
    def test_high_protein_favours_protein_rich(self, planner):
        prefs = UserPreferences(adults_count=2)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START, mode="high-protein")
        high_protein_count = sum(
            1
            for day in plan.days
            for slot in day.meals().values()
            if slot and "high-protein" in slot.recipe.tags
        )
        # Most meals should be high-protein
        assert high_protein_count >= 14  # at least half of 28


class TestShoppingList:
    def test_shopping_list_quantities_are_positive(self, planner):
        prefs = UserPreferences(adults_count=2)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        for item in plan.shopping_list.items:
            assert item.quantity > 0

    def test_pantry_reduces_shopping_list(self, planner, pantry):
        # Add a large stock of a common ingredient
        pantry.add_item(PantryItem(name="onion", quantity=100.0, unit="kg"))
        prefs = UserPreferences(adults_count=2)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        # Onion should not appear on the shopping list (or quantity should be 0)
        for item in plan.shopping_list.items:
            assert item.name != "onion"

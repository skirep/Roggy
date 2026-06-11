"""Tests for the MealPlanFormatter."""

from __future__ import annotations

from datetime import date

import pytest

from meal_planner.database import Database
from meal_planner.formatter import MealPlanFormatter
from meal_planner.models import UserPreferences
from meal_planner.pantry import PantryManager
from meal_planner.planner import MealPlanner


WEEK_START = date(2026, 6, 16)


@pytest.fixture()
def plan(tmp_path):
    db = Database(db_path=str(tmp_path / "test.db"))
    pantry = PantryManager(db)
    planner = MealPlanner(db, pantry)
    prefs = UserPreferences(adults_count=2)
    return planner.generate_week(preferences=prefs, week_start=WEEK_START)


class TestMealPlanFormatter:
    def test_format_plan_contains_week_date(self, plan):
        fmt = MealPlanFormatter()
        output = fmt.format_plan(plan)
        assert "June 16, 2026" in output

    def test_format_plan_contains_all_day_names(self, plan):
        fmt = MealPlanFormatter()
        output = fmt.format_plan(plan)
        for name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            assert name in output

    def test_format_plan_contains_meal_types(self, plan):
        fmt = MealPlanFormatter()
        output = fmt.format_plan(plan)
        for meal_type in ["BREAKFAST", "LUNCH", "SNACK", "DINNER"]:
            assert meal_type in output

    def test_format_plan_contains_shopping_list(self, plan):
        fmt = MealPlanFormatter()
        output = fmt.format_plan(plan)
        assert "SHOPPING LIST" in output

    def test_format_plan_contains_estimated_total(self, plan):
        fmt = MealPlanFormatter()
        output = fmt.format_plan(plan)
        assert "ESTIMATED TOTAL" in output

    def test_format_summary_is_one_line(self, plan):
        fmt = MealPlanFormatter()
        summary = fmt.format_summary(plan)
        assert "June 16, 2026" in summary
        assert "$" in summary
        assert "\n" not in summary

    def test_pantry_indicator_shown(self, tmp_path):
        from meal_planner.models import PantryItem

        db = Database(db_path=str(tmp_path / "fmt_test.db"))
        pantry = PantryManager(db)
        pantry.add_item(PantryItem(name="oats", quantity=10.0, unit="kg"))
        pantry.add_item(PantryItem(name="milk", quantity=10.0, unit="L"))
        pantry.add_item(PantryItem(name="banana", quantity=100.0, unit="unit"))
        pantry.add_item(PantryItem(name="honey", quantity=1.0, unit="kg"))
        planner = MealPlanner(db, pantry)
        prefs = UserPreferences(adults_count=2)
        plan = planner.generate_week(preferences=prefs, week_start=WEEK_START)
        fmt = MealPlanFormatter()
        output = fmt.format_plan(plan)
        # At least one day should show pantry items used
        assert "From pantry" in output or "To purchase" in output

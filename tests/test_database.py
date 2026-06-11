"""Tests for the Database layer."""

from __future__ import annotations

import tempfile
from datetime import date, timedelta

import pytest

from meal_planner.database import Database
from meal_planner.models import PantryItem


@pytest.fixture()
def db(tmp_path):
    """Return a fresh in-memory-backed Database for each test."""
    return Database(db_path=str(tmp_path / "test.db"))


class TestMealHistory:
    def test_record_and_retrieve(self, db):
        today = date.today()
        meal_id = db.record_meal(today, "dinner", "Spaghetti Bolognese", 4)
        assert meal_id is not None
        records = db.get_meal_history(limit=10)
        assert len(records) == 1
        r = records[0]
        assert r.meal_date == today
        assert r.meal_type == "dinner"
        assert r.recipe_name == "Spaghetti Bolognese"
        assert r.people == 4
        assert r.user_rating is None
        assert r.family_feedback is None

    def test_update_feedback(self, db):
        today = date.today()
        meal_id = db.record_meal(today, "breakfast", "Oatmeal with Fruit", 2)
        db.update_meal_feedback(meal_id, user_rating=5, family_feedback="Delicious!")
        records = db.get_meal_history()
        r = records[0]
        assert r.user_rating == 5
        assert r.family_feedback == "Delicious!"

    def test_get_recent_recipes(self, db):
        today = date.today()
        yesterday = today - timedelta(days=1)
        old_date = today - timedelta(days=20)
        db.record_meal(today, "dinner", "Recipe A", 2)
        db.record_meal(yesterday, "lunch", "Recipe B", 2)
        db.record_meal(old_date, "dinner", "Recipe C", 2)  # older than 14 days

        recent = db.get_recent_recipes(days=14)
        assert "Recipe A" in recent
        assert "Recipe B" in recent
        assert "Recipe C" not in recent

    def test_get_recipe_usage_count(self, db):
        today = date.today()
        yesterday = today - timedelta(days=1)
        db.record_meal(today, "dinner", "Pasta", 2)
        db.record_meal(today, "lunch", "Pasta", 2)
        count = db.get_recipe_usage_count("Pasta", days=7)
        assert count == 2
        # A recipe not recorded should return 0
        count_absent = db.get_recipe_usage_count("NonExistentRecipe", days=7)
        assert count_absent == 0

    def test_filter_by_meal_type(self, db):
        today = date.today()
        db.record_meal(today, "breakfast", "Pancakes", 2)
        db.record_meal(today, "dinner", "Spaghetti", 2)

        breakfast_records = db.get_meal_history(meal_type="breakfast")
        assert len(breakfast_records) == 1
        assert breakfast_records[0].recipe_name == "Pancakes"


class TestPantry:
    def test_upsert_and_get(self, db):
        item = PantryItem(name="eggs", quantity=12.0, unit="unit")
        db.upsert_pantry_item(item)
        pantry = db.get_pantry()
        assert len(pantry) == 1
        assert pantry[0].name == "eggs"
        assert pantry[0].quantity == 12.0

    def test_upsert_updates_existing(self, db):
        item = PantryItem(name="milk", quantity=2.0, unit="L")
        db.upsert_pantry_item(item)
        updated = PantryItem(name="milk", quantity=0.5, unit="L")
        db.upsert_pantry_item(updated)
        pantry = db.get_pantry()
        assert len(pantry) == 1
        assert pantry[0].quantity == 0.5

    def test_remove_item(self, db):
        item = PantryItem(name="butter", quantity=0.5, unit="kg")
        db.upsert_pantry_item(item)
        db.remove_pantry_item("butter")
        assert db.get_pantry() == []

    def test_clear_pantry(self, db):
        for name in ("a", "b", "c"):
            db.upsert_pantry_item(PantryItem(name=name, quantity=1.0, unit="kg"))
        db.clear_pantry()
        assert db.get_pantry() == []

    def test_expiry_date_roundtrip(self, db):
        expiry = date(2026, 12, 31)
        item = PantryItem(name="yogurt", quantity=0.5, unit="kg", expiry_date=expiry)
        db.upsert_pantry_item(item)
        retrieved = db.get_pantry()[0]
        assert retrieved.expiry_date == expiry


class TestUserPreferences:
    def test_set_and_get(self, db):
        db.set_preference("weekly_budget", "150.00")
        value = db.get_preference("weekly_budget")
        assert value == "150.00"

    def test_get_missing_key_returns_default(self, db):
        value = db.get_preference("nonexistent", default="42")
        assert value == "42"

    def test_update_preference(self, db):
        db.set_preference("people", "3")
        db.set_preference("people", "4")
        assert db.get_preference("people") == "4"

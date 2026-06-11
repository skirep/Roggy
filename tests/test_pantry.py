"""Tests for PantryManager."""

from __future__ import annotations

from datetime import date

import pytest

from meal_planner.database import Database
from meal_planner.models import PantryItem
from meal_planner.pantry import PantryManager


@pytest.fixture()
def db(tmp_path):
    return Database(db_path=str(tmp_path / "test.db"))


@pytest.fixture()
def pantry(db):
    return PantryManager(db)


class TestPantryManager:
    def test_add_and_get_item(self, pantry):
        pantry.add_item(PantryItem(name="eggs", quantity=6.0, unit="unit"))
        item = pantry.get_item("eggs")
        assert item is not None
        assert item.quantity == 6.0

    def test_get_missing_item(self, pantry):
        assert pantry.get_item("unicorn") is None

    def test_remove_item(self, pantry):
        pantry.add_item(PantryItem(name="butter", quantity=0.25, unit="kg"))
        pantry.remove_item("butter")
        assert pantry.get_item("butter") is None

    def test_clear(self, pantry):
        pantry.add_item(PantryItem(name="salt", quantity=0.5, unit="kg"))
        pantry.clear()
        assert pantry.get_all() == []

    def test_as_dict(self, pantry):
        pantry.add_item(PantryItem(name="Milk", quantity=1.0, unit="L"))
        d = pantry.as_dict()
        assert "milk" in d  # lower-cased key

    def test_coverage_full(self, pantry):
        pantry.add_item(PantryItem(name="eggs", quantity=12.0, unit="unit"))
        # Need 4 eggs – fully covered
        assert pantry.coverage("eggs", 4.0, "unit") == pytest.approx(4.0)

    def test_coverage_partial(self, pantry):
        pantry.add_item(PantryItem(name="milk", quantity=0.3, unit="L"))
        # Need 0.5 L but only 0.3 available
        assert pantry.coverage("milk", 0.5, "L") == pytest.approx(0.3)

    def test_coverage_missing(self, pantry):
        assert pantry.coverage("pasta", 0.1, "kg") == pytest.approx(0.0)

    def test_coverage_unit_mismatch(self, pantry):
        pantry.add_item(PantryItem(name="milk", quantity=1.0, unit="L"))
        # Pantry has 'L' but we request 'mL'
        assert pantry.coverage("milk", 500.0, "mL") == pytest.approx(0.0)

    def test_needed_to_buy_fully_covered(self, pantry):
        pantry.add_item(PantryItem(name="salt", quantity=1.0, unit="kg"))
        assert pantry.needed_to_buy("salt", 0.002, "kg") == pytest.approx(0.0)

    def test_needed_to_buy_partially_covered(self, pantry):
        pantry.add_item(PantryItem(name="olive_oil", quantity=0.2, unit="L"))
        needed = pantry.needed_to_buy("olive_oil", 0.5, "L")
        assert needed == pytest.approx(0.3)

    def test_deduct(self, pantry):
        pantry.add_item(PantryItem(name="flour", quantity=1.0, unit="kg"))
        pantry.deduct("flour", 0.3, "kg")
        assert pantry.get_item("flour").quantity == pytest.approx(0.7)

    def test_deduct_below_zero_clamps_to_zero(self, pantry):
        pantry.add_item(PantryItem(name="honey", quantity=0.1, unit="kg"))
        pantry.deduct("honey", 0.5, "kg")  # more than available
        assert pantry.get_item("honey").quantity == pytest.approx(0.0)

    def test_deduct_missing_ingredient_is_noop(self, pantry):
        pantry.deduct("unicorn_dust", 1.0, "kg")  # should not raise

    def test_load_items_replaces_existing(self, pantry):
        pantry.add_item(PantryItem(name="old_item", quantity=1.0, unit="kg"))
        new_items = [
            PantryItem(name="new_a", quantity=0.5, unit="kg"),
            PantryItem(name="new_b", quantity=1.0, unit="L"),
        ]
        pantry.load_items(new_items)
        names = {i.name for i in pantry.get_all()}
        assert names == {"new_a", "new_b"}

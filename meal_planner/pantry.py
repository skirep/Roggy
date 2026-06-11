"""Pantry management for the Weekly Meal Planner."""

from __future__ import annotations

from typing import Dict, List, Optional

from .database import Database
from .models import PantryItem


class PantryManager:
    """Manages pantry inventory using the database."""

    def __init__(self, db: Database) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Inventory CRUD
    # ------------------------------------------------------------------

    def add_item(self, item: PantryItem) -> None:
        """Add or update a pantry item."""
        self._db.upsert_pantry_item(item)

    def remove_item(self, name: str) -> None:
        """Remove an item from the pantry."""
        self._db.remove_pantry_item(name)

    def get_all(self) -> List[PantryItem]:
        """Return all items currently in the pantry."""
        return self._db.get_pantry()

    def get_item(self, name: str) -> Optional[PantryItem]:
        """Return a specific pantry item by name, or None if not found."""
        for item in self.get_all():
            if item.name.lower() == name.lower():
                return item
        return None

    def as_dict(self) -> Dict[str, PantryItem]:
        """Return pantry items as a dict keyed by ingredient name (lower-case)."""
        return {item.name.lower(): item for item in self.get_all()}

    def clear(self) -> None:
        """Remove all items from the pantry."""
        self._db.clear_pantry()

    def load_items(self, items: List[PantryItem]) -> None:
        """Replace the entire pantry with the given item list."""
        self.clear()
        for item in items:
            self.add_item(item)

    # ------------------------------------------------------------------
    # Coverage checks
    # ------------------------------------------------------------------

    def coverage(
        self,
        ingredient: str,
        required_quantity: float,
        unit: str,
    ) -> float:
        """
        Return how much of *required_quantity* can be covered from the pantry.

        Returns a value in [0, required_quantity].  Currently assumes units
        match (caller is responsible for consistency).
        """
        item = self.get_item(ingredient)
        if item is None or item.unit != unit:
            return 0.0
        return min(item.quantity, required_quantity)

    def needed_to_buy(
        self,
        ingredient: str,
        required_quantity: float,
        unit: str,
    ) -> float:
        """Return how much of *ingredient* still needs to be purchased."""
        covered = self.coverage(ingredient, required_quantity, unit)
        return max(0.0, required_quantity - covered)

    def deduct(self, ingredient: str, quantity: float, unit: str) -> None:
        """
        Deduct *quantity* of *ingredient* from pantry stock.

        If the pantry has less than the requested quantity, the stock is set
        to zero (no negative quantities).
        """
        item = self.get_item(ingredient)
        if item is None:
            return
        new_qty = max(0.0, item.quantity - quantity)
        updated = PantryItem(
            name=item.name,
            quantity=new_qty,
            unit=item.unit,
            expiry_date=item.expiry_date,
        )
        self._db.upsert_pantry_item(updated)

"""SQLite database layer for the Weekly Meal Planner."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date
from typing import Generator, List, Optional

from .models import MealHistory, PantryItem


class Database:
    """Manages the SQLite database for meal history and pantry."""

    def __init__(self, db_path: str = "meal_planner.db") -> None:
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Create all tables if they do not exist yet."""
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS meal_history (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    meal_date   TEXT    NOT NULL,
                    meal_type   TEXT    NOT NULL,
                    recipe_name TEXT    NOT NULL,
                    people      INTEGER NOT NULL DEFAULT 2,
                    user_rating INTEGER,
                    family_feedback TEXT,
                    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS pantry (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT    NOT NULL UNIQUE,
                    quantity    REAL    NOT NULL DEFAULT 0,
                    unit        TEXT    NOT NULL DEFAULT '',
                    expiry_date TEXT
                );

                CREATE TABLE IF NOT EXISTS user_preferences (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    # ------------------------------------------------------------------
    # Meal history
    # ------------------------------------------------------------------

    def record_meal(
        self,
        meal_date: date,
        meal_type: str,
        recipe_name: str,
        people: int,
    ) -> int:
        """Insert a meal history record and return its id."""
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO meal_history (meal_date, meal_type, recipe_name, people)
                VALUES (?, ?, ?, ?)
                """,
                (meal_date.isoformat(), meal_type, recipe_name, people),
            )
            return cur.lastrowid  # type: ignore[return-value]

    def update_meal_feedback(
        self,
        meal_id: int,
        user_rating: Optional[int] = None,
        family_feedback: Optional[str] = None,
    ) -> None:
        """Update rating and feedback for an existing history record."""
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE meal_history
                SET user_rating = COALESCE(?, user_rating),
                    family_feedback = COALESCE(?, family_feedback)
                WHERE id = ?
                """,
                (user_rating, family_feedback, meal_id),
            )

    def get_recent_recipes(self, days: int = 14) -> List[str]:
        """Return distinct recipe names used in the last *days* days."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT DISTINCT recipe_name
                FROM meal_history
                WHERE meal_date >= date('now', ?)
                ORDER BY meal_date DESC
                """,
                (f"-{days} days",),
            ).fetchall()
        return [r["recipe_name"] for r in rows]

    def get_recipe_usage_count(self, recipe_name: str, days: int = 30) -> int:
        """Return how many times a recipe has been used in the last *days* days."""
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) AS cnt
                FROM meal_history
                WHERE recipe_name = ?
                  AND meal_date >= date('now', ?)
                """,
                (recipe_name, f"-{days} days"),
            ).fetchone()
        return int(row["cnt"])

    def get_meal_history(
        self,
        limit: int = 50,
        meal_type: Optional[str] = None,
    ) -> List[MealHistory]:
        """Return recent meal history records."""
        query = "SELECT * FROM meal_history"
        params: list = []
        if meal_type:
            query += " WHERE meal_type = ?"
            params.append(meal_type)
        query += " ORDER BY meal_date DESC LIMIT ?"
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()

        return [
            MealHistory(
                id=r["id"],
                meal_date=date.fromisoformat(r["meal_date"]),
                meal_type=r["meal_type"],
                recipe_name=r["recipe_name"],
                people=r["people"],
                user_rating=r["user_rating"],
                family_feedback=r["family_feedback"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    # ------------------------------------------------------------------
    # Pantry
    # ------------------------------------------------------------------

    def upsert_pantry_item(self, item: PantryItem) -> None:
        """Insert or update a pantry item."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO pantry (name, quantity, unit, expiry_date)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    quantity    = excluded.quantity,
                    unit        = excluded.unit,
                    expiry_date = excluded.expiry_date
                """,
                (
                    item.name,
                    item.quantity,
                    item.unit,
                    item.expiry_date.isoformat() if item.expiry_date else None,
                ),
            )

    def get_pantry(self) -> List[PantryItem]:
        """Return all current pantry items."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM pantry ORDER BY name").fetchall()
        return [
            PantryItem(
                name=r["name"],
                quantity=r["quantity"],
                unit=r["unit"],
                expiry_date=date.fromisoformat(r["expiry_date"]) if r["expiry_date"] else None,
            )
            for r in rows
        ]

    def remove_pantry_item(self, name: str) -> None:
        """Remove a pantry item by name."""
        with self._connect() as conn:
            conn.execute("DELETE FROM pantry WHERE name = ?", (name,))

    def clear_pantry(self) -> None:
        """Remove all pantry items."""
        with self._connect() as conn:
            conn.execute("DELETE FROM pantry")

    # ------------------------------------------------------------------
    # User preferences (key-value store)
    # ------------------------------------------------------------------

    def set_preference(self, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO user_preferences (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )

    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM user_preferences WHERE key = ?", (key,)
            ).fetchone()
        return row["value"] if row else default

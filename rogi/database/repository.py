"""SQLite repository layer for ROGI."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import (
    DigestModel,
    EmailModel,
    FamilyMemberModel,
    FavoriteProductModel,
    FoodPreferenceModel,
    MealHistoryModel,
    MealPlanModel,
    PantryItemModel,
    ShoppingHabitModel,
    ShoppingListModel,
)
from .schema import create_all_tables

logger = logging.getLogger(__name__)


def _row_factory(cursor: sqlite3.Cursor, row: tuple) -> Dict[str, Any]:
    """Return rows as dicts keyed by column name."""
    cols = [d[0] for d in cursor.description]
    return dict(zip(cols, row))


class Repository:
    """Central data access object backed by SQLite."""

    def __init__(self, db_path: str | Path = "rogi.db") -> None:
        self._path = str(db_path)
        self._conn: Optional[sqlite3.Connection] = None

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Open the database connection and ensure schema exists."""
        self._conn = sqlite3.connect(self._path, check_same_thread=False)
        self._conn.row_factory = _row_factory  # type: ignore[assignment]
        self._conn.execute("PRAGMA journal_mode=WAL;")
        create_all_tables(self._conn)
        logger.info("Connected to ROGI database: %s", self._path)

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self.connect()
        return self._conn  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Pantry
    # ------------------------------------------------------------------

    def upsert_pantry_item(self, item: PantryItemModel) -> None:
        self.conn.execute(
            """
            INSERT INTO pantry (name, quantity, unit, category, purchase_date, expiry_date, updated_at)
            VALUES (:name, :quantity, :unit, :category, :purchase_date, :expiry_date, datetime('now'))
            ON CONFLICT(name) DO UPDATE SET
                quantity=excluded.quantity,
                unit=excluded.unit,
                category=excluded.category,
                purchase_date=excluded.purchase_date,
                expiry_date=excluded.expiry_date,
                updated_at=datetime('now')
            """,
            {
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "category": item.category,
                "purchase_date": item.purchase_date.isoformat() if item.purchase_date else None,
                "expiry_date": item.expiry_date.isoformat() if item.expiry_date else None,
            },
        )
        self.conn.commit()

    def get_pantry(self) -> List[PantryItemModel]:
        rows = self.conn.execute("SELECT * FROM pantry ORDER BY name").fetchall()
        return [_parse_pantry_row(r) for r in rows]

    def get_pantry_item(self, name: str) -> Optional[PantryItemModel]:
        row = self.conn.execute(
            "SELECT * FROM pantry WHERE LOWER(name)=LOWER(?)", (name,)
        ).fetchone()
        return _parse_pantry_row(row) if row else None

    def delete_pantry_item(self, name: str) -> None:
        self.conn.execute("DELETE FROM pantry WHERE LOWER(name)=LOWER(?)", (name,))
        self.conn.commit()

    def get_expiring_pantry(self, days: int = 7) -> List[PantryItemModel]:
        rows = self.conn.execute(
            "SELECT * FROM pantry WHERE expiry_date IS NOT NULL "
            "AND expiry_date <= date('now', ?)",
            (f"+{days} days",),
        ).fetchall()
        return [_parse_pantry_row(r) for r in rows]

    # ------------------------------------------------------------------
    # Emails
    # ------------------------------------------------------------------

    def upsert_email(self, email: EmailModel) -> None:
        self.conn.execute(
            """
            INSERT INTO emails
                (message_id, account, sender, subject, body_snippet,
                 received_at, category, is_invoice, is_appointment,
                 is_important, summary)
            VALUES
                (:message_id, :account, :sender, :subject, :body_snippet,
                 :received_at, :category, :is_invoice, :is_appointment,
                 :is_important, :summary)
            ON CONFLICT(message_id) DO UPDATE SET
                category=excluded.category,
                is_invoice=excluded.is_invoice,
                is_appointment=excluded.is_appointment,
                is_important=excluded.is_important,
                summary=excluded.summary
            """,
            {
                "message_id": email.message_id,
                "account": email.account,
                "sender": email.sender,
                "subject": email.subject,
                "body_snippet": email.body_snippet,
                "received_at": email.received_at.isoformat() if email.received_at else None,
                "category": email.category,
                "is_invoice": int(email.is_invoice),
                "is_appointment": int(email.is_appointment),
                "is_important": int(email.is_important),
                "summary": email.summary,
            },
        )
        self.conn.commit()

    def get_emails(
        self,
        limit: int = 50,
        category: Optional[str] = None,
        account: Optional[str] = None,
    ) -> List[EmailModel]:
        query = "SELECT * FROM emails WHERE 1=1"
        params: List[Any] = []
        if category:
            query += " AND category=?"
            params.append(category)
        if account:
            query += " AND account=?"
            params.append(account)
        query += " ORDER BY received_at DESC LIMIT ?"
        params.append(limit)
        rows = self.conn.execute(query, params).fetchall()
        return [_parse_email_row(r) for r in rows]

    def get_unread_emails(self, since: Optional[datetime] = None) -> List[EmailModel]:
        query = "SELECT * FROM emails WHERE 1=1"
        params: List[Any] = []
        if since:
            query += " AND received_at >= ?"
            params.append(since.isoformat())
        query += " ORDER BY received_at DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [_parse_email_row(r) for r in rows]

    # ------------------------------------------------------------------
    # Meal plans & history
    # ------------------------------------------------------------------

    def save_meal_plan(self, plan: MealPlanModel) -> None:
        self.conn.execute(
            "INSERT INTO meal_plans (week_start, people, plan_json) VALUES (?,?,?)",
            (plan.week_start.isoformat(), plan.people, plan.plan_json),
        )
        self.conn.commit()

    def get_latest_meal_plan(self) -> Optional[MealPlanModel]:
        row = self.conn.execute(
            "SELECT * FROM meal_plans ORDER BY week_start DESC LIMIT 1"
        ).fetchone()
        return _parse_meal_plan_row(row) if row else None

    def save_meal_history(self, entry: MealHistoryModel) -> None:
        self.conn.execute(
            """INSERT INTO meal_history
               (meal_date, meal_type, recipe_name, people, user_rating, family_feedback)
               VALUES (?,?,?,?,?,?)""",
            (
                entry.meal_date.isoformat(),
                entry.meal_type,
                entry.recipe_name,
                entry.people,
                entry.user_rating,
                entry.family_feedback,
            ),
        )
        self.conn.commit()

    def get_recent_recipes(self, days: int = 14) -> List[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT recipe_name FROM meal_history "
            "WHERE meal_date >= date('now', ?)",
            (f"-{days} days",),
        ).fetchall()
        return [r["recipe_name"] for r in rows]

    # ------------------------------------------------------------------
    # Shopping lists
    # ------------------------------------------------------------------

    def save_shopping_list(self, shopping: ShoppingListModel) -> int:
        cursor = self.conn.execute(
            "INSERT INTO shopping_lists (name, items_json, total_cost, status) VALUES (?,?,?,?)",
            (shopping.name, json.dumps(shopping.items), shopping.total_cost, shopping.status),
        )
        self.conn.commit()
        return cursor.lastrowid  # type: ignore[return-value]

    def get_shopping_list(self, list_id: int) -> Optional[ShoppingListModel]:
        row = self.conn.execute(
            "SELECT * FROM shopping_lists WHERE id=?", (list_id,)
        ).fetchone()
        return _parse_shopping_row(row) if row else None

    def list_shopping_lists(self, status: Optional[str] = None) -> List[ShoppingListModel]:
        query = "SELECT * FROM shopping_lists"
        params: List[Any] = []
        if status:
            query += " WHERE status=?"
            params.append(status)
        query += " ORDER BY created_at DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [_parse_shopping_row(r) for r in rows]

    def update_shopping_status(self, list_id: int, status: str) -> None:
        self.conn.execute(
            "UPDATE shopping_lists SET status=?, updated_at=datetime('now') WHERE id=?",
            (status, list_id),
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    # Memory – food preferences
    # ------------------------------------------------------------------

    def add_food_preference(self, pref: FoodPreferenceModel) -> None:
        self.conn.execute(
            "INSERT INTO memory_food_preferences (preference_type, item, member, notes) VALUES (?,?,?,?)",
            (pref.preference_type, pref.item, pref.member, pref.notes),
        )
        self.conn.commit()

    def get_food_preferences(self) -> List[FoodPreferenceModel]:
        rows = self.conn.execute(
            "SELECT * FROM memory_food_preferences ORDER BY item"
        ).fetchall()
        return [
            FoodPreferenceModel(
                id=r["id"],
                preference_type=r["preference_type"],
                item=r["item"],
                member=r["member"],
                notes=r["notes"],
            )
            for r in rows
        ]

    # ------------------------------------------------------------------
    # Memory – family members
    # ------------------------------------------------------------------

    def upsert_family_member(self, member: FamilyMemberModel) -> None:
        self.conn.execute(
            """
            INSERT INTO memory_family (name, role, age, dietary_notes)
            VALUES (:name, :role, :age, :dietary_notes)
            ON CONFLICT(name) DO UPDATE SET
                role=excluded.role, age=excluded.age,
                dietary_notes=excluded.dietary_notes
            """,
            {
                "name": member.name,
                "role": member.role,
                "age": member.age,
                "dietary_notes": member.dietary_notes,
            },
        )
        self.conn.commit()

    def get_family(self) -> List[FamilyMemberModel]:
        rows = self.conn.execute("SELECT * FROM memory_family ORDER BY name").fetchall()
        return [
            FamilyMemberModel(
                id=r["id"],
                name=r["name"],
                role=r["role"],
                age=r["age"],
                dietary_notes=r["dietary_notes"],
            )
            for r in rows
        ]

    # ------------------------------------------------------------------
    # Memory – favorite products
    # ------------------------------------------------------------------

    def add_favorite_product(self, product: FavoriteProductModel) -> None:
        self.conn.execute(
            "INSERT INTO memory_favorite_products (product_name, brand, supermarket, notes) VALUES (?,?,?,?)",
            (product.product_name, product.brand, product.supermarket, product.notes),
        )
        self.conn.commit()

    def get_favorite_products(self) -> List[FavoriteProductModel]:
        rows = self.conn.execute(
            "SELECT * FROM memory_favorite_products ORDER BY product_name"
        ).fetchall()
        return [
            FavoriteProductModel(
                id=r["id"],
                product_name=r["product_name"],
                brand=r["brand"],
                supermarket=r["supermarket"],
                notes=r["notes"],
            )
            for r in rows
        ]

    # ------------------------------------------------------------------
    # Memory – shopping habits
    # ------------------------------------------------------------------

    def set_shopping_habit(self, key: str, value: str) -> None:
        self.conn.execute(
            """
            INSERT INTO memory_shopping_habits (habit_key, habit_value)
            VALUES (?,?)
            ON CONFLICT(habit_key) DO UPDATE SET
                habit_value=excluded.habit_value, updated_at=datetime('now')
            """,
            (key, value),
        )
        self.conn.commit()

    def get_shopping_habit(self, key: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT habit_value FROM memory_shopping_habits WHERE habit_key=?", (key,)
        ).fetchone()
        return row["habit_value"] if row else None

    def get_all_shopping_habits(self) -> Dict[str, str]:
        rows = self.conn.execute("SELECT habit_key, habit_value FROM memory_shopping_habits").fetchall()
        return {r["habit_key"]: r["habit_value"] for r in rows}

    # ------------------------------------------------------------------
    # Digests
    # ------------------------------------------------------------------

    def save_digest(self, digest: DigestModel) -> None:
        self.conn.execute(
            """
            INSERT INTO digests (digest_date, content, sent_telegram)
            VALUES (?,?,?)
            ON CONFLICT(digest_date) DO UPDATE SET
                content=excluded.content, sent_telegram=excluded.sent_telegram
            """,
            (digest.digest_date.isoformat(), digest.content, int(digest.sent_telegram)),
        )
        self.conn.commit()

    def get_digest(self, digest_date: date) -> Optional[DigestModel]:
        row = self.conn.execute(
            "SELECT * FROM digests WHERE digest_date=?", (digest_date.isoformat(),)
        ).fetchone()
        return _parse_digest_row(row) if row else None


# ---------------------------------------------------------------------------
# Private helpers – row parsers
# ---------------------------------------------------------------------------


def _parse_pantry_row(r: Dict[str, Any]) -> PantryItemModel:
    return PantryItemModel(
        id=r["id"],
        name=r["name"],
        quantity=r["quantity"],
        unit=r["unit"],
        category=r["category"],
        purchase_date=date.fromisoformat(r["purchase_date"]) if r.get("purchase_date") else None,
        expiry_date=date.fromisoformat(r["expiry_date"]) if r.get("expiry_date") else None,
    )


def _parse_email_row(r: Dict[str, Any]) -> EmailModel:
    return EmailModel(
        id=r["id"],
        message_id=r["message_id"],
        account=r["account"],
        sender=r["sender"],
        subject=r["subject"],
        body_snippet=r["body_snippet"],
        received_at=datetime.fromisoformat(r["received_at"]) if r.get("received_at") else None,
        category=r["category"],
        is_invoice=bool(r["is_invoice"]),
        is_appointment=bool(r["is_appointment"]),
        is_important=bool(r["is_important"]),
        summary=r["summary"],
    )


def _parse_meal_plan_row(r: Dict[str, Any]) -> MealPlanModel:
    return MealPlanModel(
        id=r["id"],
        week_start=date.fromisoformat(r["week_start"]),
        people=r["people"],
        plan_json=r["plan_json"],
    )


def _parse_shopping_row(r: Dict[str, Any]) -> ShoppingListModel:
    return ShoppingListModel(
        id=r["id"],
        name=r["name"],
        items=json.loads(r["items_json"]),
        total_cost=r["total_cost"],
        status=r["status"],
    )


def _parse_digest_row(r: Dict[str, Any]) -> DigestModel:
    return DigestModel(
        id=r["id"],
        digest_date=date.fromisoformat(r["digest_date"]),
        content=r["content"],
        sent_telegram=bool(r["sent_telegram"]),
    )

"""SQLite schema creation for ROGI."""

from __future__ import annotations

import sqlite3
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# DDL statements
# ---------------------------------------------------------------------------

PANTRY_TABLE = """
CREATE TABLE IF NOT EXISTS pantry (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    quantity        REAL NOT NULL DEFAULT 0,
    unit            TEXT NOT NULL DEFAULT 'unit',
    category        TEXT,
    purchase_date   TEXT,
    expiry_date     TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

EMAILS_TABLE = """
CREATE TABLE IF NOT EXISTS emails (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id      TEXT UNIQUE,
    account         TEXT NOT NULL,
    sender          TEXT,
    subject         TEXT,
    body_snippet    TEXT,
    received_at     TEXT,
    category        TEXT,    -- invoice | appointment | important | newsletter | other
    is_invoice      INTEGER NOT NULL DEFAULT 0,
    is_appointment  INTEGER NOT NULL DEFAULT 0,
    is_important    INTEGER NOT NULL DEFAULT 0,
    summary         TEXT,
    processed_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

MEAL_PLANS_TABLE = """
CREATE TABLE IF NOT EXISTS meal_plans (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start      TEXT NOT NULL,
    people          INTEGER NOT NULL DEFAULT 2,
    plan_json       TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

MEAL_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS meal_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_date       TEXT NOT NULL,
    meal_type       TEXT NOT NULL,
    recipe_name     TEXT NOT NULL,
    people          INTEGER NOT NULL DEFAULT 2,
    user_rating     INTEGER,
    family_feedback TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

SHOPPING_LISTS_TABLE = """
CREATE TABLE IF NOT EXISTS shopping_lists (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    items_json      TEXT NOT NULL,
    total_cost      REAL NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'pending',  -- pending | confirmed | ordered | done
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

MEMORY_FOOD_PREFERENCES_TABLE = """
CREATE TABLE IF NOT EXISTS memory_food_preferences (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    preference_type TEXT NOT NULL,   -- like | dislike | allergy | restriction
    item            TEXT NOT NULL,
    member          TEXT,            -- family member name
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

MEMORY_FAMILY_TABLE = """
CREATE TABLE IF NOT EXISTS memory_family (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    role            TEXT,            -- adult | child | pet
    age             INTEGER,
    dietary_notes   TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

MEMORY_FAVORITE_PRODUCTS_TABLE = """
CREATE TABLE IF NOT EXISTS memory_favorite_products (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name    TEXT NOT NULL,
    brand           TEXT,
    supermarket     TEXT,
    notes           TEXT,
    last_seen_at    TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

MEMORY_SHOPPING_HABITS_TABLE = """
CREATE TABLE IF NOT EXISTS memory_shopping_habits (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_key       TEXT NOT NULL UNIQUE,
    habit_value     TEXT NOT NULL,
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

DIGESTS_TABLE = """
CREATE TABLE IF NOT EXISTS digests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    digest_date     TEXT NOT NULL UNIQUE,
    content         TEXT NOT NULL,
    sent_telegram   INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

ALL_TABLES = [
    PANTRY_TABLE,
    EMAILS_TABLE,
    MEAL_PLANS_TABLE,
    MEAL_HISTORY_TABLE,
    SHOPPING_LISTS_TABLE,
    MEMORY_FOOD_PREFERENCES_TABLE,
    MEMORY_FAMILY_TABLE,
    MEMORY_FAVORITE_PRODUCTS_TABLE,
    MEMORY_SHOPPING_HABITS_TABLE,
    DIGESTS_TABLE,
]


def create_all_tables(conn: sqlite3.Connection) -> None:
    """Create all ROGI tables if they do not exist."""
    cursor = conn.cursor()
    for ddl in ALL_TABLES:
        cursor.execute(ddl)
    conn.commit()
    logger.info("All ROGI database tables ensured.")

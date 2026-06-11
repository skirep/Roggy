# ROGI Database Schema

## Overview

ROGI uses SQLite (`rogi.db`) with WAL journal mode for concurrent read performance.

All timestamps are stored in ISO 8601 format (`YYYY-MM-DD HH:MM:SS`).

---

## Tables

### `pantry`

Stores current pantry inventory.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `name` | TEXT UNIQUE | Product name |
| `quantity` | REAL | Amount in stock |
| `unit` | TEXT | Unit (kg, L, unit, etc.) |
| `category` | TEXT | Category (dairy, produce, etc.) |
| `purchase_date` | TEXT | Date purchased (YYYY-MM-DD) |
| `expiry_date` | TEXT | Expiry date (YYYY-MM-DD) |
| `created_at` | TEXT | Row creation time |
| `updated_at` | TEXT | Last update time |

---

### `emails`

Stores processed emails from all accounts.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `message_id` | TEXT UNIQUE | RFC 2822 Message-ID |
| `account` | TEXT | Account label (gmail, outlook) |
| `sender` | TEXT | From address |
| `subject` | TEXT | Email subject |
| `body_snippet` | TEXT | First 500 chars of body |
| `received_at` | TEXT | Email received datetime |
| `category` | TEXT | invoice \| appointment \| important \| newsletter \| other |
| `is_invoice` | INTEGER | Boolean (0/1) |
| `is_appointment` | INTEGER | Boolean (0/1) |
| `is_important` | INTEGER | Boolean (0/1) |
| `summary` | TEXT | AI-generated 1-sentence summary |
| `processed_at` | TEXT | When ROGI processed it |

---

### `meal_plans`

Stores generated weekly meal plans (serialised JSON).

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `week_start` | TEXT | Monday date (YYYY-MM-DD) |
| `people` | INTEGER | Number of people |
| `plan_json` | TEXT | Full plan as JSON |
| `created_at` | TEXT | Row creation time |

---

### `meal_history`

Records meals that were actually eaten.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `meal_date` | TEXT | Date eaten |
| `meal_type` | TEXT | breakfast \| lunch \| snack \| dinner |
| `recipe_name` | TEXT | Recipe name |
| `people` | INTEGER | Number of people served |
| `user_rating` | INTEGER | 1-5 rating |
| `family_feedback` | TEXT | Free-text feedback |
| `created_at` | TEXT | Row creation time |

---

### `shopping_lists`

Manages shopping lists with status lifecycle.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `name` | TEXT | List name |
| `items_json` | TEXT | Items as JSON array |
| `total_cost` | REAL | Estimated total (€) |
| `status` | TEXT | pending → confirmed → ordered → done |
| `created_at` | TEXT | Row creation time |
| `updated_at` | TEXT | Last status change |

> ⚠️ Status `ordered` must only be set after explicit user confirmation.  
> ROGI never transitions to `ordered` automatically.

---

### `memory_food_preferences`

Long-term food preference memory.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `preference_type` | TEXT | like \| dislike \| allergy \| restriction |
| `item` | TEXT | Food item or ingredient |
| `member` | TEXT | Family member name (optional) |
| `notes` | TEXT | Additional notes |
| `created_at` | TEXT | Row creation time |

---

### `memory_family`

Household member registry.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `name` | TEXT UNIQUE | Member name |
| `role` | TEXT | adult \| child \| pet |
| `age` | INTEGER | Age (optional) |
| `dietary_notes` | TEXT | Dietary restrictions / notes |
| `created_at` | TEXT | Row creation time |

---

### `memory_favorite_products`

Products the user likes to buy.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `product_name` | TEXT | Product name |
| `brand` | TEXT | Brand (optional) |
| `supermarket` | TEXT | Where to buy it (optional) |
| `notes` | TEXT | Notes |
| `last_seen_at` | TEXT | Last time seen in search results |
| `created_at` | TEXT | Row creation time |

---

### `memory_shopping_habits`

Key-value store for shopping behaviour patterns.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `habit_key` | TEXT UNIQUE | Habit identifier |
| `habit_value` | TEXT | Value |
| `updated_at` | TEXT | Last update time |

Example keys: `preferred_supermarket`, `shopping_day`, `avg_weekly_budget`

---

### `digests`

Archive of generated daily digests.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `digest_date` | TEXT UNIQUE | Date of the digest (YYYY-MM-DD) |
| `content` | TEXT | Full Markdown content |
| `sent_telegram` | INTEGER | Boolean – was it sent? |
| `created_at` | TEXT | Row creation time |

---

## Entity Relationships

```
pantry ──────────────────────────► meal_plans
                                   meal_history

emails (multiple accounts)

shopping_lists ◄──── ShoppingAgent (never auto-orders)

memory_family ──────────────────► memory_food_preferences
memory_favorite_products
memory_shopping_habits

digests (one per day)
```

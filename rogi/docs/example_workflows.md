# ROGI Example Workflows

## Workflow 1 – Daily Morning Digest (n8n)

**File:** `rogi/workflows/daily_digest.json`

**Trigger:** Every day at 07:00

**What it does:**
1. Calls `POST /api/digest/generate?send_telegram=true`
2. ROGI generates the digest (email summary + pantry alerts + meal suggestions)
3. Sends the result via Telegram

**How to activate:**
1. Import `daily_digest.json` into n8n
2. Enable the workflow
3. Adjust the cron time if needed (default: `0 7 * * *`)

---

## Workflow 2 – Email Processing (n8n)

**File:** `rogi/workflows/email_processing.json`

**Trigger:** Every 30 minutes

**What it does:**
1. `POST /api/email/fetch` – fetches new IMAP emails and classifies them
2. `GET /api/email/?category=important` – retrieves important ones
3. If any important emails exist, summarises them for Telegram

**How to activate:**
1. Import `email_processing.json` into n8n
2. Configure your IMAP accounts in `.env`
3. Enable the workflow

---

## Workflow 3 – Weekly Meal Plan (API call)

No n8n workflow needed – call the existing meal_planner CLI or API directly.

```bash
# CLI (uses existing meal_planner module)
python -m meal_planner.cli --people 2 --budget 80

# Or via ROGI conversational agent
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Generate a meal plan for 2 people with a €80 weekly budget"}'
```

---

## Workflow 4 – Add Pantry Item

```bash
curl -X PUT http://localhost:8000/api/pantry/Tomatoes \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 6,
    "unit": "unit",
    "category": "produce",
    "expiry_date": "2026-06-20"
  }'
```

---

## Workflow 5 – Shopping Search & Confirm

```bash
# 1. Search for a product
curl -X POST http://localhost:8000/api/shopping/search \
  -H "Content-Type: application/json" \
  -d '{"query": "organic milk", "max_results": 5}'

# 2. Create a shopping list (status = pending)
curl -X POST http://localhost:8000/api/shopping/lists \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly shop",
    "items": [
      {"name": "Organic Milk", "quantity": 2, "unit": "L", "price": 1.89}
    ]
  }'

# 3. Confirm the list (user explicitly approves)
curl -X POST http://localhost:8000/api/shopping/lists/1/confirm

# ⚠️  Checkout is NEVER performed automatically.
# The user must proceed to the supermarket website manually.
```

---

## Workflow 6 – Ask ROGI a Question

```bash
# What food do I have?
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What food do I have at home?"}'

# What expires soon?
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What expires this week?"}'

# Important emails?
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Do I have any important emails today?"}'
```

---

## Workflow 7 – Store Family Preferences

```bash
# Add a family member
curl -X PUT http://localhost:8000/api/memory/family/Alice \
  -H "Content-Type: application/json" \
  -d '{"role": "adult", "age": 35, "dietary_notes": "vegetarian"}'

# Add a food dislike
curl -X POST http://localhost:8000/api/memory/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "preference_type": "dislike",
    "item": "broccoli",
    "member": "Alice"
  }'

# ROGI will now take this into account when suggesting meals
```

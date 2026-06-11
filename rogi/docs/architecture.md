# ROGI Architecture

## Design Principles

1. **Local-first** – All data stays on your device. No external APIs except email providers and Telegram.
2. **Low resource consumption** – Designed for 16 GB RAM with local Ollama models.
3. **Modular** – Each feature is a separate Python module. Add supermarkets, agents, or workflows independently.
4. **Privacy by default** – SQLite keeps all data local. Ollama runs fully offline.
5. **Never auto-order** – Shopping automation requires explicit user confirmation before checkout.

---

## Component Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         User Interfaces                          │
├───────────────┬──────────────────┬──────────────────────────────┤
│  Telegram Bot │   Open WebUI     │   Direct API (curl/httpie)   │
│  (interactive)│  (chat on :3000) │   (http://localhost:8000)    │
└───────┬───────┴────────┬─────────┴──────────────┬───────────────┘
        │                │                         │
        └────────────────┼─────────────────────────┘
                         │
              ┌──────────▼───────────┐
              │   FastAPI Backend    │
              │   rogi/backend/      │
              │  ┌──────────────────┐│
              │  │ Routes           ││
              │  │ /api/pantry      ││
              │  │ /api/email       ││
              │  │ /api/chat        ││
              │  │ /api/digest      ││
              │  │ /api/shopping    ││
              │  │ /api/memory      ││
              │  └────────┬─────────┘│
              └───────────┼──────────┘
                          │
          ┌───────────────┼───────────────────┐
          │               │                   │
 ┌────────▼──────┐ ┌──────▼──────┐ ┌─────────▼────────┐
 │ Agents Layer  │ │  Repository │ │  Playwright Layer │
 │ rogi/agents/  │ │ rogi/db/    │ │ rogi/playwright/  │
 │               │ │             │ │                   │
 │ EmailAgent    │ │ SQLite WAL  │ │ BaseSupermarket   │
 │ ConvAgent     │ │ rogi.db     │ │ ExampleSupermarket│
 │ DigestAgent   │ │             │ │ (add more here)   │
 │ ShoppingAgent │ └─────────────┘ └───────────────────┘
 └───────┬───────┘
         │
 ┌───────▼────────┐
 │  Ollama Client │
 │  (qwen3:8b)    │
 │  :11434        │
 └────────────────┘
```

---

## Data Flow – Daily Digest

```
07:00 (cron / n8n)
    │
    ▼
DigestAgent.generate()
    ├── EmailAgent: get recent emails from DB
    ├── Repository: get_expiring_pantry()
    ├── Repository: list_shopping_lists(pending)
    └── OllamaClient: generate meal suggestions
    │
    ▼
DigestModel saved to digests table
    │
    ▼
RogiBot.send_digest() → Telegram
```

---

## Data Flow – Email Processing

```
IMAP Server (Gmail / Outlook)
    │
    ▼
EmailAgent.fetch_imap()
    │  imaplib (stdlib)
    ▼
List[EmailModel] (raw)
    │
    ▼
EmailAgent.classify(email)
    │  OllamaClient.chat() → JSON response
    │  {category, is_invoice, is_appointment, is_important, summary}
    ▼
Repository.upsert_email()
    │  SQLite emails table
    ▼
Available via GET /api/email/
```

---

## Data Flow – Shopping (Safe Pattern)

```
User: "Search for milk"
    │
    ▼
ShoppingAgent.search("milk")
    │  Delegates to registered supermarket scrapers
    │  BaseSupermarket.search() → Playwright browser
    ▼
List of products with prices
    │
    ▼
User reviews & selects
    │
    ▼
ShoppingAgent.create_list_from_items()
    │  Status = "pending"
    ▼
User confirms via /api/shopping/lists/{id}/confirm
    │  Status = "confirmed"
    │
    │  ⚠️  ROGI NEVER proceeds to checkout automatically
    │      User must initiate checkout manually
    ▼
Status = "ordered" (only when user explicitly marks it)
```

---

## Adding a New Supermarket

1. Create `rogi/playwright/supermarkets/my_supermarket.py`
2. Subclass `BaseSupermarket`
3. Implement `search(query, max_results)` using Playwright
4. Register in the app:
   ```python
   from rogi.playwright.supermarkets.my_supermarket import MySupermarket
   app_state.shopping_agent.register_supermarket("mymart", MySupermarket())
   ```

---

## Changing the AI Model

The model is configured via `.env`:

```env
OLLAMA_MODEL=llama3:8b
```

Or via the `OllamaClient` constructor:

```python
ollama = OllamaClient(model="mistral:7b")
```

Pull the model first:
```powershell
ollama pull llama3:8b
```

---

## Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| LLM | Ollama (qwen3:8b) | Local inference |
| Chat UI | Open WebUI | Web chat interface |
| Backend API | FastAPI + uvicorn | REST API |
| Database | SQLite (WAL) | All persistent data |
| Web automation | Playwright | Supermarket scraping |
| Notifications | Telegram Bot API | Daily digest + alerts |
| Email | imaplib (stdlib) | IMAP for Gmail/Outlook |
| Orchestration | n8n | Scheduled workflows |
| Deployment | Docker Compose | Container management |
| Config | pydantic-settings | Typed .env loading |
| Testing | pytest + pytest-asyncio | Unit tests |

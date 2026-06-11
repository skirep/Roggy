# ROGI – ROG Intelligent Assistant

**Local-first AI assistant for ASUS ROG Ally Z1 Extreme (Windows, 16 GB RAM)**

ROGI is a fully local, privacy-first AI assistant that runs on your device without sending data to the cloud. It uses [Ollama](https://ollama.com) with the **Qwen3 4B** model and integrates with your emails, pantry, meal planning, and shopping.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📧 **Email Assistant** | Reads Gmail/Outlook via IMAP, classifies emails, detects invoices & appointments, generates daily summaries |
| 🥫 **Pantry Management** | Tracks food items, quantities, expiry dates, categories |
| 🍽️ **Meal Planning** | Generates weekly meal plans based on pantry, people, budget, preferences |
| 🛒 **Shopping Assistant** | Searches & compares products on supermarket websites (Playwright) |
| 🌅 **Daily Digest** | Morning summary sent via Telegram with emails, pantry alerts, meal suggestions |
| 💬 **Conversational Agent** | Natural-language Q&A backed by local Ollama + SQLite context |
| 🧠 **Memory System** | Long-term storage of food preferences, family members, shopping habits |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     ROGI Stack                          │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Open WebUI │  │  FastAPI     │  │   Telegram    │  │
│  │  (port 3000)│  │  (port 8000) │  │   Bot         │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘  │
│         │                │                  │           │
│         └────────────────┼──────────────────┘           │
│                          │                              │
│                  ┌───────▼────────┐                     │
│                  │  Agents Layer  │                     │
│                  │  - Email Agent │                     │
│                  │  - Conv Agent  │                     │
│                  │  - Digest      │                     │
│                  │  - Shopping    │                     │
│                  └───────┬────────┘                     │
│                          │                              │
│          ┌───────────────┼───────────────┐              │
│          │               │               │              │
│  ┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐       │
│  │   Ollama     │ │   SQLite    │ │ Playwright  │       │
│  │ (qwen3:4b)   │ │ (rogi.db)   │ │ Supermarkets│      │
│  └──────────────┘ └─────────────┘ └────────────┘       │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  n8n Workflows (port 5678)                      │    │
│  │  - Daily Digest (07:00 cron)                    │    │
│  │  - Email Processing (every 30 min)              │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

See [docs/installation.md](docs/installation.md) for the full guide.

```powershell
# 1. Clone and enter the rogi directory
cd rogi

# 2. Copy environment file and configure
Copy-Item .env.example .env
notepad .env

# 3. Start everything
.\start.ps1

# 4. Open the chat interface
Start-Process "http://localhost:3000"
```

---

## 📁 Project Structure

```
rogi/
├── backend/          # FastAPI application
│   ├── main.py       # App factory + lifespan
│   ├── config.py     # Pydantic settings from .env
│   └── routes/       # API route handlers
│       ├── pantry.py
│       ├── meals.py
│       ├── email.py
│       ├── memory.py
│       ├── shopping.py
│       ├── digest.py
│       └── chat.py
├── agents/           # AI agent logic
│   ├── ollama_client.py       # Async Ollama wrapper
│   ├── email_agent.py         # IMAP + classification
│   ├── conversational_agent.py
│   ├── digest_agent.py
│   └── shopping_agent.py
├── database/         # SQLite layer
│   ├── schema.py     # DDL / table creation
│   ├── models.py     # Pydantic models
│   └── repository.py # Data access object
├── playwright/       # Web automation
│   ├── base.py       # BaseSupermarket ABC
│   └── supermarkets/
│       ├── example_supermarket.py
│       └── (add your own here)
├── telegram/         # Telegram bot
│   ├── bot.py        # HTTP-based bot client
│   └── handlers.py   # Message routing
├── workflows/        # n8n JSON workflow configs
│   ├── daily_digest.json
│   └── email_processing.json
├── docs/             # Documentation
├── tests/            # ROGI-specific tests
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── start.ps1
└── stop.ps1
```

---

## 🔑 API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/pantry/` | List pantry items |
| PUT | `/api/pantry/{name}` | Add/update pantry item |
| DELETE | `/api/pantry/{name}` | Remove pantry item |
| GET | `/api/pantry/expiring?days=7` | Items expiring soon |
| GET | `/api/email/` | List classified emails |
| POST | `/api/email/fetch` | Trigger IMAP fetch |
| GET | `/api/email/summary` | AI email summary |
| POST | `/api/chat/` | Ask ROGI a question |
| POST | `/api/digest/generate` | Generate daily digest |
| GET | `/api/shopping/lists` | List shopping lists |
| POST | `/api/shopping/lists/{id}/confirm` | Confirm a list |
| GET | `/api/memory/family` | Family members |
| GET | `/api/memory/preferences` | Food preferences |

Full interactive docs: **http://localhost:8000/docs**

---

## ⚙️ Configuration

All configuration is done through `.env`. Key variables:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `qwen3:4b` | Ollama model to use |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `DATABASE_PATH` | `rogi.db` | SQLite file path |
| `TELEGRAM_BOT_TOKEN` | — | Telegram bot token |
| `TELEGRAM_CHAT_ID` | — | Your Telegram chat ID |
| `IMAP_ACCOUNTS` | `[]` | JSON array of IMAP configs |

---

## 🧪 Running Tests

```bash
# ROGI tests
pytest rogi/tests/ -v

# All tests (including existing meal_planner)
pytest tests/ rogi/tests/ -v
```

---

## 📜 License

MIT

# ROGI Installation Guide

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Windows 10/11 | — | ASUS ROG Ally Z1 Extreme |
| Python | 3.12 | https://python.org |
| Ollama | latest | https://ollama.com |
| Docker Desktop | latest | Optional – for Open WebUI + n8n |
| Git | latest | https://git-scm.com |

---

## Step 1 – Install Ollama

1. Download from https://ollama.com/download
2. Install and verify:
   ```powershell
   ollama --version
   ```
3. Pull the default model:
   ```powershell
   ollama pull qwen3:8b
   ```

---

## Step 2 – Clone the Repository

```powershell
git clone https://github.com/skirep/Roggy.git
cd Roggy
```

---

## Step 3 – Run Automatic Installer

```powershell
cd rogi
.\install.ps1
```

---

## Step 4 – Configure Environment (optional)

```powershell
cd rogi
# .env is created automatically by install.ps1 if missing
notepad .env
```

Minimum required settings for first run:

```env
DATABASE_PATH=rogi.db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

### Telegram Setup (optional)

1. Chat with [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot: `/newbot`
3. Copy the token and add to `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   TELEGRAM_CHAT_ID=your_numeric_chat_id
   ```
4. To get your chat ID: message [@userinfobot](https://t.me/userinfobot)

### Gmail IMAP Setup

1. Enable IMAP in Gmail settings
2. Create an App Password: Google Account → Security → App Passwords
3. Add to `.env`:
   ```env
   IMAP_ACCOUNTS=[{"label":"Gmail","host":"imap.gmail.com","port":993,"username":"you@gmail.com","password":"your_app_password","ssl":true}]
   ```

### Outlook / Exchange Setup

```env
IMAP_ACCOUNTS=[{"label":"Outlook","host":"outlook.office365.com","port":993,"username":"you@outlook.com","password":"your_password","ssl":true}]
```

---

## Step 5 – Start ROGI

```powershell
cd rogi
.\start.ps1
```

Or with Docker services:

```powershell
.\start.ps1 -UseDocker
```

---

## Step 6 – Verify

- **API Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Open WebUI** (if Docker): http://localhost:3000
- **n8n** (if Docker): http://localhost:5678

---

## Step 7 – Import n8n Workflows (optional)

1. Open n8n at http://localhost:5678
2. Settings → Import from file
3. Import `rogi/workflows/daily_digest.json`
4. Import `rogi/workflows/email_processing.json`
5. Activate the workflows

---

## Stopping ROGI

```powershell
cd rogi
.\stop.ps1
```

---

## Resource Optimisation for ROG Ally

ROGI is designed for low resource consumption:

- **Qwen3 8B** provides stronger responses but uses more RAM
- SQLite has no server overhead
- Background jobs are scheduled (not polling)
- Playwright only launches when shopping features are used
- Docker services are optional — run FastAPI natively for minimal footprint

To check memory usage:
```powershell
Get-Process python, ollama | Select-Object Name, WorkingSet
```

<#
.SYNOPSIS
    Starts the ROGI assistant on a Windows device (ASUS ROG Ally Z1 Extreme).

.DESCRIPTION
    1. Starts Ollama (local LLM)
    2. Starts Docker services (Open WebUI, n8n, backend)
    3. Starts FastAPI backend (if not using Docker)
    4. Verifies database
    5. Verifies Telegram connection
    6. Prints service URLs
#>

param(
    [switch]$UseDocker = $false,
    [switch]$Verbose   = $false
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$defaultModel = "qwen3:8b"
$envFile = Join-Path $ScriptDir ".env"
$modelName = $defaultModel
if (Test-Path $envFile) {
    $modelLine = Get-Content $envFile | Where-Object { $_ -match '^OLLAMA_MODEL=' } | Select-Object -First 1
    if ($modelLine) {
        $modelName = ($modelLine -split '=', 2)[1].Trim()
    }
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ROGI – ROG Intelligent Assistant  " -ForegroundColor Cyan
Write-Host "  Starting up...                    " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# 1. Start Ollama
# ---------------------------------------------------------------------------
Write-Host "`n[1/5] Starting Ollama..." -ForegroundColor Yellow

$ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if ($ollamaProcess) {
    Write-Host "  Ollama already running (PID $($ollamaProcess.Id))" -ForegroundColor Green
} else {
    $ollamaExe = "ollama"
    try {
        Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
        Write-Host "  Ollama started." -ForegroundColor Green
    } catch {
        Write-Warning "  Could not start Ollama. Is it installed? https://ollama.com"
    }
}

# Pull configured model if not present
Write-Host "  Ensuring model $modelName is available..."
& ollama pull $modelName 2>$null
Write-Host "  Model ready." -ForegroundColor Green

# ---------------------------------------------------------------------------
# 2. Start Docker services (optional)
# ---------------------------------------------------------------------------
if ($UseDocker) {
    Write-Host "`n[2/5] Starting Docker services..." -ForegroundColor Yellow
    Push-Location $ScriptDir
    & docker compose up -d
    Pop-Location
    Write-Host "  Docker services started." -ForegroundColor Green
} else {
    Write-Host "`n[2/5] Skipping Docker (use -UseDocker to enable)" -ForegroundColor Gray
}

# ---------------------------------------------------------------------------
# 3. Start FastAPI backend
# ---------------------------------------------------------------------------
Write-Host "`n[3/5] Starting FastAPI backend..." -ForegroundColor Yellow

if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $ScriptDir ".env.example") $envFile
    Write-Warning "  .env not found – copied from .env.example. Please configure it."
}

$backendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    & python -m uvicorn rogi.backend.main:app --host 0.0.0.0 --port 8000 2>&1
} -ArgumentList $ScriptDir

Start-Sleep -Seconds 4
Write-Host "  FastAPI backend started (Job ID: $($backendJob.Id))" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 4. Verify SQLite database
# ---------------------------------------------------------------------------
Write-Host "`n[4/5] Verifying database..." -ForegroundColor Yellow
$dbPath = Join-Path $ScriptDir "rogi.db"
if (Test-Path $dbPath) {
    Write-Host "  Database found: $dbPath" -ForegroundColor Green
} else {
    Write-Host "  Database will be created on first API call." -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# 5. Verify Telegram connection
# ---------------------------------------------------------------------------
Write-Host "`n[5/5] Verifying Telegram..." -ForegroundColor Yellow
try {
    $result = & python -c "
import asyncio, sys
sys.path.insert(0, '.')
from rogi.telegram.bot import RogiBot
from rogi.backend.config import get_settings
s = get_settings()
if not s.telegram_bot_token:
    print('SKIP')
else:
    ok = asyncio.run(RogiBot(s.telegram_bot_token, s.telegram_chat_id).is_healthy())
    print('OK' if ok else 'FAIL')
" 2>$null
    if ($result -eq "OK") {
        Write-Host "  Telegram bot connected." -ForegroundColor Green
    } elseif ($result -eq "SKIP") {
        Write-Host "  Telegram not configured (set TELEGRAM_BOT_TOKEN in .env)" -ForegroundColor Yellow
    } else {
        Write-Warning "  Telegram connection failed. Check TELEGRAM_BOT_TOKEN."
    }
} catch {
    Write-Warning "  Could not verify Telegram."
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "  ROGI is running!" -ForegroundColor Green
Write-Host "  FastAPI:     http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor White
if ($UseDocker) {
    Write-Host "  Open WebUI:  http://localhost:3000" -ForegroundColor White
    Write-Host "  n8n:         http://localhost:5678" -ForegroundColor White
}
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C or run stop.ps1 to shut down." -ForegroundColor Gray

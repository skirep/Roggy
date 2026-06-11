<#
.SYNOPSIS
    Installs all local prerequisites for ROGI.

.DESCRIPTION
    1. Creates/updates Python virtual environment
    2. Installs Python dependencies
    3. Installs Playwright Chromium browser
    4. Ensures .env exists and sets OLLAMA_MODEL
    5. Pulls the Ollama model
#>

param(
    [string]$Model = "qwen3:8b",
    [switch]$SkipPlaywright = $false,
    [switch]$SkipModelPull = $false
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvDir = Join-Path $ScriptDir ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
$venvPip = Join-Path $venvDir "Scripts\pip.exe"
$envFile = Join-Path $ScriptDir ".env"
$envExample = Join-Path $ScriptDir ".env.example"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ROGI – Install setup               " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# 1. Validate required executables
# ---------------------------------------------------------------------------
Write-Host "`n[1/5] Checking required tools..." -ForegroundColor Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found in PATH. Install Python 3.12 first."
}
if ((-not $SkipModelPull) -and -not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    throw "Ollama was not found in PATH. Install Ollama from https://ollama.com/download"
}
Write-Host "  Tool check OK." -ForegroundColor Green

# ---------------------------------------------------------------------------
# 2. Create venv + install dependencies
# ---------------------------------------------------------------------------
Write-Host "`n[2/5] Setting up Python environment..." -ForegroundColor Yellow
Push-Location $ScriptDir
try {
    if (-not (Test-Path $venvPython)) {
        & python -m venv .venv
    }
    & $venvPython -m pip install --upgrade pip
    & $venvPip install -r requirements.txt
    Write-Host "  Python dependencies installed." -ForegroundColor Green
} finally {
    Pop-Location
}

# ---------------------------------------------------------------------------
# 3. Install Playwright browser
# ---------------------------------------------------------------------------
if (-not $SkipPlaywright) {
    Write-Host "`n[3/5] Installing Playwright Chromium..." -ForegroundColor Yellow
    & $venvPython -m playwright install chromium
    Write-Host "  Playwright Chromium installed." -ForegroundColor Green
} else {
    Write-Host "`n[3/5] Skipping Playwright install." -ForegroundColor Gray
}

# ---------------------------------------------------------------------------
# 4. Ensure .env and model config
# ---------------------------------------------------------------------------
Write-Host "`n[4/5] Configuring .env..." -ForegroundColor Yellow
if (-not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
}
$envContent = Get-Content $envFile -Raw
if ($envContent -match "(?m)^OLLAMA_MODEL=") {
    $envContent = $envContent -replace "(?m)^OLLAMA_MODEL=.*$", "OLLAMA_MODEL=$Model"
} else {
    if (-not $envContent.EndsWith("`n")) {
        $envContent += "`n"
    }
    $envContent += "OLLAMA_MODEL=$Model`n"
}
Set-Content -Path $envFile -Value $envContent -NoNewline
Write-Host "  .env ready with OLLAMA_MODEL=$Model" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 5. Pull Ollama model
# ---------------------------------------------------------------------------
if (-not $SkipModelPull) {
    Write-Host "`n[5/5] Pulling Ollama model ($Model)..." -ForegroundColor Yellow
    & ollama pull $Model
    Write-Host "  Ollama model ready." -ForegroundColor Green
} else {
    Write-Host "`n[5/5] Skipping model pull." -ForegroundColor Gray
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "  Install completed." -ForegroundColor Green
Write-Host "  Next step: .\start.ps1" -ForegroundColor White
Write-Host "=====================================" -ForegroundColor Cyan

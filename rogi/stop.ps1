<#
.SYNOPSIS
    Gracefully stops all ROGI services.
#>

param(
    [switch]$UseDocker = $false
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ROGI – Stopping services...       " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ---------------------------------------------------------------------------
# Stop FastAPI background jobs
# ---------------------------------------------------------------------------
Write-Host "`nStopping FastAPI background jobs..." -ForegroundColor Yellow
Get-Job | Where-Object { $_.State -ne "Completed" } | ForEach-Object {
    Stop-Job -Job $_
    Remove-Job -Job $_
    Write-Host "  Stopped job $($_.Id)" -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# Stop Docker services
# ---------------------------------------------------------------------------
if ($UseDocker) {
    Write-Host "`nStopping Docker services..." -ForegroundColor Yellow
    Push-Location $ScriptDir
    & docker compose down
    Pop-Location
    Write-Host "  Docker services stopped." -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# Stop Ollama (optional – it may be used by other apps)
# ---------------------------------------------------------------------------
$ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if ($ollamaProcess) {
    Write-Host "`nStopping Ollama..." -ForegroundColor Yellow
    Stop-Process -Name "ollama" -Force
    Write-Host "  Ollama stopped." -ForegroundColor Green
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "  ROGI stopped cleanly." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

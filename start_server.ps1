# Script khởi động Flask server cho PowerShell
# Chạy: .\start_server.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " KHOI DONG FLASK SERVER - ADMISSION SYSTEM" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Change to backend directory
Set-Location -Path "$PSScriptRoot\backend"

Write-Host "[1/3] Checking Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[2/3] Setting environment variables..." -ForegroundColor Yellow
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = "1"

Write-Host ""
Write-Host "[3/3] Starting Flask server..." -ForegroundColor Yellow
Write-Host "Server will run at: " -NoNewline
Write-Host "http://localhost:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Start server
python app.py

Read-Host "Press Enter to exit"

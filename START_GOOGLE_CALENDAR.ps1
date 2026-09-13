$ErrorActionPreference = "Stop"
Write-Host "=== LIVE Google Calendar MCP Agent ==="

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Virtual environment not found. Running setup_windows.ps1..."
    & .\setup_windows.ps1
}

if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "Created .env. Paste GROQ_API_KEY into .env, then run this script again."
    exit 1
}

if (-not (Test-Path "credentials.json")) {
    Write-Host ""
    Write-Host "credentials.json is missing." -ForegroundColor Yellow
    Write-Host "Create a Google OAuth Desktop App, download its JSON, rename it credentials.json,"
    Write-Host "and place it in this project folder. See docs\GOOGLE_CALENDAR_SETUP.md."
    exit 2
}

Write-Host ""
Write-Host "1/3 Checking configuration..."
& .\.venv\Scripts\python.exe scripts\check_setup.py

Write-Host ""
Write-Host "2/3 Authorizing Google Calendar..."
& .\.venv\Scripts\python.exe scripts\google_auth.py

Write-Host ""
Write-Host "3/3 Starting LIVE interactive Calendar Agent..."
& .\.venv\Scripts\python.exe src\app.py --interactive

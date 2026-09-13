$ErrorActionPreference = "Stop"
Write-Host "=== Day03 setup: Groq + REAL MCP + LIVE Google Calendar ==="

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "Created .env from .env.example"
}

Write-Host ""
Write-Host "Setup complete. Next:"
Write-Host "1) Open .env and set GROQ_API_KEY=gsk_..."
Write-Host "2) Put your Google OAuth Desktop App file at .\credentials.json"
Write-Host "3) Run: .\START_GOOGLE_CALENDAR.ps1"
Write-Host ""
Write-Host "The first OAuth run opens your browser, lets you sign in to Google, and creates token.json."
Write-Host "Use --interactive for real Calendar. --all stays blocked by default to protect your personal calendar."

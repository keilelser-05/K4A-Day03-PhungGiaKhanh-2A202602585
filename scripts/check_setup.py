"""Environment checker. It never prints API keys or OAuth tokens."""

from pathlib import Path
import importlib.util
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

mods = ["openai", "mcp", "googleapiclient", "google_auth_oauthlib", "dotenv"]
for mod in mods:
    print(("✅" if importlib.util.find_spec(mod) else "❌"), mod)

provider = os.getenv("LLM_PROVIDER", "groq").lower()
print("LLM provider:", provider)
if provider == "groq":
    key = os.getenv("GROQ_API_KEY", "")
    ok = bool(key and key != "your_groq_api_key_here")
    print("✅ GROQ_API_KEY set" if ok else "⚠️ GROQ_API_KEY missing/placeholder")
    print("Groq model:", os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"))
elif provider == "openai":
    key = os.getenv("OPENAI_API_KEY", "")
    ok = bool(key and key != "your_openai_api_key_here")
    print("✅ OPENAI_API_KEY set" if ok else "⚠️ OPENAI_API_KEY missing/placeholder")
    print("OpenAI model:", os.getenv("OPENAI_MODEL", "gpt-5.6"))
else:
    print("❌ Unsupported LLM_PROVIDER")

backend = os.getenv("CALENDAR_BACKEND", "google").lower()
print("Calendar backend:", backend)
if backend == "google":
    creds_raw = Path(os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json"))
    token_raw = Path(os.getenv("GOOGLE_TOKEN_FILE", "token.json"))
    creds = creds_raw if creds_raw.is_absolute() else ROOT / creds_raw
    token = token_raw if token_raw.is_absolute() else ROOT / token_raw
    print("✅ Google OAuth credentials found" if creds.exists() else f"⚠️ Missing OAuth file: {creds}")
    print("✅ Google account authorized (token.json exists)" if token.exists() else "ℹ️ Google account not authorized yet — run scripts\\google_auth.py")
    print("Calendar ID:", os.getenv("GOOGLE_CALENDAR_ID", "primary"))
    print("Timezone:", os.getenv("GOOGLE_TIMEZONE", "Asia/Ho_Chi_Minh"))
    print("OAuth scope:", os.getenv("GOOGLE_CALENDAR_SCOPE", "https://www.googleapis.com/auth/calendar.events"))

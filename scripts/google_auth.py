"""Authorize the user's real Google Calendar and save token.json."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from calendar_client import get_calendar_service


def main() -> int:
    credentials_name = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    credentials_path = Path(credentials_name)
    if not credentials_path.is_absolute():
        credentials_path = ROOT / credentials_path

    if not credentials_path.exists():
        print("❌ Chưa có credentials.json của Google OAuth Desktop App.")
        print(f"   Hãy đặt file tại: {credentials_path}")
        print("   Xem docs/GOOGLE_CALENDAR_SETUP.md để tạo file này.")
        return 2

    service = get_calendar_service()
    now = datetime.now(timezone.utc)
    result = (
        service.events()
        .list(
            calendarId=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
            timeMin=now.isoformat(),
            timeMax=(now + timedelta(days=7)).isoformat(),
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    print("✅ Google OAuth OK — Calendar events permission granted")
    print("Calendar ID:", os.getenv("GOOGLE_CALENDAR_ID", "primary"))
    print("Token saved to:", ROOT / os.getenv("GOOGLE_TOKEN_FILE", "token.json"))

    items = result.get("items", [])
    print(f"Upcoming events in next 7 days: {len(items)}")
    for event in items[:5]:
        start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", ""))
        print(f"  - {start} | {event.get('summary', '(không tiêu đề)')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

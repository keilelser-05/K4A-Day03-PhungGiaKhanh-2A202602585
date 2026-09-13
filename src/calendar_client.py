"""Google Calendar backend used by the MCP tools.

CALENDAR_BACKEND=google -> real Google Calendar API through OAuth 2.0 (default).
CALENDAR_BACKEND=mock   -> optional deterministic in-memory data for lab tests.
"""

from __future__ import annotations

import os
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]

_INITIAL_MOCK_EVENTS: List[Dict[str, Any]] = [
    {"id":"mock-deep-learning-001","summary":"Deep Learning","description":"Buổi học Deep Learning","start":{"dateTime":"2026-09-15T14:00:00+07:00","timeZone":"Asia/Ho_Chi_Minh"},"end":{"dateTime":"2026-09-15T16:00:00+07:00","timeZone":"Asia/Ho_Chi_Minh"}},
    {"id":"mock-ai-project-001","summary":"AI Project Meeting","description":"Họp nhóm dự án AI","start":{"dateTime":"2026-09-16T09:00:00+07:00","timeZone":"Asia/Ho_Chi_Minh"},"end":{"dateTime":"2026-09-16T10:00:00+07:00","timeZone":"Asia/Ho_Chi_Minh"}},
]
MOCK_EVENTS: List[Dict[str, Any]] = deepcopy(_INITIAL_MOCK_EVENTS)

def backend_name() -> str:
    return os.getenv("CALENDAR_BACKEND", "google").strip().lower()

def _timezone() -> str:
    return os.getenv("GOOGLE_TIMEZONE", "Asia/Ho_Chi_Minh")

def _calendar_id() -> str:
    return os.getenv("GOOGLE_CALENDAR_ID", "primary")

def _resolve_project_file(env_name: str, default: str) -> Path:
    raw = Path(os.getenv(env_name, default))
    return raw if raw.is_absolute() else PROJECT_ROOT / raw

def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def reset_mock_calendar() -> Dict[str, Any]:
    MOCK_EVENTS.clear(); MOCK_EVENTS.extend(deepcopy(_INITIAL_MOCK_EVENTS)); return {"reset": True, "count": len(MOCK_EVENTS)}

def get_calendar_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    scopes = [os.getenv("GOOGLE_CALENDAR_SCOPE", "https://www.googleapis.com/auth/calendar.events")]
    credentials_file = _resolve_project_file("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    token_file = _resolve_project_file("GOOGLE_TOKEN_FILE", "token.json")
    creds = Credentials.from_authorized_user_file(str(token_file), scopes) if token_file.exists() else None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_file.exists():
                raise FileNotFoundError(f"Thiếu Google OAuth credentials tại {credentials_file}.")
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), scopes)
            creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json(), encoding="utf-8")
    return build("calendar", "v3", credentials=creds)

def list_events(time_min: str, time_max: str) -> List[Dict[str, Any]]:
    if backend_name() == "mock":
        start_bound, end_bound = _parse_iso(time_min), _parse_iso(time_max)
        return [deepcopy(e) for e in MOCK_EVENTS if e.get("start",{}).get("dateTime") and start_bound <= _parse_iso(e["start"]["dateTime"]) <= end_bound]
    service = get_calendar_service()
    result = service.events().list(calendarId=_calendar_id(), timeMin=time_min, timeMax=time_max, singleEvents=True, orderBy="startTime").execute()
    return [{"id":e.get("id"),"summary":e.get("summary",""),"description":e.get("description",""),"start":e.get("start",{}),"end":e.get("end",{}),"htmlLink":e.get("htmlLink")} for e in result.get("items", [])]

def create_event(summary: str, start_datetime: str, end_datetime: str, description: str = "") -> Dict[str, Any]:
    body={"summary":summary,"description":description,"start":{"dateTime":start_datetime,"timeZone":_timezone()},"end":{"dateTime":end_datetime,"timeZone":_timezone()}}
    if backend_name()=="mock":
        event={"id":f"mock-{uuid.uuid4().hex[:10]}", **body}; MOCK_EVENTS.append(event); return deepcopy(event)
    created=get_calendar_service().events().insert(calendarId=_calendar_id(), body=body).execute()
    return {"id":created.get("id"),"summary":created.get("summary"),"description":created.get("description",""),"start":created.get("start"),"end":created.get("end"),"htmlLink":created.get("htmlLink")}

def update_event(event_id: str, summary: Optional[str]=None, start_datetime: Optional[str]=None, end_datetime: Optional[str]=None, description: Optional[str]=None) -> Dict[str, Any]:
    if backend_name()=="mock":
        for event in MOCK_EVENTS:
            if event["id"]==event_id:
                if summary is not None: event["summary"]=summary
                if description is not None: event["description"]=description
                if start_datetime is not None: event["start"]={"dateTime":start_datetime,"timeZone":_timezone()}
                if end_datetime is not None: event["end"]={"dateTime":end_datetime,"timeZone":_timezone()}
                return deepcopy(event)
        raise ValueError(f"Không tìm thấy event_id={event_id}")
    service=get_calendar_service(); event=service.events().get(calendarId=_calendar_id(), eventId=event_id).execute()
    if summary is not None: event["summary"]=summary
    if description is not None: event["description"]=description
    if start_datetime is not None: event["start"]={"dateTime":start_datetime,"timeZone":_timezone()}
    if end_datetime is not None: event["end"]={"dateTime":end_datetime,"timeZone":_timezone()}
    updated=service.events().update(calendarId=_calendar_id(), eventId=event_id, body=event).execute()
    return {"id":updated.get("id"),"summary":updated.get("summary"),"description":updated.get("description",""),"start":updated.get("start"),"end":updated.get("end"),"htmlLink":updated.get("htmlLink")}

def delete_event(event_id: str) -> Dict[str, Any]:
    if backend_name()=="mock":
        for i,event in enumerate(MOCK_EVENTS):
            if event["id"]==event_id:
                removed=MOCK_EVENTS.pop(i); return {"deleted":True,"event_id":event_id,"summary":removed.get("summary","")}
        raise ValueError(f"Không tìm thấy event_id={event_id}")
    service=get_calendar_service(); service.events().delete(calendarId=_calendar_id(), eventId=event_id).execute(); return {"deleted":True,"event_id":event_id}

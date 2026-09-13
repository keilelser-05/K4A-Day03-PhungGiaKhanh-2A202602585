"""Business functions exposed by the real MCP server."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from calendar_client import create_event, delete_event, list_events, reset_mock_calendar, update_event


def calendar_list_events(time_min: str, time_max: str) -> List[Dict[str, Any]]:
    """List Google Calendar events in an ISO-8601 time range."""
    return list_events(time_min=time_min, time_max=time_max)


def calendar_create_event(summary: str, start_datetime: str, end_datetime: str, description: str = "") -> Dict[str, Any]:
    """Create a Google Calendar event with ISO-8601 start/end datetimes."""
    return create_event(summary=summary, start_datetime=start_datetime, end_datetime=end_datetime, description=description)


def calendar_update_event(event_id: str, summary: Optional[str] = None, start_datetime: Optional[str] = None, end_datetime: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """Update an event by event_id. Omitted/null fields are kept unchanged."""
    return update_event(event_id=event_id, summary=summary, start_datetime=start_datetime, end_datetime=end_datetime, description=description)


def calendar_delete_event(event_id: str) -> Dict[str, Any]:
    """Delete a Google Calendar event by event_id."""
    return delete_event(event_id=event_id)


def calendar_reset_mock() -> Dict[str, Any]:
    """Reset mock Calendar data. Intended only for deterministic lab testing."""
    return reset_mock_calendar()

"""REAL MCP server for Google Calendar tools.

Transport: stdio by default. The host launches this file as a child process
and communicates through the official Model Context Protocol Python SDK.
"""

from mcp.server import MCPServer

from tools import (
    calendar_create_event,
    calendar_delete_event,
    calendar_list_events,
    calendar_reset_mock,
    calendar_update_event,
)

mcp = MCPServer(
    "Google Calendar MCP",
    instructions=(
        "Tools read/create/update/delete Google Calendar events. "
        "Never invent event IDs; list events first when the caller only knows a title/time."
    ),
)

mcp.tool()(calendar_list_events)
mcp.tool()(calendar_create_event)
mcp.tool()(calendar_update_event)
mcp.tool()(calendar_delete_event)
mcp.tool()(calendar_reset_mock)

if __name__ == "__main__":
    mcp.run()

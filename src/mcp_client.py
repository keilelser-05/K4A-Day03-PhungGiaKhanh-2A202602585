"""Real MCP stdio client bridge used by the OpenAI-compatible host application."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp import Client, StdioServerParameters


class CalendarMCPClient:
    """Launch mcp_server.py as a subprocess and speak MCP over stdio."""

    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parents[1]
        self.server_file = Path(__file__).with_name("mcp_server.py")
        self._context: Optional[Client] = None
        self.client: Optional[Client] = None

    async def __aenter__(self) -> "CalendarMCPClient":
        params = StdioServerParameters(command=sys.executable, args=[str(self.server_file)], env=os.environ.copy())
        self._context = Client(params)
        self.client = await self._context.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._context is not None:
            await self._context.__aexit__(exc_type, exc, tb)
        self.client = None
        self._context = None

    def _require_client(self) -> Client:
        if self.client is None:
            raise RuntimeError("MCP client chưa được kết nối. Hãy dùng 'async with CalendarMCPClient()'.")
        return self.client

    async def list_tools(self) -> List[Any]:
        result = await self._require_client().list_tools()
        return list(result.tools)

    async def openai_tools(self, include_test_tools: bool = False) -> List[Dict[str, Any]]:
        tools = await self.list_tools()
        output: List[Dict[str, Any]] = []
        for tool in tools:
            if not include_test_tools and tool.name == "calendar_reset_mock":
                continue
            output.append({"type": "function", "name": tool.name, "description": tool.description or "", "parameters": tool.input_schema})
        return output

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        result = await self._require_client().call_tool(name, arguments)
        text_blocks: List[str] = []
        for block in result.content:
            text = getattr(block, "text", None)
            if text is not None:
                text_blocks.append(text)
        if result.is_error:
            return {"status": "ERROR", "data": result.structured_content, "content": text_blocks}
        return {"status": "SUCCESS", "data": result.structured_content, "content": text_blocks}

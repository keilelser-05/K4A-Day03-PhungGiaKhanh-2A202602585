"""OpenAI-compatible Responses API providers for the MCP ReAct loop."""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

@dataclass
class FunctionCall:
    name: str
    arguments: Dict[str, Any]
    call_id: str

@dataclass
class ResponseState:
    response: Any
    history: List[Dict[str, Any]] = field(default_factory=list)

def _output_items_for_history(response: Any) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for item in getattr(response, "output", []) or []:
        if hasattr(item, "model_dump"):
            payload = item.model_dump(exclude_none=True)
        elif isinstance(item, dict):
            payload = dict(item)
        else:
            continue
        items.append(payload)
    return items

class OpenAICompatibleResponsesProvider:
    def __init__(self, *, provider_name: str, api_key: str, model: str, base_url: str | None = None) -> None:
        if not api_key or api_key.startswith("your_"):
            raise RuntimeError(f"Thiếu API key cho provider '{provider_name}'.")
        self.provider_name = provider_name
        self.model_name = model
        self.base_url = base_url
        kwargs: Dict[str, Any] = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)

    async def _create_response(self, history: List[Dict[str, Any]], tools: List[Dict[str, Any]], instructions: str) -> Any:
        return await asyncio.to_thread(self.client.responses.create, model=self.model_name, instructions=instructions, input=history, tools=tools, tool_choice="auto")

    async def start(self, user_input: str, tools: List[Dict[str, Any]], instructions: str) -> ResponseState:
        history = [{"role": "user", "content": user_input}]
        response = await self._create_response(history, tools, instructions)
        return ResponseState(response=response, history=history)

    async def continue_after_tools(self, state: ResponseState, tool_outputs: List[Dict[str, Any]], tools: List[Dict[str, Any]], instructions: str) -> ResponseState:
        history = list(state.history)
        history.extend(_output_items_for_history(state.response))
        history.extend(tool_outputs)
        response = await self._create_response(history, tools, instructions)
        return ResponseState(response=response, history=history)

    @staticmethod
    def function_calls(state: ResponseState) -> List[FunctionCall]:
        calls: List[FunctionCall] = []
        for item in getattr(state.response, "output", []) or []:
            if getattr(item, "type", None) != "function_call":
                continue
            raw_args = getattr(item, "arguments", "{}") or "{}"
            try:
                parsed = json.loads(raw_args)
            except json.JSONDecodeError:
                parsed = {}
            calls.append(FunctionCall(name=getattr(item, "name", ""), arguments=parsed, call_id=getattr(item, "call_id", "")))
        return calls

    @staticmethod
    def output_text(state: ResponseState) -> str:
        return (getattr(state.response, "output_text", "") or "").strip()

class GroqResponsesProvider(OpenAICompatibleResponsesProvider):
    def __init__(self) -> None:
        super().__init__(provider_name="groq", api_key=os.getenv("GROQ_API_KEY", ""), model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"), base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"))

class OpenAIResponsesProvider(OpenAICompatibleResponsesProvider):
    def __init__(self) -> None:
        super().__init__(provider_name="openai", api_key=os.getenv("OPENAI_API_KEY", ""), model=os.getenv("OPENAI_MODEL", "gpt-5.6"), base_url=os.getenv("OPENAI_BASE_URL") or None)

def get_provider() -> OpenAICompatibleResponsesProvider:
    name = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    if name == "groq":
        return GroqResponsesProvider()
    if name == "openai":
        return OpenAIResponsesProvider()
    raise RuntimeError(f"LLM_PROVIDER='{name}' chưa được hỗ trợ. Hãy dùng 'groq' hoặc 'openai'.")

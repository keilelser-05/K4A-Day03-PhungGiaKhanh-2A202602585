"""Groq/OpenAI Responses API host -> REAL MCP stdio client -> Google Calendar MCP server."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

from mcp_client import CalendarMCPClient
from prompts import MAX_ITERATIONS, REACT_AGENT_SYSTEM_PROMPT
from providers import OpenAICompatibleResponsesProvider, get_provider


def load_test_cases() -> List[Dict[str, Any]]:
    with (PROJECT_ROOT / "config" / "test_cases.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def _sanitize_trace(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _sanitize_trace(v) for k, v in value.items() if k not in {"htmlLink"}}
    if isinstance(value, list):
        return [_sanitize_trace(v) for v in value]
    return value


def save_waterfall_trace(trace_data: List[Dict[str, Any]], *, append: bool = False) -> Path:
    path = PROJECT_ROOT / "docs" / "trace_waterfall.json"
    clean = _sanitize_trace(trace_data)
    if append and path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
        except (json.JSONDecodeError, OSError):
            existing = []
        clean = existing + clean
    path.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


async def run_react_agent(user_query: str, provider: OpenAICompatibleResponsesProvider, mcp: CalendarMCPClient) -> Dict[str, Any]:
    print(f"\n🤖 {user_query}")
    openai_tools = await mcp.openai_tools()
    trace: List[Dict[str, Any]] = []
    started = time.perf_counter()
    state = await provider.start(user_query, openai_tools, REACT_AGENT_SYSTEM_PROMPT)

    for step in range(1, MAX_ITERATIONS + 1):
        calls = provider.function_calls(state)
        if not calls:
            final = provider.output_text(state)
            trace.append({"step": step, "action_type": "FINAL_ANSWER", "output": final, "elapsed_ms": round((time.perf_counter()-started)*1000,2)})
            print(f"🏁 {final}")
            return {"final": final, "trace": trace}

        tool_outputs: List[Dict[str, Any]] = []
        for call in calls:
            print(f"🛠️ MCP tool: {call.name}({call.arguments})")
            tool_started = time.perf_counter()
            observation = await mcp.call_tool(call.name, call.arguments)
            tool_ms = round((time.perf_counter() - tool_started) * 1000, 2)
            print(f"👁️ {json.dumps(observation, ensure_ascii=False)}")
            trace.append({"step": step, "action_type": "MCP_TOOL_CALL", "tool_name": call.name, "arguments": call.arguments, "observation": observation, "tool_latency_ms": tool_ms})
            tool_outputs.append({"type": "function_call_output", "call_id": call.call_id, "output": json.dumps(observation, ensure_ascii=False)})

        state = await provider.continue_after_tools(state=state, tool_outputs=tool_outputs, tools=openai_tools, instructions=REACT_AGENT_SYSTEM_PROMPT)

    final = "Agent dừng vì vượt MAX_ITERATIONS."
    trace.append({"step": MAX_ITERATIONS + 1, "action_type": "STOP", "output": final})
    print(f"⛔ {final}")
    return {"final": final, "trace": trace}


def actual_tool_sequence(trace: List[Dict[str, Any]]) -> List[str]:
    return [x["tool_name"] for x in trace if x.get("action_type") == "MCP_TOOL_CALL"]


async def mcp_smoke_test() -> int:
    async with CalendarMCPClient() as mcp:
        tools = await mcp.list_tools()
        names = [t.name for t in tools]
        print("✅ REAL MCP connected")
        print("Protocol tools:", ", ".join(names))
        observation = await mcp.call_tool("calendar_list_events", {"time_min": "2026-09-15T08:00:00+07:00", "time_max": "2026-09-15T18:00:00+07:00"})
        print("✅ MCP call_tool result:")
        print(json.dumps(observation, ensure_ascii=False, indent=2))
    return 0


async def run_all(provider: OpenAICompatibleResponsesProvider) -> int:
    tests = load_test_cases()
    backend = os.getenv("CALENDAR_BACKEND", "google").lower()
    if backend == "google" and os.getenv("ALLOW_GOOGLE_WRITE_TESTS", "false").lower() != "true":
        raise RuntimeError("--all có test tạo/sửa/xóa lịch thật. Nếu bạn dùng Calendar test riêng và chấp nhận ghi dữ liệu, hãy đặt ALLOW_GOOGLE_WRITE_TESTS=true.")
    all_trace: List[Dict[str, Any]] = []
    passed = 0
    async with CalendarMCPClient() as mcp:
        if backend == "mock":
            await mcp.call_tool("calendar_reset_mock", {})
        for tc in tests:
            print("\n" + "=" * 72)
            print(f"🧪 {tc['id']} | {tc['type']} | {tc['complexity']}")
            result = await run_react_agent(tc["question"], provider, mcp)
            sequence = actual_tool_sequence(result["trace"])
            expected = tc.get("expected_tools", [])
            ok = sequence == expected and bool(result["final"])
            print(f"Expected tools: {expected}")
            print(f"Actual tools:   {sequence}")
            print("✅ PASS" if ok else "❌ CHECK")
            if ok:
                passed += 1
            for item in result["trace"]:
                item["test_id"] = tc["id"]
            all_trace.extend(result["trace"])
    path = save_waterfall_trace(all_trace)
    print(f"\n📊 Trace: {path}")
    print(f"🎯 Test summary: {passed}/{len(tests)}")
    return 0 if passed == len(tests) else 1


async def interactive(provider: OpenAICompatibleResponsesProvider) -> int:
    async with CalendarMCPClient() as mcp:
        print("Gõ 'exit' để thoát.")
        while True:
            text = (await asyncio.to_thread(input, "👤 Bạn: ")).strip()
            if not text or text.lower() in {"exit", "quit"}:
                return 0
            result = await run_react_agent(text, provider, mcp)
            save_waterfall_trace(result["trace"], append=True)


async def async_main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--mcp-smoke", action="store_true")
    args = parser.parse_args()
    print("=" * 72)
    print("DAY 03 | GROQ/OPENAI RESPONSES API + REAL MCP + GOOGLE CALENDAR")
    print("=" * 72)
    print("Calendar backend:", os.getenv("CALENDAR_BACKEND", "google"))
    if args.mcp_smoke:
        return await mcp_smoke_test()
    provider = get_provider()
    print("LLM provider:", provider.provider_name)
    print("LLM model:", provider.model_name)
    if args.all:
        return await run_all(provider)
    if args.interactive:
        return await interactive(provider)
    print("Dùng: --mcp-smoke | --all | --interactive")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(async_main()))
    except KeyboardInterrupt:
        raise SystemExit(130)
    except BaseExceptionGroup as exc:
        import traceback
        print("\n❌ ExceptionGroup chi tiết:", file=sys.stderr)
        traceback.print_exception(exc)
        raise SystemExit(1)
    except Exception as exc:
        import traceback
        print(f"\n❌ {type(exc).__name__}: {exc}", file=sys.stderr)
        traceback.print_exception(exc)
        raise SystemExit(1)

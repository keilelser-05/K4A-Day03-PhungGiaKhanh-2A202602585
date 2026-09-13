# K4-DAY03-PhungGiaKhanh-2A202602585

**Bài Lab 3 — Chatbot vs ReAct Agent (MCP Enhanced)**  
Học viên: **Phùng Gia Khánh** — **2A202602585**

## Chủ đề

ReAct Agent quản lý **Google Calendar thật** qua **Model Context Protocol (MCP)**. Agent có thể đọc, tạo, sửa và xóa sự kiện; các tác vụ sửa/xóa theo ngôn ngữ tự nhiên thực hiện multi-step `list → lấy event_id → update/delete`.

## Kiến trúc

```text
User → Groq/OpenAI-compatible LLM → ReAct loop → MCP Client
     → REAL MCP Server (stdio) → Google Calendar API (OAuth)
```

Project sử dụng official Python MCP SDK. MCP Server chạy độc lập dưới dạng subprocess qua stdio.

## Artifacts nộp bài

- `src/app.py` — ReAct loop + waterfall trace
- `src/mcp_server.py` — MCP Server thật
- `src/mcp_client.py` — MCP Client thật
- `src/tools.py` — Calendar tools
- `config/test_cases.json` — 5 test cases
- `docs/trace_waterfall.json` — trace từ Google Calendar thật
- `docs/trace_eval.md` — báo cáo nghiệm thu

## Quickstart

Python 3.10–3.12.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Điền API key của riêng bạn vào `.env`. Để chạy Google Calendar thật, tạo OAuth Desktop Client và đặt file cục bộ thành `credentials.json`, sau đó:

```powershell
python scripts\google_auth.py
python src\app.py --interactive
```

Test MCP transport độc lập:

```powershell
python src\app.py --mcp-smoke
```

Test 5 cases (khuyến nghị `CALENDAR_BACKEND=mock` để deterministic và không tác động lịch cá nhân):

```powershell
python src\app.py --all
```

## Bảo mật

**Không có secret nào trong repo nộp bài.** `.gitignore` loại trừ `.env`, `credentials.json`, `token.json`, `.venv/`. File OAuth/API key phải được tạo cục bộ bởi người chạy.

## Kết quả

- 5/5 test cases PASS trên Groq API thật + MCP thật + Calendar mock deterministic.
- Google Calendar thật đã nghiệm thu end-to-end: list/create/update/delete SUCCESS.
- Multi-step ReAct đã xác minh: `calendar_list_events → calendar_update_event` và `calendar_list_events → calendar_delete_event`.

Xem chi tiết tại `docs/trace_eval.md`.

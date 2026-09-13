# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3

> **Họ và Tên Học viên:** Phùng Gia Khánh  
> **Mã Sinh Viên / Mã Học viên:** 2A202602585  
> **Chủ đề Lựa chọn:** Đề tài mở — ReAct Agent quản lý Google Calendar thật qua Model Context Protocol (MCP)

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình |
| :--- | :---: | :--- |
| **Multi-step Reasoning** | **5/5** | Yêu cầu sửa/xóa theo tên và thời gian cần tra cứu sự kiện trước, lấy `event_id`, sau đó mới thực hiện thao tác tiếp theo. |
| **Tool Interaction** | **5/5** | Agent phải gọi MCP tools để đọc/tạo/sửa/xóa sự kiện trên Google Calendar API thật. |
| **Dynamic Decision** | **5/5** | Bước tiếp theo phụ thuộc trực tiếp vào Observation: có tìm thấy event hay không, event ID nào được trả về. |
| **Long Horizon Goal** | **4/5** | Agent giữ mục tiêu xuyên suốt nhiều lượt tool call cho đến khi hoàn tất thao tác, nhưng tác vụ vẫn có horizon tương đối ngắn. |
| **TỔNG ĐIỂM AGENTIC FIT** | **19/20** | **> 12/20 — phù hợp triển khai Agentic System.** |

## 2. TOOL SPECS & KIẾN TRÚC MCP

MCP Server công bố các tool chính:

- `calendar_list_events(time_min, time_max)`
- `calendar_create_event(summary, start_datetime, end_datetime, description)`
- `calendar_update_event(event_id, ...)`
- `calendar_delete_event(event_id)`

```text
User
  ↓
Groq LLM (openai/gpt-oss-20b, real API)
  ↓ native function/tool calling
ReAct loop
  ↓
MCP Client (official Python MCP SDK)
  ↓ stdio / MCP protocol
MCP Server subprocess
  ↓
Google Calendar API (OAuth)
  ↓
Google Calendar thật
```

Project dùng **MCP SDK thật qua stdio**, không gọi trực tiếp Calendar function từ Agent host.

## 3. WATERFALL TRACE — BẰNG CHỨNG CHẠY THẬT

Bằng chứng trong `docs/trace_waterfall.json` được lấy từ phiên chạy thật với:

- LLM API thật: **Groq / `openai/gpt-oss-20b`**
- MCP transport thật: **stdio**
- Calendar backend thật: **Google Calendar API + OAuth**

Trace multi-step tiêu biểu:

```json
{
  "step": 1,
  "action_type": "MCP_TOOL_CALL",
  "tool_name": "calendar_list_events",
  "observation": {"status": "SUCCESS"}
}
{
  "step": 2,
  "action_type": "MCP_TOOL_CALL",
  "tool_name": "calendar_update_event",
  "observation": {"status": "SUCCESS"}
}
{
  "step": 3,
  "action_type": "FINAL_ANSWER",
  "output": "Sự kiện TEST MCP đã được dời sang 20/09/2026, 21:00–21:30."
}
```

Chuỗi này chứng minh Observation bước 1 cung cấp `event_id` thật cho Action bước 2. Trace delete cũng thể hiện `calendar_list_events → calendar_delete_event → SUCCESS`.

> `htmlLink` và thông tin xác thực đã được loại khỏi trace nộp bài để không làm lộ thông tin tài khoản.

## 4. KẾT QUẢ NGHIỆM THU

- [x] MCP Client kết nối MCP Server thật thành công.
- [x] LLM API thật hoạt động và native tool calling hoạt động.
- [x] Bộ 5 test cases đã chạy **5/5 PASS** với Groq API thật + MCP thật + Calendar mock deterministic.
- [x] Đã nghiệm thu riêng Google Calendar thật: list/create/update/delete đều SUCCESS qua OAuth.
- [x] Multi-step reasoning đã chạy đúng: `list → update` và `list → delete`.
- [x] `docs/trace_waterfall.json` chứa bằng chứng từ phiên Google Calendar thật.
- [x] `.gitignore` loại `.env`, `credentials.json`, `token.json`, `.venv`.

| Test | Expected tools | Kết quả đã nghiệm thu |
|---|---|---|
| TC01 direct query | `[]` | PASS |
| TC02 list calendar | `calendar_list_events` | PASS |
| TC03 create event | `calendar_create_event` | PASS |
| TC04 multi-step | `calendar_list_events → calendar_update_event` | PASS |
| TC05 edge case | `calendar_list_events` | PASS |

**Tổng: 5/5 test cases.**

## 5. GHI CHÚ BẢO MẬT KHI NỘP

Không commit `.env`, `credentials.json`, `token.json`, `.venv/`.

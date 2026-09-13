# Kết nối Google Calendar thật (OAuth Desktop App)

Project mặc định dùng `CALENDAR_BACKEND=google`. Các MCP tool `calendar_list_events`, `calendar_create_event`, `calendar_update_event`, `calendar_delete_event` sẽ thao tác trực tiếp với Calendar được chỉ định bởi `GOOGLE_CALENDAR_ID=primary`.

## 1. Tạo OAuth Desktop credential

1. Mở Google Cloud Console và tạo/chọn một project.
2. Enable **Google Calendar API**.
3. Vào **Google Auth Platform** và cấu hình Branding/Audience.
4. Tạo OAuth Client ID với **Application type = Desktop app**.
5. Download JSON.
6. Đổi tên file thành `credentials.json`.
7. Đặt nó ở root project, cạnh `.env`.

```text
project/
├── .env
├── credentials.json
├── START_GOOGLE_CALENDAR.ps1
├── src/
└── scripts/
```

## 2. Scope

Project dùng:

```text
https://www.googleapis.com/auth/calendar.events
```

Scope này cho phép xem và chỉnh sửa event trên Calendar mà tài khoản có quyền truy cập.

## 3. Đăng nhập Google

```powershell
.\.venv\Scripts\python.exe scripts\google_auth.py
```

Lần đầu, trình duyệt mở ra để bạn chọn tài khoản và cấp quyền. Sau đó project lưu `token.json` cục bộ.

**Không đưa `.env`, `credentials.json` hoặc `token.json` lên GitHub.**

## 4. Cách chạy dễ nhất

```powershell
.\START_GOOGLE_CALENDAR.ps1
```

## 5. Test an toàn trên Calendar thật

```text
Xem các lịch của tôi trong 7 ngày tới.
Tạo sự kiện TEST MCP ngày 20/09/2026 từ 20:00 đến 20:30.
Dời sự kiện TEST MCP ngày 20/09/2026 sang 21:00, giữ nguyên 30 phút.
Xóa sự kiện TEST MCP ngày 20/09/2026.
```

## 6. Không chạy `--all` trên lịch cá nhân

Project mặc định:

```env
ALLOW_GOOGLE_WRITE_TESTS=false
```

Hãy dùng `--interactive` cho Calendar thật. Chỉ bật `ALLOW_GOOGLE_WRITE_TESTS=true` nếu cố ý dùng Calendar test riêng.

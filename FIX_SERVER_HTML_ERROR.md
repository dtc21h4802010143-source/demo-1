# ⚠️ LỖI "Server trả về HTML" - HƯỚNG DẪN KHẮC PHỤC

## 🔴 Vấn đề hiện tại

Lỗi **"Server trả về HTML thay vì JSON"** nghĩa là:
- **Server CHƯA CHẠY** hoặc đã crash
- Browser đang truy cập trang không tồn tại → trả về 404 HTML

## ✅ GIẢI PHÁP: Khởi động server thủ công

### Bước 1: Mở Terminal/PowerShell MỚI

**Quan trọng**: Mở cửa sổ terminal RIÊNG để chạy server (không dùng VS Code terminal cũ)

### Bước 2: Chạy lệnh sau

```powershell
cd "C:\Users\Bạc Cầm Ngọc\ttks\TS2"
python admission_system\run_server.py
```

### Bước 3: Đợi cho đến khi thấy

```
======================================================================
  ADMISSION SYSTEM - Flask Development Server
======================================================================
  Server running at: http://localhost:5000
  API Documentation: http://localhost:5000/api/docs
  Press Ctrl+C to stop
======================================================================

 * Running on http://127.0.0.1:5000
```

**✅ Server đã sẵn sàng khi thấy dòng "Running on http://127.0.0.1:5000"**

### Bước 4: GIỮ NGUYÊN terminal đó, KHÔNG tắt

⚠️ **LƯU Ý**: Nếu bạn tắt terminal này, server sẽ dừng!

### Bước 5: Mở browser và test

```
http://localhost:5000/advisor
```

Scroll xuống mục **"Gợi ý ngành bằng AI"** và nhập điểm → Click "Nhận gợi ý"

---

## 🧪 Test nhanh server đang chạy

### Cách 1: Mở browser
```
http://localhost:5000
```

Nếu thấy trang chủ → Server OK ✅

### Cách 2: Dùng PowerShell (terminal khác, không phải terminal chạy server)
```powershell
curl http://localhost:5000 -UseBasicParsing
```

Nếu thấy HTML code → Server OK ✅

### Cách 3: Test API trực tiếp
```powershell
python admission_system\test_api_quick.py
```

Nếu thấy "✅ Success: True" và "Top 3 recommendations" → API OK ✅

---

## 🐛 Troubleshooting

### Lỗi: "Address already in use"
**Nguyên nhân**: Port 5000 đang được dùng bởi process khác

**Giải pháp**:
```powershell
# Tìm process đang dùng port 5000
netstat -ano | findstr :5000

# Kill process (thay <PID> bằng số ở cột cuối)
taskkill /PID <PID> /F

# Chạy lại server
python admission_system\run_server.py
```

### Lỗi: "ImportError: attempted relative import"
**Giải pháp**: Dùng `run_server.py`, KHÔNG chạy `app.py` trực tiếp

❌ SAI:
```powershell
cd admission_system\backend
python app.py
```

✅ ĐÚNG:
```powershell
cd C:\Users\Bạc Cầm Ngọc\ttks\TS2
python admission_system\run_server.py
```

### Lỗi: "No module named 'backend'"
**Giải pháp**: Chạy từ thư mục GỐC dự án (TS2), không phải thư mục backend

---

## 📱 Quy trình hoàn chỉnh

### 1. Khởi động server (Terminal 1)
```powershell
cd "C:\Users\Bạc Cầm Ngọc\ttks\TS2"
python admission_system\run_server.py
```

**Đợi thấy**: `Running on http://127.0.0.1:5000`

### 2. Test trong browser
- Mở: `http://localhost:5000/advisor`
- Nhập điểm: **21.5**
- Nhập sở thích: **công nghệ, AI, lập trình**
- Click: **"Nhận gợi ý"**

### 3. Xem kết quả
Phải thấy danh sách ngành như:
```
1. Khoa học máy tính (AI) (2023)
   18.50 điểm
   Phù hợp: 60 — Xác suất: Rất cao (95-100%)
```

Nếu thấy **"Lỗi: Server trả về HTML"** → Quay lại bước 1, đảm bảo server đang chạy!

---

## 🎯 Checklist nhanh

Trước khi test, kiểm tra:

- [ ] Terminal chạy server ĐANG MỞ và không có lỗi
- [ ] Thấy dòng "Running on http://127.0.0.1:5000" trong terminal
- [ ] Mở `http://localhost:5000` trong browser → thấy trang chủ
- [ ] Browser không dùng cache cũ (nhấn Ctrl+Shift+R để hard refresh)

---

## 💡 Tips

### Để server chạy background
```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Bạc Cầm Ngọc\ttks\TS2'; python admission_system\run_server.py"
```

### Dừng server
- Trong terminal chạy server: Nhấn **Ctrl+C**
- Hoặc đóng terminal

### Check log khi có lỗi
Server logs sẽ hiện trong terminal chạy server. Nếu có lỗi Python, copy log đó để debug.

---

## 📞 Hỗ trợ

Nếu vẫn gặp lỗi:
1. Chụp ảnh terminal chạy server
2. Chụp ảnh lỗi trong browser console (F12)
3. Copy nội dung từ tab Network > Response

# Hướng Dẫn Khởi Động Server & Test API

## 🚀 Khởi động Flask Server

### Cách 1: Chạy app.py trực tiếp
```powershell
# Từ thư mục gốc dự án
cd admission_system\backend
python app.py
```

Server sẽ chạy tại: `http://127.0.0.1:5000`

### Cách 2: Dùng Flask CLI
```powershell
# Từ thư mục gốc dự án
cd admission_system\backend
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"
flask run
```

### Cách 3: Dùng Flask CLI với debug mode
```powershell
flask run --debug --host=0.0.0.0 --port=5000
```

## ✅ Kiểm tra Server đang chạy

### Mở browser và truy cập:
- **Trang chủ**: http://localhost:5000
- **API Docs**: http://localhost:5000/api/docs
- **Trang tư vấn AI**: http://localhost:5000/advisor

### Test API qua terminal:
```powershell
# Test endpoint recommend-programs
python admission_system\test_api_quick.py
```

## 📊 Kiểm tra dữ liệu đã import

```powershell
python -c "from admission_system.backend.app import app, db; from admission_system.backend.models import AdmissionScore; ctx=app.app_context(); ctx.push(); print('Total scores:', AdmissionScore.query.count()); ctx.pop()"
```

Kết quả mong đợi: `Total scores: 86`

## 🔧 Khắc phục lỗi "Server trả về HTML"

### Nguyên nhân:
- Server **chưa khởi động** hoặc crash
- URL sai (kiểm tra `http://localhost:5000` vs `http://127.0.0.1:5000`)
- CORS issue nếu frontend/backend khác origin

### Giải pháp:

#### 1. Kiểm tra server có đang chạy không
```powershell
# Test connection
curl http://localhost:5000
```

Nếu không kết nối được → Khởi động server

#### 2. Xem logs của Flask server
Khi bạn gửi request từ browser, Flask console sẽ hiển thị:
```
127.0.0.1 - - [21/Oct/2025 10:30:00] "POST /api/recommend-programs HTTP/1.1" 200 -
```

Nếu thấy **404** hoặc **500** → Có vấn đề với route hoặc code

#### 3. Kiểm tra trong Browser DevTools (F12)

**Tab Network:**
- **Request URL**: Phải là `http://localhost:5000/api/recommend-programs`
- **Status Code**: Phải là `200 OK`
- **Content-Type**: Phải là `application/json`

**Tab Console:**
- Xem có lỗi JavaScript không
- Check log "Non-JSON response" (đã được thêm vào advisor.html)

## 📋 API Endpoints có sẵn

### 1. Gợi ý theo điểm & sở thích (đã có dữ liệu)
```
POST http://localhost:5000/api/recommend-programs
Content-Type: application/json

{
  "total_score": 21.5,
  "interests": ["công nghệ", "AI"],
  "save_preference": false
}
```

✅ **Hoạt động OK** - Trả về 10 ngành phù hợp

### 2. Gợi ý theo phương thức (cần thêm dữ liệu AdmissionQuota)
```
POST http://localhost:5000/api/suggest-programs
Content-Type: application/json

{
  "scores": {"toan": 8.5, "ly": 9.0, "hoa": 8.5},
  "method": "thpt"
}
```

⚠️ **Chưa có dữ liệu** - Cần import thêm vào bảng `AdmissionQuota`

### 3. Lấy điểm chuẩn
```
GET http://localhost:5000/api/admission-scores?year=2025
```

✅ **Hoạt động OK** - 86 records

### 4. Thống kê điểm chuẩn
```
GET http://localhost:5000/api/statistics/admission-scores?year=2025
```

✅ **Hoạt động OK**

## 🐛 Debug Checklist

Khi gặp lỗi "Unexpected token '<'" hoặc "Server trả về HTML":

- [ ] Flask server đang chạy (`python backend/app.py`)
- [ ] Có thể truy cập `http://localhost:5000` trong browser
- [ ] Database đã được tạo (`admission_system/data/admission_system.db` tồn tại)
- [ ] Đã import dữ liệu (`python backend/import_admission_scores.py`)
- [ ] Browser không cache response cũ (Ctrl+Shift+R để hard refresh)
- [ ] URL trong JavaScript đúng (`/api/recommend-programs`)
- [ ] Content-Type header là `application/json`
- [ ] Không có CORS error trong console

## 📱 Test từ browser

### Test form gợi ý AI trong trang advisor:

1. Mở browser: http://localhost:5000/advisor
2. Scroll xuống mục **"Gợi ý ngành bằng AI theo điểm & sở thích"**
3. Nhập:
   - Tổng điểm: **21.5**
   - Sở thích: **công nghệ, AI, lập trình**
4. Click **"Nhận gợi ý"**
5. Xem kết quả hiển thị bên dưới

### Kết quả mong đợi:
```
Kết quả gợi ý (AI)

1. Khoa học máy tính (AI) (2023)
   21.5 điểm
   Phù hợp: 60 — Xác suất: Rất cao (95-100%)

2. Kỹ thuật máy tính (2023)
   18.75 điểm
   Phù hợp: 60 — Xác suất: Rất cao (95-100%)
   ...
```

## 🔥 Quick Fix nếu vẫn lỗi

1. **Dừng server (Ctrl+C)**
2. **Xóa database cũ:**
   ```powershell
   Remove-Item admission_system\data\admission_system.db -ErrorAction SilentlyContinue
   ```
3. **Khởi động lại server** (tự động tạo DB mới)
4. **Import lại dữ liệu:**
   ```powershell
   python admission_system\backend\import_admission_scores.py
   ```
5. **Refresh browser** (Ctrl+Shift+R)

## 📞 Liên hệ & Tài liệu

- **API Documentation**: http://localhost:5000/api/docs
- **Hướng dẫn gợi ý ngành**: `HUONG_DAN_GOI_Y_NGANH_HOC.md`
- **Khắc phục lỗi API**: `KHAC_PHUC_LOI_API.md`
- **Test script**: `test_api_quick.py`

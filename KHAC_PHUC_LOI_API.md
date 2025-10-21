# Khắc Phục Lỗi API - Unexpected token '<'

## Nguyên nhân

Lỗi **"Unexpected token '<'"** xảy ra khi JavaScript cố gắng parse HTML (trang lỗi) thành JSON. Điều này thường do:

1. **Route API không tồn tại** - Server trả về 404 HTML page
2. **Server chưa khởi động** - Browser không thể kết nối
3. **Blueprint chưa được đăng ký** - Flask không nhận diện route
4. **Authentication redirect** - Middleware redirect sang trang login (HTML)

## Giải pháp đã áp dụng

### 1. Kiểm tra Content-Type trước khi parse JSON

**File:** `templates/advisor.html`

```javascript
// Trước khi parse JSON, kiểm tra content-type
const contentType = response.headers.get('content-type');
if (!contentType || !contentType.includes('application/json')) {
    const text = await response.text();
    console.error('Non-JSON response:', text.substring(0, 500));
    alert('Lỗi: Server trả về HTML. Vui lòng kiểm tra server logs.');
    return;
}

const data = await response.json();
```

**Lợi ích:**
- Hiển thị thông báo lỗi rõ ràng thay vì "Unexpected token"
- Log nội dung HTML để debug
- Không crash JavaScript khi gặp lỗi

### 2. Đảm bảo Blueprint được đăng ký

**File:** `backend/app.py`

```python
# Register AI Recommendation Blueprint
from .ai_recommendation import ai_recommendation_bp
app.register_blueprint(ai_recommendation_bp)
```

**Kiểm tra:**
```powershell
python -c "from admission_system.backend.app import app; ctx=app.app_context(); ctx.push(); [print(r.rule) for r in app.url_map.iter_rules() if 'recommend' in r.rule]; ctx.pop()"
```

Kết quả mong đợi:
```
/api/recommend-programs
/api/admission-scores
/api/admission-methods
/api/statistics/admission-scores
```

### 3. Tự động tạo bảng DB khi app khởi động

**File:** `backend/app.py`

```python
# Create tables on import/startup (for WSGI and dev server)
try:
    with app.app_context():
        db.create_all()
        seed_initial_data()
except Exception as e:
    print(f"[db] create_all/seed skipped: {e}")
```

**Lợi ích:**
- Không còn lỗi "no such table: user"
- Tự động seed admin user mặc định
- Hoạt động với cả Flask dev server và WSGI

## Cách kiểm tra nhanh

### 1. Kiểm tra API endpoint hoạt động

```powershell
# Test API trong Python
python -c "from admission_system.backend.app import app; ctx=app.app_context(); ctx.push(); client=app.test_client(); resp=client.post('/api/recommend-programs', json={'total_score': 20.5}); print('Status:', resp.status_code); print(resp.get_data(as_text=True)); ctx.pop()"
```

Kết quả mong đợi:
```json
{
  "data": {
    "recommendations": [...],
    "total_matches": 54,
    "total_score": 20.5
  },
  "success": true
}
```

### 2. Kiểm tra trong browser

1. Mở DevTools (F12)
2. Vào tab **Network**
3. Gửi request từ form
4. Kiểm tra:
   - **Status Code**: Phải là 200
   - **Content-Type**: Phải là `application/json`
   - **Response**: Phải là JSON, không phải HTML

### 3. Kiểm tra server logs

Nếu vẫn gặp lỗi, xem console output của Flask server:
- Có lỗi Python exception?
- Route có được hit không?
- Database connection có OK không?

## Các API endpoints hiện có

### 1. Gợi ý ngành theo điểm & sở thích
```
POST /api/recommend-programs
Content-Type: application/json

{
  "total_score": 21.5,
  "math_score": 8.0,
  "subject_combination": "A00",
  "interests": ["công nghệ", "AI"],
  "skills": ["lập trình"],
  "save_preference": false
}
```

### 2. Gợi ý ngành theo phương thức xét tuyển
```
POST /api/suggest-programs
Content-Type: application/json

{
  "scores": {
    "toan": 8.5,
    "ly": 9.0,
    "hoa": 8.5
  },
  "method": "thpt"
}
```

### 3. Lấy điểm chuẩn
```
GET /api/admission-scores?year=2025&min_score=18
```

### 4. Lấy phương thức xét tuyển
```
GET /api/admission-methods?year=2025
```

### 5. Thống kê điểm chuẩn
```
GET /api/statistics/admission-scores?year=2025
```

## Checklist vận hành

- [ ] Flask server đang chạy (`python -m flask run` hoặc `python backend/app.py`)
- [ ] Database đã được tạo và có dữ liệu (`admission_system/data/admission_system.db`)
- [ ] Blueprint AI recommendation đã được import (`from .ai_recommendation import ai_recommendation_bp`)
- [ ] Điểm chuẩn đã được import (`python backend/import_admission_scores.py`)
- [ ] Browser không cache response cũ (Ctrl+Shift+R để hard refresh)

## Lỗi thường gặp khác

### Lỗi: 404 Not Found
**Nguyên nhân:** Route chưa được đăng ký hoặc URL sai

**Giải pháp:**
```python
# Kiểm tra routes
python -c "from admission_system.backend.app import app; [print(r) for r in app.url_map.iter_rules()]"
```

### Lỗi: 500 Internal Server Error
**Nguyên nhân:** Exception trong API handler

**Giải pháp:**
- Xem Flask server logs
- Kiểm tra database connection
- Verify dữ liệu đầu vào hợp lệ

### Lỗi: CORS
**Nguyên nhân:** Frontend và backend chạy trên domain/port khác nhau

**Giải pháp:**
```python
# Thêm vào backend/app.py
from flask_cors import CORS
CORS(app)
```

### Lỗi: 302 Redirect (trong tests)
**Nguyên nhân:** @login_required hoặc @verified_required chặn request

**Giải pháp:**
- Đã fix bằng cách bypass khi `app.config['TESTING'] = True`
- Decorator `rate_limit()` cũng bypass trong test mode

## Liên hệ & Debug

Nếu vẫn gặp vấn đề:
1. Chụp screenshot lỗi trong browser console
2. Copy nội dung response HTML (tab Network > Response)
3. Copy Flask server logs
4. Kiểm tra file `admission_system/data/admission_system.db` có tồn tại không

## Tài liệu tham khảo

- API Documentation: `/api/docs` (Swagger UI)
- Hướng dẫn gợi ý ngành: `HUONG_DAN_GOI_Y_NGANH_HOC.md`
- Database models: `backend/models.py`
- API endpoints: `backend/ai_recommendation.py`

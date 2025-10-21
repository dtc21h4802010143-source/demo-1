# Tính năng Gợi ý Ngành học bằng AI

## Tổng quan

Hệ thống đã được bổ sung tính năng **Gợi ý ngành học thông minh** dựa trên điểm thi và sở thích của thí sinh. Tính năng này sử dụng thuật toán matching để đề xuất các ngành phù hợp nhất với năng lực và nguyện vọng của học sinh.

## Cấu trúc dữ liệu

### 1. Bảng dữ liệu mới

#### `AdmissionScore` - Điểm chuẩn theo ngành
- `id`: ID tự tăng
- `program_id`: Liên kết với bảng Program (nullable)
- `program_name`: Tên ngành (bắt buộc)
- `year`: Năm tuyển sinh
- `admission_score`: Điểm chuẩn
- `notes`: Ghi chú đặc biệt (VD: yêu cầu Toán ≥ 8.0)

#### `AdmissionMethod` - Phương thức xét tuyển
- `id`: ID tự tăng
- `method_name`: Tên phương thức (V-SAT-TNU, Học bạ, THPT...)
- `year`: Năm áp dụng
- `min_score`: Điểm sàn tối thiểu
- `special_requirements`: Yêu cầu đặc biệt
- `description`: Mô tả chi tiết

#### `StudentPreference` - Sở thích học sinh
- Lưu trữ điểm các môn, tổ hợp, sở thích và kỹ năng của học sinh
- Hỗ trợ phân tích và cải thiện thuật toán gợi ý

### 2. File dữ liệu CSV

- **`data/admission_scores.csv`**: Điểm chuẩn 86 ngành từ 2022-2025
- **`data/admission_methods.csv`**: 6 phương thức xét tuyển qua các năm

## API Endpoints

### 1. Lấy danh sách điểm chuẩn
```
GET /api/admission-scores
```

**Query Parameters:**
- `year` (int): Lọc theo năm
- `program_name` (string): Tìm kiếm tên ngành
- `min_score` (float): Điểm tối thiểu
- `max_score` (float): Điểm tối đa

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "program_name": "Nghệ thuật số",
      "year": 2025,
      "admission_score": 23.0,
      "notes": ""
    }
  ],
  "total": 86
}
```

### 2. Lấy phương thức xét tuyển
```
GET /api/admission-methods
```

**Query Parameters:**
- `year` (int): Lọc theo năm

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "method_name": "V-SAT-TNU",
      "year": 2025,
      "min_score": 225,
      "special_requirements": "Không có môn nào dưới 15.0 điểm",
      "description": "Kỳ thi V-SAT-TNU..."
    }
  ],
  "total": 6
}
```

### 3. Gợi ý ngành học (API chính)
```
POST /api/recommend-programs
```

**Request Body:**
```json
{
  "total_score": 21.5,
  "math_score": 8.0,
  "subject_combination": "A00",
  "interests": ["công nghệ", "lập trình", "AI"],
  "skills": ["logic", "giải quyết vấn đề"],
  "career_goals": "Trở thành kỹ sư phần mềm",
  "save_preference": false,
  "applicant_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_score": 21.5,
    "total_matches": 54,
    "recommendations": [
      {
        "program_name": "Kỹ thuật máy tính",
        "admission_score": 18.75,
        "year": 2025,
        "match_score": 60.0,
        "score_difference": 2.75,
        "probability": "Rất cao (95-100%)",
        "notes": "",
        "program_info": {
          "name": "Kỹ thuật máy tính",
          "code": "KTM",
          "description": "Ngành Kỹ thuật máy tính.",
          "career_prospects": "Cơ hội việc làm rộng mở...",
          "tuition_fee": 12000000.0
        }
      }
    ]
  }
}
```

### 4. Thống kê điểm chuẩn
```
GET /api/statistics/admission-scores?year=2025
```

**Response:**
```json
{
  "success": true,
  "data": {
    "year": 2025,
    "total_programs": 25,
    "average_score": 19.53,
    "max_score": 23.0,
    "min_score": 18.0,
    "top_programs": [
      {
        "program_name": "Nghệ thuật số",
        "admission_score": 23.0,
        "notes": ""
      }
    ]
  }
}
```

## Thuật toán Matching

### Công thức tính điểm phù hợp (Match Score)

**Thang điểm: 0-100**

#### 1. Điểm số (40%)
- Chênh lệch ≥ 3 điểm: 40 điểm (Rất an toàn)
- Chênh lệch ≥ 1.5 điểm: 35 điểm (An toàn)
- Chênh lệch ≥ 0.5 điểm: 30 điểm (Trúng tuyển khả thi)
- Chênh lệch ≥ 0 điểm: 25 điểm (Nguy hiểm)
- Chênh lệch < 0: 10 điểm (Rất khó)

#### 2. Sở thích (30%)
Hệ thống matching từ khóa:
- **Công nghệ**: máy tính, phần mềm, mạng, an ninh
- **Kinh doanh**: quản trị, marketing, thương mại
- **Thiết kế**: đồ họa, truyền thông, nghệ thuật
- **AI**: trí tuệ, máy học, dữ liệu
- **Tự động**: robot, điện tử, cơ điện

#### 3. Kỹ năng (30%)
- **Lập trình** → Phần mềm, CNTT, Máy tính
- **Logic** → Máy tính, Toán, AI
- **Sáng tạo** → Thiết kế, Đồ họa, Nghệ thuật
- **Giao tiếp** → Marketing, Quản trị, Kinh doanh
- **Kỹ thuật** → Kỹ thuật, Điện, Tự động, Ô tô

### Xác suất trúng tuyển

- **Rất cao (95-100%)**: Điểm cao hơn chuẩn ≥ 3 điểm
- **Cao (80-95%)**: Điểm cao hơn 1.5-3 điểm
- **Trung bình (60-80%)**: Điểm cao hơn 0.5-1.5 điểm
- **Thấp (40-60%)**: Điểm cao hơn 0-0.5 điểm
- **Rất thấp (<40%)**: Điểm thấp hơn điểm chuẩn

## Giao diện người dùng

### Form nhập liệu (Trang Hồ sơ - `/profile`)

**Các trường dữ liệu:**
1. **Tổng điểm (3 môn)** - Bắt buộc
2. **Điểm Toán** - Tùy chọn
3. **Tổ hợp** - Tùy chọn (VD: A00, D01)
4. **Sở thích** - Tùy chọn (phân cách bằng dấu phẩy)

**Hiển thị kết quả:**
- Danh sách ngành được sắp xếp theo độ phù hợp
- Hiển thị: Tên ngành, Điểm chuẩn, Năm, Độ phù hợp, Xác suất
- Ghi chú đặc biệt (nếu có)
- Thông tin chương trình (mô tả, triển vọng nghề nghiệp)

## Hướng dẫn sử dụng

### 1. Import dữ liệu điểm chuẩn (Lần đầu)

```powershell
# Chạy từ thư mục gốc dự án
python .\admission_system\backend\import_admission_scores.py
```

**Kết quả mong đợi:**
```
✅ Đã import 86 điểm chuẩn mới
✅ Đã import 6 phương thức xét tuyển mới
📊 THỐNG KÊ DỮ LIỆU ĐIỂM CHUẨN
Tổng số điểm chuẩn: 86
...
```

### 2. Sử dụng qua giao diện web

1. Đăng nhập vào hệ thống
2. Vào trang **Hồ sơ cá nhân** (`/profile`)
3. Cuộn xuống phần **"Gợi ý ngành bằng AI theo điểm và sở thích"**
4. Nhập:
   - Tổng điểm 3 môn (VD: 21.5)
   - Điểm Toán (nếu có)
   - Tổ hợp môn (VD: A00)
   - Sở thích (VD: công nghệ, lập trình, AI)
5. Nhấn **"Nhận gợi ý"**
6. Xem danh sách ngành phù hợp kèm xác suất trúng tuyển

### 3. Sử dụng qua API (Developer)

**Test nhanh bằng Python:**
```python
import requests

url = "http://localhost:5000/api/recommend-programs"
data = {
    "total_score": 20.5,
    "interests": ["công nghệ", "AI"],
    "skills": ["lập trình"]
}

response = requests.post(url, json=data)
print(response.json())
```

**Test bằng PowerShell:**
```powershell
$body = @{
    total_score = 20.5
    interests = @("công nghệ", "AI")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/recommend-programs" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

## Cập nhật dữ liệu

### Thêm điểm chuẩn mới

Chỉnh sửa file `data/admission_scores.csv`:
```csv
program_name,year_2025,year_2024,year_2023,year_2022,notes
Ngành mới,22.00,-,-,-,Ghi chú đặc biệt
```

Sau đó chạy lại script import:
```powershell
python .\admission_system\backend\import_admission_scores.py
```

### Cập nhật thuật toán matching

File: `backend/ai_recommendation.py`

Hàm: `calculate_match_score()` và `get_admission_probability()`

## Kiểm thử

### Unit Test
```powershell
# Test API gợi ý
python .\admission_system\backend\smoke_test_recommend.py
```

### Integration Test
```powershell
# Test toàn bộ hệ thống
pytest -q .\admission_system\tests\
```

## Lưu ý quan trọng

1. **Dữ liệu điểm chuẩn**: Cần cập nhật hàng năm từ nguồn chính thức
2. **Thuật toán matching**: Có thể tinh chỉnh trọng số (40%-30%-30%) theo phản hồi người dùng
3. **Rate limiting**: API có giới hạn request (tắt khi TESTING=True)
4. **Email verification**: Yêu cầu xác thực email được bỏ qua khi TESTING=True
5. **Department nullable**: Trường `department_id` trong `Program` cho phép NULL để linh hoạt

## Cải tiến tương lai

- [ ] Tích hợp Machine Learning để học từ lựa chọn thực tế của học sinh
- [ ] Thêm bộ lọc theo khu vực, học phí, thời gian đào tạo
- [ ] Gợi ý dựa trên xu hướng nghề nghiệp và thị trường lao động
- [ ] Chatbot tích hợp tư vấn ngành học
- [ ] Export danh sách gợi ý ra PDF/Excel
- [ ] So sánh điểm của bạn với điểm trung bình đỗ các năm trước
- [ ] Dự đoán điểm chuẩn năm tới dựa trên xu hướng

## Liên hệ & Hỗ trợ

Nếu có vấn đề hoặc đề xuất cải tiến, vui lòng:
- Tạo Issue trên GitHub repository
- Liên hệ admin@university.edu.vn
- Xem tài liệu đầy đủ tại `/api/docs`

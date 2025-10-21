# Deploy lên Render

## Bước 1: Chuẩn bị Repository

1. Push code lên GitHub:
```bash
git add .
git commit -m "Add Render deployment config"
git push origin main
```

## Bước 2: Tạo Web Service trên Render

1. Truy cập https://render.com và đăng nhập
2. Click **New +** → **Web Service**
3. Connect GitHub repository: `dtc21h4802010143-source/demo-1`
4. Cấu hình:
   - **Name**: `admission-system` (hoặc tên bạn muốn)
   - **Region**: Singapore (hoặc gần bạn nhất)
   - **Branch**: `main`
   - **Root Directory**: để trống
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```
     pip install -r requirements.txt && python download_nltk_data.py
     ```
   - **Start Command**: 
     ```
     gunicorn backend.app:app --workers 4 --bind 0.0.0.0:$PORT
     ```
   - **Instance Type**: `Free`

## Bước 3: Cấu hình Environment Variables

Trong phần **Environment**, thêm các biến sau:

### Bắt buộc:
```
SECRET_KEY=your-random-secret-key-here-change-this
FLASK_ENV=production
DEBUG=False
USE_RAG_CHATBOT=false
```

### LLM API Keys (chọn 1 trong các option):
```
# Option 1: Groq (KHUYẾN NGHỊ - miễn phí, nhanh)
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.3-70b-versatile

# Option 2: Google Gemini (miễn phí)
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-google-api-key

# Option 3: OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
```

### Email Configuration (Gmail):
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=Admissions <your-email@gmail.com>
```

## Bước 4: Cấu hình Database (PostgreSQL)

### Option A: Sử dụng Render PostgreSQL (Khuyến nghị)

1. Click **New +** → **PostgreSQL**
2. Cấu hình:
   - **Name**: `admission-db`
   - **Region**: Singapore (cùng region với web service)
   - **Plan**: Free
3. Sau khi tạo xong, copy **Internal Database URL**
4. Quay lại Web Service → Environment → Add:
   ```
   DATABASE_URL=<paste-internal-database-url-here>
   ```

### Option B: Sử dụng SQLite (Đơn giản nhưng không khuyến khích cho production)

Thêm vào Environment:
```
DATABASE_URL=sqlite:///data/admission_system.db
```

## Bước 5: Deploy

1. Click **Create Web Service**
2. Render sẽ tự động build và deploy
3. Đợi 5-10 phút để deployment hoàn tất
4. Truy cập URL được cung cấp (ví dụ: `https://admission-system.onrender.com`)

## Bước 6: Import dữ liệu ban đầu

Sau khi deploy thành công, chạy các lệnh sau trong **Shell** của Render:

```bash
# Import departments và programs
python backend/import_all_csv.py

# Import admission quotas
python backend/import_admission_quotas.py

# Import admission scores
python backend/import_admission_scores.py

# (Optional) Import sample applications
python backend/import_applications.py
```

## Lưu ý quan trọng:

### 1. Database SQLite vs PostgreSQL
- **SQLite**: Đơn giản nhưng Render sẽ xóa database mỗi khi restart
- **PostgreSQL**: Khuyến nghị cho production, dữ liệu persistent

### 2. RAG/LLM Features
- Set `USE_RAG_CHATBOT=false` ban đầu vì Python 3.13 chưa tương thích
- Chỉ bật RAG khi deploy với Python 3.11

### 3. Free Plan Limitations
- Sleep sau 15 phút không hoạt động
- Restart mất ~30-60 giây
- 750 giờ/tháng

### 4. Logs và Monitoring
- Xem logs trong Render Dashboard → Logs tab
- Monitor errors và performance

## Troubleshooting

### Lỗi: "Application failed to respond"
- Check logs trong Render Dashboard
- Đảm bảo `gunicorn` đã được cài trong requirements.txt
- Verify PORT environment variable được bind đúng

### Lỗi: Database connection
- Check DATABASE_URL environment variable
- Đảm bảo PostgreSQL database đã được tạo và running
- Verify connection string format đúng

### Lỗi: Module not found
- Check requirements.txt có đầy đủ dependencies
- Rebuild service để cài lại packages

### Website sleep/slow
- Free plan sẽ sleep sau 15 phút không hoạt động
- Truy cập lần đầu sau khi sleep sẽ mất ~30s để wake up
- Nâng cấp lên Starter plan ($7/tháng) để tránh sleep

## Nâng cấp

### Sử dụng render.yaml (Infrastructure as Code)

Repository đã có file `render.yaml` để tự động cấu hình. Trong Render Dashboard:

1. New → Blueprint
2. Connect repository
3. Render sẽ tự động tạo cả Web Service + PostgreSQL database

## Tài liệu tham khảo

- [Render Python Deployment](https://render.com/docs/deploy-flask)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Render PostgreSQL](https://render.com/docs/databases)

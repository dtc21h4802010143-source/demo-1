# 🎓 Hệ Thống Tuyển Sinh AI

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Flask](https://img.shields.io/badge/flask-3.1+-red.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

**Hệ thống quản lý tuyển sinh thông minh với AI Chatbot tư vấn 24/7**

[Tính năng](#-tính-năng) • [Cài đặt](#-cài-đặt) • [Sử dụng](#-sử-dụng) • [Tech Stack](#-tech-stack) • [API](#-api-endpoints)

</div>

---

## 📖 Giới thiệu

Hệ thống Tuyển Sinh AI là một nền tảng web toàn diện giúp quản lý quy trình tuyển sinh sinh viên, tích hợp công nghệ AI (RAG - Retrieval Augmented Generation) để tư vấn tự động 24/7.

### 🎯 Mục tiêu

- ✅ Số hóa quy trình tuyển sinh
- ✅ Tư vấn thông minh bằng AI
- ✅ Quản lý hồ sơ hiệu quả
- ✅ Trải nghiệm người dùng tốt nhất

---

## ✨ Tính năng

### 👨‍🎓 Dành cho Thí sinh

- 📝 **Đăng ký tài khoản** - Xác thực email tự động
- 👤 **Quản lý hồ sơ** - Cập nhật thông tin cá nhân, upload tài liệu
- ❤️ **Chọn nguyện vọng** - Đăng ký tối đa 3 nguyện vọng
- 🔍 **Tra cứu ngành học** - Tìm kiếm & xem chi tiết các chương trình đào tạo
- 🤖 **Chatbot AI 24/7** - Tư vấn tuyển sinh thông minh với RAG
- 📊 **Theo dõi kết quả** - Xem trạng thái hồ sơ realtime
- 🔐 **Bảo mật** - Mật khẩu mã hóa, reset password qua email

### 👨‍💼 Dành cho Admin

- 📈 **Dashboard thống kê** - Biểu đồ, số liệu tổng hợp
- 🏢 **Quản lý Khoa/Viện** - CRUD departments
- 🎓 **Quản lý Ngành** - CRUD programs, phân bổ khoa
- ✅ **Duyệt hồ sơ** - Approve/Reject applications
- 📧 **Quản lý Email** - Cấu hình SMTP, test email
- 📁 **Export dữ liệu** - Xuất CSV/Excel
- ⚙️ **Cấu hình hệ thống** - Site settings

### 🤖 Chatbot RAG Engine

- 🧠 **Multi-LLM Support** - OpenAI GPT, Google Gemini, Groq, HuggingFace
- 📚 **Knowledge Base** - Vector embeddings với FAISS
- 🔍 **Semantic Search** - Sentence Transformers
- 💬 **Context-aware** - Ghi nhớ lịch sử hội thoại
- 🎯 **Domain-specific** - Chuyên về tuyển sinh

---

## 🚀 Cài đặt

### Yêu cầu hệ thống

- Python 3.8+
- pip (Python package manager)
- SQLite (dev) hoặc PostgreSQL (production)
- Git

### Bước 1: Clone repository

```bash
git clone https://github.com/your-username/admission-system.git
cd admission-system
```

### Bước 2: Tạo môi trường ảo

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 4: Tải NLTK data (cho chatbot)

```bash
python download_nltk_data.py
```

### Bước 5: Cấu hình môi trường

Tạo file `.env` từ template:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:

```env
# Flask
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DATABASE_URL=sqlite:///admission.db

# Email (SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# AI/LLM Keys (chọn 1 trong các providers)
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key

# reCAPTCHA (optional)
RECAPTCHA_SITE_KEY=your-site-key
RECAPTCHA_SECRET_KEY=your-secret-key
```

### Bước 6: Khởi tạo database

```bash
cd backend
python manage_db.py
```

### Bước 7: Import dữ liệu mẫu (optional)

```bash
python import_from_csv.py
```

### Bước 8: Chạy ứng dụng

```bash
python app.py
```

Truy cập: **http://localhost:5000**

---

## 📁 Cấu trúc thư mục

```
admission_system/
│
├── backend/                    # Backend code
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration
│   ├── models.py              # Database models
│   ├── database.py            # Database connection
│   ├── chatbot_engine.py      # Chatbot RAG engine V1
│   ├── chatbot_engine_v2.py   # Chatbot RAG engine V2
│   ├── rag_engine.py          # RAG implementation
│   ├── llm_provider.py        # Multi-LLM provider
│   ├── manage_db.py           # Database management
│   ├── import_from_csv.py     # CSV importer
│   └── utils.py               # Helper functions
│
├── templates/                  # Jinja2 templates
│   ├── base.html              # Base template (Tailwind CSS)
│   ├── index.html             # Homepage
│   ├── login.html             # Login page
│   ├── register.html          # Register page
│   ├── chatbot.html           # Chatbot interface
│   ├── admin/                 # Admin templates
│   │   ├── dashboard.html
│   │   ├── programs.html
│   │   └── ...
│   ├── profile/               # User profile templates
│   ├── wishes/                # Wishes templates
│   └── emails/                # Email templates
│
├── static/                     # Static files
│   ├── css/
│   │   ├── main.css
│   │   └── chatbot.css
│   ├── js/
│   │   ├── main.js
│   │   └── chatbot.js
│   ├── images/
│   └── uploads/               # User uploads
│
├── data/                       # Data files
│   ├── chatbot_knowledge.json # Chatbot knowledge base
│   ├── programs.csv           # Programs data
│   ├── departments.csv        # Departments data
│   └── ...
│
├── tests/                      # Test files
│   └── test_chatbot_rag.py
│
├── instance/                   # Instance folder (SQLite DB)
├── venv/                       # Virtual environment
├── .env                        # Environment variables
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
├── download_nltk_data.py      # NLTK data downloader
└── README.md                  # This file
```

---

## 💻 Tech Stack

### Backend

- **Flask 3.1+** - Web framework
- **SQLAlchemy 2.0+** - ORM
- **Flask-Login** - Authentication
- **Flask-Mail** - Email handling
- **Flask-Limiter** - Rate limiting
- **Flask-WTF** - Forms & CSRF protection
- **python-jose** - JWT tokens
- **Werkzeug** - Password hashing

### Frontend

- **Tailwind CSS 3.4+** - Utility-first CSS
- **FontAwesome 6.5+** - Icons
- **JavaScript (Vanilla)** - Interactivity
- **Jinja2** - Template engine

### AI/ML

- **OpenAI GPT** - Language model
- **Google Gemini** - Alternative LLM
- **Groq** - Fast inference
- **Sentence Transformers** - Embeddings
- **FAISS** - Vector similarity search
- **NLTK** - Natural language processing
- **spaCy** - NLP toolkit
- **scikit-learn** - ML utilities

### Database

- **SQLite** - Development
- **PostgreSQL** - Production ready

### Deployment

- **Gunicorn** - WSGI server
- **HTTPS** - SSL/TLS ready

---

## 🔌 API Endpoints

### Public Routes

```
GET  /                      # Homepage
GET  /programs              # Programs list
GET  /departments           # Departments list
GET  /chatbot               # Chatbot interface
GET  /contact               # Contact page
GET  /faq                   # FAQ page
```

### Authentication

```
GET  /login                 # Login page
POST /login                 # Login submit
GET  /register              # Register page
POST /register              # Register submit
GET  /logout                # Logout
POST /forgot-password       # Password reset request
GET  /reset-password/<token> # Reset password form
GET  /verify-email/<token>  # Email verification
```

### User Profile

```
GET  /profile/view          # View profile
GET  /profile/edit          # Edit profile
POST /profile/edit          # Save profile
GET  /profile/documents     # Upload documents
POST /profile/documents     # Save documents
```

### Wishes/Applications

```
GET  /wishes/add            # Add wish form
POST /wishes/add            # Submit wish
GET  /wishes/view           # View wishes
GET  /results/view          # View results
```

### API Endpoints

```
POST /api/chat              # Chatbot API
POST /api/cv_parse          # CV parsing
```

### Admin Routes

```
GET  /admin/dashboard       # Admin dashboard
GET  /admin/programs        # Manage programs
GET  /admin/departments     # Manage departments
GET  /admin/applications    # Review applications
GET  /admin/statistics      # Statistics
GET  /admin/contact         # Contact settings
GET  /admin/email-test      # Email testing
GET  /admin/export-csv      # Export data
```

---

## 🔧 Cấu hình nâng cao

### Cấu hình Email

Sử dụng **Gmail** (khuyến nghị App Password):

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Cấu hình LLM

Chọn provider trong file `backend/config.py`:

```python
LLM_PROVIDER = 'openai'  # hoặc 'gemini', 'groq', 'huggingface'
```

### Cấu hình Rate Limiting

```python
RATELIMIT_STORAGE_URL = 'redis://localhost:6379'
```

### Production Settings

```env
DEBUG=False
SECRET_KEY=very-secure-random-key
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

---

## 🧪 Testing

### Chạy tests

```bash
cd tests
python test_chatbot_rag.py
```

### Test coverage (TODO)

```bash
pytest --cov=backend tests/
```

---

## 📚 Tài liệu hướng dẫn

- [Hướng dẫn sử dụng](HUONG_DAN_SU_DUNG.md)
- [Hướng dẫn LLM miễn phí](HUONG_DAN_LLM_MIEN_PHI.md)
- [Thiết kế hệ thống](README_DESIGN.md)
- [Chatbot RAG](README_CHATBOT_RAG.md)
- [Tính năng mới](TINH_NANG_MOI.md)
- [Đánh giá hệ thống](DANH_GIA_HE_THONG.md)

---

## 🎨 Screenshots

### Homepage
![Homepage](screenshots/homepage.png)

### Chatbot Interface
![Chatbot](screenshots/chatbot.png)

### Admin Dashboard
![Admin](screenshots/admin-dashboard.png)

### User Profile
![Profile](screenshots/profile.png)

---

## 🤝 Đóng góp

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Your Name** - *Initial work* - [GitHub Profile](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Flask documentation
- Tailwind CSS team
- OpenAI, Google, Groq for LLM APIs
- Sentence Transformers team
- All contributors

---

## 📞 Liên hệ

- Email: admin@example.com
- Website: https://admission-system.example.com
- GitHub: https://github.com/your-username/admission-system

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ and ☕

</div>

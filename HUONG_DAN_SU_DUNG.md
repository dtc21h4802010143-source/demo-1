# HƯỚNG DẪN SỬ DỤNG GIAO DIỆN MỚI

## 🎨 CÁC CẬP NHẬT GIAO DIỆN

### ✅ Navigation Menu (Thanh điều hướng) - ĐÃ CẬP NHẬT

Thanh điều hướng đã được cải thiện với các tính năng sau:

#### **1. Menu Công Khai (Cho tất cả người dùng)**
- 🏠 **Trang chủ** - Trang chủ hệ thống
- 📚 **Ngành đào tạo** - Danh sách các ngành học
- 🏢 **Khoa/Viện** - Thông tin các khoa
- 💬 **Tư vấn AI** - Chatbot tư vấn thông minh
- ✉️ **Liên hệ** - Thông tin liên hệ

#### **2. Khi CHƯA đăng nhập**
Phía bên phải menu hiển thị:
- **Đăng nhập** (nút text)
- **Đăng ký** (nút màu trắng nổi bật, bo tròn)

#### **3. Khi ĐÃ đăng nhập (User thường)**
Phía bên phải menu hiển thị dropdown với tên người dùng:
- 👤 **[Tên người dùng]** ▼
  - Email và trạng thái xác thực (✓ Đã xác thực / ⚠️ Chưa xác thực)
  - **Hồ sơ cá nhân** - Xem/sửa thông tin
  - **Nguyện vọng** - Quản lý nguyện vọng đăng ký
  - **Kết quả** - Xem kết quả xét tuyển
  - **Đăng xuất** (màu đỏ)

#### **4. Khi đăng nhập với quyền ADMIN**
Phía bên phải menu có 2 dropdown:
- ⚙️ **Quản trị** ▼
  - 🏠 Dashboard
  - 📚 Quản lý ngành
  - 🏢 Quản lý khoa
  - 📝 Đơn đăng ký
  - 📊 Thống kê
  - ⚙️ Cài đặt
- 👤 **[Tên admin]** ▼
  - Email và trạng thái
  - **Đăng xuất** (màu đỏ)

---

## 🎯 HƯỚNG DẪN SỬ DỤNG TỪNG TÍNH NĂNG

### **A. Đăng Ký Tài Khoản Mới**

1. Truy cập: http://127.0.0.1:5000
2. Click nút **"Đăng ký"** (nút trắng bên phải navbar)
3. Hoặc truy cập trực tiếp: http://127.0.0.1:5000/register
4. Điền đầy đủ thông tin:
   - Họ và tên đệm
   - Tên
   - Email
   - Số điện thoại
   - Mật khẩu (tối thiểu 8 ký tự)
   - Xác nhận mật khẩu
   - Ngày sinh
   - ✓ Đồng ý điều khoản
5. Click **"Đăng ký"**
6. Kiểm tra email để xác thực tài khoản

### **B. Đăng Nhập**

1. Click nút **"Đăng nhập"** trên navbar
2. Hoặc truy cập: http://127.0.0.1:5000/login
3. Nhập:
   - Email
   - Mật khẩu
   - ✓ Ghi nhớ đăng nhập (optional)
4. Click **"Đăng nhập"**

**Tài khoản admin mặc định:**
- Username: `admin`
- Password: `admin123`
- URL: http://127.0.0.1:5000/login

### **C. Quản Lý Hồ Sơ (User)**

1. Đăng nhập vào hệ thống
2. Click dropdown **[Tên bạn]** ▼ trên navbar
3. Chọn **"Hồ sơ cá nhân"**
4. Hoặc truy cập: http://127.0.0.1:5000/profile
5. Click **"Chỉnh sửa"** để cập nhật thông tin

### **D. Đăng Ký Nguyện Vọng**

1. Đăng nhập và xác thực email
2. Click dropdown → **"Nguyện vọng"**
3. Hoặc: http://127.0.0.1:5000/wishes
4. Click **"Thêm nguyện vọng"**
5. Chọn ngành học muốn đăng ký
6. Click **"Nộp nguyện vọng"**

### **E. Chatbot Tư Vấn AI**

1. Click **"Tư vấn AI"** trên navbar
2. Hoặc: http://127.0.0.1:5000/chatbot
3. Gõ câu hỏi vào ô chat, ví dụ:
   - "Điểm chuẩn ngành CNTT 2024"
   - "Học phí ICTU"
   - "Địa chỉ trường"
4. Bot sẽ trả lời dựa trên knowledge base

### **F. Quản Trị Admin**

#### **Dashboard**
- URL: http://127.0.0.1:5000/admin/dashboard
- Xem thống kê tổng quan: users, ngành, khoa, đơn đăng ký

#### **Quản lý Ngành học**
- URL: http://127.0.0.1:5000/admin/programs
- **Thêm ngành:** Click "Thêm ngành mới"
- **Sửa:** Click biểu tượng ✏️
- **Xóa:** Click biểu tượng 🗑️

#### **Quản lý Khoa**
- URL: http://127.0.0.1:5000/admin/departments
- Tương tự như quản lý ngành

#### **Đơn đăng ký**
- URL: http://127.0.0.1:5000/admin/applications
- Xem danh sách đơn
- **Phê duyệt:** Click "Phê duyệt"
- **Từ chối:** Click "Từ chối"

#### **Thống kê**
- URL: http://127.0.0.1:5000/admin/statistics
- Xem biểu đồ, báo cáo chi tiết

#### **Cài đặt**
- URL: http://127.0.0.1:5000/admin/contact
- Cập nhật thông tin liên hệ
- Test email: http://127.0.0.1:5000/admin/email-test

---

## 📱 RESPONSIVE DESIGN

### **Trên Desktop (> 992px)**
- Menu ngang đầy đủ
- Dropdown menu mở xuống
- 2-3 cột layout

### **Trên Tablet (768px - 991px)**
- Menu có thể collapse
- 2 cột layout
- Buttons vừa vặn

### **Trên Mobile (< 768px)**
- Menu hamburger (☰)
- Click để mở menu
- 1 cột layout
- Buttons full-width

**Cách mở menu trên mobile:**
1. Click biểu tượng hamburger ☰ (góc phải navbar)
2. Menu sẽ mở ra dạng dropdown
3. Click vào mục bất kỳ để điều hướng

---

## 🎨 CÁC TEMPLATE HIỆN ĐẠI

Hệ thống có 2 bộ templates:

### **Templates Cũ (Hiện tại đang dùng)**
- `index.html`, `login.html`, `register.html`, etc.
- Dùng Bootstrap 5
- Có đầy đủ chức năng

### **Templates Mới (Modern - Đã tạo sẵn)**
- `index_modern.html` - Trang chủ hiện đại
- `programs_modern.html` - Ngành học với filter
- `chatbot_modern.html` - Chat UI đẹp
- `login_modern.html` - Login với social
- `register_modern.html` - Register form đẹp
- `contact_modern.html` - Contact với map

**Để sử dụng templates modern:**
```bash
# Backup templates cũ
cd templates
mv index.html index_old.html
mv login.html login_old.html
# ... tương tự

# Rename templates modern
mv index_modern.html index.html
mv login_modern.html login.html
# ... tương tự
```

---

## 🔧 TROUBLESHOOTING

### **Vấn đề: Không thấy menu Đăng nhập/Đăng xuất**

**Nguyên nhân:** Navbar bị collapse trên mobile

**Giải pháp:**
1. Kiểm tra chiều rộng màn hình
2. Trên mobile: Click biểu tượng ☰
3. Trên desktop: Zoom out trình duyệt (Ctrl + -)
4. Refresh trang (F5)

### **Vấn đề: Dropdown menu không hoạt động**

**Nguyên nhân:** Bootstrap JS chưa load

**Giải pháp:**
1. Kiểm tra console (F12) xem có lỗi JS không
2. Đảm bảo có internet (Bootstrap CDN)
3. Clear cache (Ctrl + Shift + Del)
4. Restart server:
```bash
cd "c:\Users\Bạc Cầm Ngọc\ttks\TS2\admission_system"
python backend\app.py
```

### **Vấn đề: Đăng nhập thành công nhưng không chuyển trang**

**Nguyên nhân:** Session không lưu

**Giải pháp:**
1. Kiểm tra SECRET_KEY trong .env
2. Clear cookies trình duyệt
3. Thử trình duyệt khác (Chrome/Firefox)

### **Vấn đề: Email xác thực không nhận được**

**Nguyên nhân:** SMTP chưa cấu hình

**Giải pháp:**
1. Kiểm tra banner cảnh báo trên trang
2. Xem file .env:
   - MAIL_USERNAME=dtc21h4802010143@ictu.edu.vn
   - MAIL_PASSWORD=jutkeqhwpcjnkwje
3. Test email:
```bash
python backend\mail_quick_test.py
```

---

## 📊 DANH SÁCH ROUTES (URL)

### **Public Routes (Không cần đăng nhập)**
- `/` - Trang chủ
- `/programs` - Ngành đào tạo
- `/departments` - Khoa/Viện
- `/chatbot` - Chatbot
- `/contact` - Liên hệ
- `/login` - Đăng nhập
- `/register` - Đăng ký
- `/forgot-password` - Quên mật khẩu
- `/guide` - Hướng dẫn
- `/faq` - Câu hỏi thường gặp
- `/scholarships` - Học bổng
- `/privacy` - Chính sách bảo mật
- `/terms` - Điều khoản

### **User Routes (Cần đăng nhập)**
- `/profile` - Hồ sơ
- `/profile/edit` - Sửa hồ sơ
- `/profile/documents` - Tài liệu
- `/wishes` - Nguyện vọng
- `/wishes/add` - Thêm nguyện vọng
- `/results` - Kết quả
- `/logout` - Đăng xuất

### **Admin Routes (Cần quyền admin)**
- `/admin/dashboard` - Dashboard
- `/admin/programs` - Quản lý ngành
- `/admin/programs/add` - Thêm ngành
- `/admin/programs/edit/<id>` - Sửa ngành
- `/admin/departments` - Quản lý khoa
- `/admin/departments/add` - Thêm khoa
- `/admin/applications` - Đơn đăng ký
- `/admin/statistics` - Thống kê
- `/admin/contact` - Cài đặt liên hệ
- `/admin/email-test` - Test email

### **API Routes**
- `POST /api/chat` - Chatbot API
- `GET/POST /api/mail-test` - Test email API
- `POST /api/cv_parse` - Parse CV

---

## 🚀 KHỞI ĐỘNG NHANH

### **Khởi động server:**
```bash
cd "c:\Users\Bạc Cầm Ngọc\ttks\TS2\admission_system"
python backend\app.py
```

### **Truy cập trang chủ:**
```
http://127.0.0.1:5000
```

### **Đăng nhập admin:**
```
URL: http://127.0.0.1:5000/login
Username: admin
Password: admin123
```

### **Test email:**
```bash
python backend\mail_quick_test.py
```

---

## 📸 SCREENSHOT CÁC TÍNH NĂNG

### **Navbar - Chưa đăng nhập:**
```
[Logo] Hệ thống Tuyển sinh | Trang chủ | Ngành | Khoa | Tư vấn | Liên hệ     [Đăng nhập] [Đăng ký]
```

### **Navbar - Đã đăng nhập (User):**
```
[Logo] Hệ thống Tuyển sinh | Trang chủ | Ngành | Khoa | Tư vấn | Liên hệ     [Nguyễn Văn A ▼]
                                                                                ├─ user@email.com ✓
                                                                                ├─ Hồ sơ
                                                                                ├─ Nguyện vọng
                                                                                ├─ Kết quả
                                                                                └─ Đăng xuất
```

### **Navbar - Admin:**
```
[Logo] Hệ thống Tuyển sinh | Trang chủ | Ngành | Khoa | Tư vấn | Liên hệ     [Quản trị ▼] [Admin ▼]
                                                                                └─ Dashboard  └─ Đăng xuất
                                                                                   Ngành
                                                                                   Khoa
                                                                                   Đơn
                                                                                   Thống kê
                                                                                   Cài đặt
```

---

## ✅ CHECKLIST KIỂM TRA

- [x] Navbar hiển thị đầy đủ menu công khai
- [x] Nút "Đăng nhập" hiển thị khi chưa đăng nhập
- [x] Nút "Đăng ký" nổi bật (màu trắng, bo tròn)
- [x] Dropdown user menu khi đã đăng nhập
- [x] Hiển thị email và trạng thái xác thực
- [x] Menu "Hồ sơ", "Nguyện vọng", "Kết quả" cho user
- [x] Dropdown "Quản trị" cho admin
- [x] Menu admin đầy đủ: Dashboard, Ngành, Khoa, Đơn, Thống kê, Cài đặt
- [x] Nút "Đăng xuất" màu đỏ
- [x] Responsive trên mobile (hamburger menu)
- [x] Hover effects mượt mà
- [x] Icons rõ ràng

---

## 💡 MẸO SỬ DỤNG

1. **Keyboard shortcuts:**
   - `Ctrl + L` → Focus vào thanh địa chỉ
   - `F5` → Refresh trang
   - `F11` → Fullscreen
   - `F12` → Mở Developer Tools

2. **Trên mobile:**
   - Scroll để thu gọn navbar
   - Swipe để mở menu
   - Tap 2 lần để zoom

3. **Test nhanh:**
   - Mở 2 trình duyệt: 1 user, 1 admin
   - Sử dụng Incognito mode để test đăng ký mới
   - Dùng responsive mode (F12 → toggle device toolbar)

---

**Cập nhật:** 19/10/2025  
**Version:** 2.0  
**Tác giả:** GitHub Copilot

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    head = db.Column(db.String(100))
    contact_email = db.Column(db.String(120))
    programs = db.relationship('Program', backref='department', lazy=True)

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    description = db.Column(db.Text)
    duration = db.Column(db.String(50))
    requirements = db.Column(db.Text)
    career_prospects = db.Column(db.Text)
    tuition_fee = db.Column(db.Float)
    admission_quotas = db.relationship('AdmissionQuota', backref='program', lazy=True)
    # Applications (wishes) linked to this program
    applications = db.relationship('Application', backref='program', lazy=True)

class AdmissionQuota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    quota = db.Column(db.Integer, nullable=False)
    minimum_score = db.Column(db.Float)
    actual_intake = db.Column(db.Integer)

class AdmissionScore(db.Model):
    """Bảng lưu điểm chuẩn theo từng ngành và năm"""
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=True)
    program_name = db.Column(db.String(200), nullable=False)  # Tên ngành (có thể khác với Program.name)
    year = db.Column(db.Integer, nullable=False)
    admission_score = db.Column(db.Float, nullable=True)  # Điểm chuẩn
    notes = db.Column(db.Text)  # Ghi chú đặc biệt (VD: yêu cầu Toán >= 8.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdmissionMethod(db.Model):
    """Bảng lưu phương thức xét tuyển theo năm"""
    id = db.Column(db.Integer, primary_key=True)
    method_name = db.Column(db.String(100), nullable=False)  # V-SAT-TNU, Học bạ, Điểm thi THPT
    year = db.Column(db.Integer, nullable=False)
    min_score = db.Column(db.Float, nullable=True)  # Điểm tối thiểu
    special_requirements = db.Column(db.Text)  # Yêu cầu đặc biệt
    description = db.Column(db.Text)  # Mô tả phương thức
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudentPreference(db.Model):
    """Bảng lưu sở thích/năng lực của học sinh để gợi ý ngành học"""
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'), nullable=True)
    session_id = db.Column(db.String(100))  # Cho người dùng ẩn danh
    
    # Điểm số các môn
    math_score = db.Column(db.Float)  # Toán
    physics_score = db.Column(db.Float)  # Lý
    chemistry_score = db.Column(db.Float)  # Hóa
    biology_score = db.Column(db.Float)  # Sinh
    literature_score = db.Column(db.Float)  # Văn
    english_score = db.Column(db.Float)  # Anh
    history_score = db.Column(db.Float)  # Sử
    geography_score = db.Column(db.Float)  # Địa
    
    # Tổ hợp môn và tổng điểm
    subject_combination = db.Column(db.String(50))  # A00, A01, D01, etc.
    total_score = db.Column(db.Float)  # Tổng điểm 3 môn
    
    # Sở thích và năng lực
    interests = db.Column(db.Text)  # JSON: ["công nghệ", "kinh doanh", "thiết kế"]
    skills = db.Column(db.Text)  # JSON: ["lập trình", "giao tiếp", "sáng tạo"]
    career_goals = db.Column(db.Text)  # Mục tiêu nghề nghiệp
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cccd = db.Column(db.String(20), unique=True, nullable=True)  # Số căn cước công dân
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(200))
    high_school = db.Column(db.String(100))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('Application', backref='applicant', lazy=True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    # Workflow: Draft -> Submitted -> Under Review -> Accepted/Rejected
    status = db.Column(db.String(20), default='Draft')
    # Phương thức xét tuyển
    admission_method = db.Column(db.String(100), nullable=True)
    scores = db.relationship('Score', backref='application', lazy=True)

class ApplicationStatusLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    from_status = db.Column(db.String(20))
    to_status = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text)
    actor_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

class ApplicantDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)  # Môn học hoặc loại điểm
    score = db.Column(db.Float, nullable=False)
    score_type = db.Column(db.String(50), nullable=True)  # Loại điểm: 'thi_thpt', 'hoc_ba', 'dgnl', etc

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Email verification
    email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ChatbotInteraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    session_id = db.Column(db.String(50))
    feedback_rating = db.Column(db.Integer)
    feedback_comment = db.Column(db.Text)

class Notification(db.Model):
    """Thông báo cho người dùng"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')  # info, success, warning, error
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    link = db.Column(db.String(500))  # Optional link to related resource
    
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

# Simple key-value settings table (e.g., contact info)
class SiteSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)


# Model News (Tin tức & sự kiện)
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.Column(db.String(100))
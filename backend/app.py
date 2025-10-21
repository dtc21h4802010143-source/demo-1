from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os
from functools import wraps
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_mail import Mail, Message
from sqlalchemy import text
# --- Thêm dotenv để nạp biến môi trường từ file .env ---
from dotenv import load_dotenv
load_dotenv()
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
except Exception:  # Fallback if package not installed
    Limiter = None
    def get_remote_address():
        return '0.0.0.0'
try:
    import requests
except Exception:
    requests = None
try:
    from flask_swagger_ui import get_swaggerui_blueprint
except Exception:
    get_swaggerui_blueprint = None

from .models import db, User, Department, Program, Applicant, Application, ChatbotInteraction, SiteSetting, News, AdmissionQuota, Score
from .config import Config
from .chatbot_engine import ChatbotEngine
from werkzeug.utils import secure_filename

app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
app.config.from_object(Config)

# Normalize SQLite path to absolute to avoid path issues
db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
if isinstance(db_uri, str) and db_uri.startswith('sqlite:///') and not db_uri.startswith('sqlite:////'):
    rel_path = db_uri.replace('sqlite:///', '', 1)
    # Base at project root (one level above backend)
    project_root = os.path.abspath(os.path.join(app.root_path, '..'))
    abs_path = os.path.abspath(os.path.join(project_root, rel_path))
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + abs_path.replace('\\', '/')

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Document upload constants
# Allow common document types and plain text for testing/simple CV uploads
ALLOWED_DOC_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "doc", "docx", "txt"}
MAX_DOC_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_doc(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOC_EXTENSIONS

# Mail and token setup
mail = Mail(app)

# Swagger UI setup (API Documentation)
if get_swaggerui_blueprint:
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    
    swagger_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Admission System API"
        }
    )
    app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)

# Register AI Recommendation Blueprint
from .ai_recommendation import ai_recommendation_bp
app.register_blueprint(ai_recommendation_bp)

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def send_email(subject, recipients, html_body):
    try:
        msg = Message(subject, recipients=recipients)
        default_sender = app.config.get('MAIL_DEFAULT_SENDER')
        if default_sender:
            msg.sender = default_sender
        msg.html = html_body
        mail.send(msg)
        return True
    except Exception as e:
        print(f"[mail] send failed: {e}")
        return False

# Rate limiter (safe fallback if dependency missing)
if Limiter:
    limiter = Limiter(get_remote_address, app=app, default_limits=["200/day", "50/hour"])
else:
    class _LimiterFallback:
        def limit(self, *_args, **_kwargs):
            def _decorator(f):
                return f
            return _decorator
    limiter = _LimiterFallback()

# Bọc decorator limit để bỏ qua khi TESTING
def rate_limit(rule: str):
    def _decorator(f):
        if app.config.get('TESTING'):
            return f
        return limiter.limit(rule)(f)
    return _decorator

def verify_recaptcha(token: str) -> bool:
    secret = os.getenv('RECAPTCHA_SECRET_KEY')
    if not secret:
        # Not configured -> skip verification
        return True
    if not token or not requests:
        return False
    try:
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
            'secret': secret,
            'response': token
        }, timeout=5)
        data = r.json()
        return bool(data.get('success'))
    except Exception as e:
        print(f"[recaptcha] verify failed: {e}")
        return False

# Add template context processor for datetime
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Environment/Config health
def _compute_env_health():
    issues = []
    # Weak/placeholder SECRET_KEY
    sk = app.config.get('SECRET_KEY')
    if not sk or sk in ('your-secret-key-here', 'change-this-in-production'):
        issues.append('SECRET_KEY')
    # SMTP completeness
    required_mail = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_DEFAULT_SENDER']
    mail_ok = all(bool(app.config.get(k)) for k in required_mail)
    if not mail_ok:
        issues.append('MAIL')
    return {'issues': issues, 'mail_ok': mail_ok}

@app.context_processor
def inject_env_health():
    env = _compute_env_health()
    return {
        'mail_config_ok': env['mail_ok'],
        'env_config_issues': env['issues'],
        'recaptcha_site_key': os.getenv('RECAPTCHA_SITE_KEY')
    }

# Log basic warnings at startup
env_health = _compute_env_health()
if env_health['issues']:
    print(f"[config] Warnings: {', '.join(env_health['issues'])} configuration incomplete. Check .env or environment variables.")

# Initialize chatbot với RAG + LLM (fallback to TF-IDF nếu không có dependencies)
USE_RAG = os.getenv('USE_RAG_CHATBOT', 'true').lower() == 'true'
if USE_RAG:
    try:
        from .chatbot_engine_v2 import ChatbotEngine as RAGChatbotEngine
        # Sử dụng file chatbot_knowledge_new.json cho RAG
        chatbot = RAGChatbotEngine(os.path.join(app.root_path, '..', 'data', 'chatbot_knowledge_new.json'), use_rag=True)
    except Exception as e:
        print(f"[chatbot] RAG initialization failed or unavailable, falling back: {e}")
        from .chatbot_engine import ChatbotEngine
        chatbot = ChatbotEngine(os.path.join(app.root_path, '..', 'data', 'chatbot_knowledge_new.json'))
else:
    from .chatbot_engine import ChatbotEngine
    chatbot = ChatbotEngine(os.path.join(app.root_path, '..', 'data', 'chatbot_knowledge_new.json'))

# Ensure data directory exists (for SQLite file and exports)
DATA_DIR = os.path.join(app.root_path, '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def seed_initial_data():
    """Create default admin, a sample department/program and contact settings if missing."""
    # Ensure new columns exist (SQLite, simple migration)
    try:
        with db.engine.connect() as con:
            # Helper to add column if missing
            def ensure_column(table_name: str, column_name: str, column_sql: str):
                info = con.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
                cols = [row[1] for row in info]
                if column_name not in cols:
                    con.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}"))

            # user: email verification fields
            ensure_column('user', 'email_verified', 'BOOLEAN DEFAULT 0')
            ensure_column('user', 'email_verified_at', 'DATETIME')
            # applicant: CCCD field for result lookup
            ensure_column('applicant', 'cccd', 'TEXT')
            # program: tuition_fee may be missing in older DBs
            ensure_column('program', 'tuition_fee', 'REAL')
            # application: admission_method (phương thức xét tuyển)
            ensure_column('application', 'admission_method', 'TEXT')
            # score: score_type để phân biệt loại điểm
            ensure_column('score', 'score_type', 'TEXT')
    except Exception as e:
        # Log and continue; fresh DB will be created by create_all
        print(f"[migrate] skipped/failed ensure columns: {e}")
    # Admin user
    admin = User.query.filter_by(username=Config.ADMIN_USERNAME).first()
    if not admin:
        admin = User(username=Config.ADMIN_USERNAME, email=f"{Config.ADMIN_USERNAME}@example.com", role='admin')
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)

    # Contact settings defaults
    defaults = {
        'contact_address': '123 Đường ABC, Quận XYZ, TP. HCM',
        'contact_email': 'tuyensinh@university.edu.vn',
        'contact_hotline': '1900 xxxx',
    }
    for k, v in defaults.items():
        s = SiteSetting.query.filter_by(key=k).first()
        if not s:
            db.session.add(SiteSetting(key=k, value=v))

    # Sample department and program
    dept = Department.query.first()
    if not dept:
        dept = Department(name='Công nghệ thông tin', description='Đào tạo về CNTT', head='Trưởng khoa A', contact_email='cntt@university.edu.vn')
        db.session.add(dept)
        db.session.flush()  # get id
        prog = Program(name='Kỹ thuật phần mềm', code='7480103', department_id=dept.id, duration='4 năm',
                       description='Đào tạo kỹ sư phần mềm', requirements='Tổ hợp A00, A01', career_prospects='Lập trình, QA, PM', tuition_fee=12000000)
        db.session.add(prog)

    db.session.commit()

# Create tables on import/startup as well (for WSGI and dev server)
try:
    with app.app_context():
        db.create_all()
        # Seed minimal defaults (idempotent)
        seed_initial_data()
except Exception as e:
    # Don't crash the app on startup if DB is temporarily unavailable
    print(f"[db] create_all/seed skipped: {e}")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Bạn không có quyền truy cập trang này!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def verified_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Bỏ qua check khi chạy test
        try:
            from flask import current_app
            if current_app and current_app.config.get('TESTING'):
                return f(*args, **kwargs)
        except Exception:
            pass
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Admins bỏ qua xác thực email cho tác vụ quản trị
        if getattr(current_user, 'role', '') == 'admin':
            return f(*args, **kwargs)
        if not getattr(current_user, 'email_verified', False):
            flash('Vui lòng xác thực email để tiếp tục sử dụng chức năng này.', 'warning')
            return redirect(url_for('view_profile'))
        return f(*args, **kwargs)
    return wrapper

# Public routes
@app.route('/')
def index():
    latest_news = []
    try:
        latest_news = News.query.order_by(News.created_at.desc()).limit(3).all()
    except Exception:
        latest_news = []
    return render_template('index.html', news_list=latest_news)

# Danh sách tin tức & sự kiện
@app.route('/news')
def news_list():
    news_list = News.query.order_by(News.created_at.desc()).all()
    return render_template('news/list.html', news_list=news_list)

# Chi tiết tin tức
@app.route('/news/<int:news_id>')
def news_detail(news_id):
    news = News.query.get_or_404(news_id)
    return render_template('news/detail.html', news=news)
# Tra cứu kết quả tuyển sinh theo CCCD hoặc Số điện thoại (chỉ cho user đã đăng nhập)
@app.route('/results', methods=['GET', 'POST'])
@login_required
def view_results():
    wishes = None
    result = None
    error = None
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query:
            error = 'Vui lòng nhập số CCCD, mã hồ sơ hoặc số điện thoại.'
        else:
            applicant = None
            # Ưu tiên tìm theo CCCD trước, nếu không có thì thử theo phone
            applicant = Applicant.query.filter_by(cccd=query).first()
            if not applicant:
                applicant = Applicant.query.filter_by(phone=query).first()
            if not applicant:
                error = 'Không tìm thấy hồ sơ với thông tin đã nhập.'
            else:
                # Lấy nguyện vọng và kết quả
                app = Application.query.filter_by(applicant_id=applicant.id).order_by(Application.application_date.desc()).first()
                if not app:
                    error = 'Chưa có nguyện vọng nào cho hồ sơ này.'
                else:
                    program = Program.query.get(app.program_id)
                    result = {
                        'full_name': applicant.full_name,
                        'program_name': program.name if program else '',
                        'status': app.status,
                        'submitted_at': app.application_date.strftime('%d/%m/%Y')
                    }
    # Nếu đã đăng nhập, hiển thị bảng nguyện vọng của user
    if current_user.is_authenticated:
        applicant = Applicant.query.filter_by(email=current_user.email).first()
        if applicant:
            wishes = Application.query.filter_by(applicant_id=applicant.id).all()
    return render_template('results/view.html', wishes=wishes, result=result, error=error)

@app.route('/programs')
def programs():
    programs = Program.query.all()
    return render_template('programs.html', programs=programs)

@app.route('/departments')
def departments():
    departments = Department.query.all()
    return render_template('departments.html', departments=departments)

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/contact')
def contact():
    # Pull contact info from SiteSetting
    def get_setting(key, default=''):
        item = SiteSetting.query.filter_by(key=key).first()
        return item.value if item and item.value is not None else default
    contact_info = {
        'address': get_setting('contact_address', '123 Đường ABC, Quận XYZ, TP. HCM'),
        'email': get_setting('contact_email', 'tuyensinh@university.edu.vn'),
        'hotline': get_setting('contact_hotline', '1900 xxxx'),
    }
    return render_template('contact.html', contact_info=contact_info)

# Public info pages
@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/scholarships')
def scholarships():
    return render_template('scholarships.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/forgot-password')
def forgot_password():
    # Minimal page kept for GET compatibility
    return render_template('forgot_password.html')

# Terms of service
@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/resend-verification')
@login_required
def resend_verification():
    if getattr(current_user, 'email_verified', False):
        flash('Tài khoản của bạn đã được xác thực.', 'info')
        return redirect(url_for('index'))
    try:
        token = serializer.dumps({'uid': current_user.id, 'email': current_user.email}, salt='verify-email')
        verify_link = url_for('verify_email', token=token, _external=True)
        html = render_template('emails/verify_email.html', username=current_user.username, verify_link=verify_link)
        sent = send_email('Xác thực email tài khoản', [current_user.email], html)
        if sent:
            flash('Đã gửi lại email xác thực. Vui lòng kiểm tra hộp thư.', 'success')
        else:
            flash('Không gửi được email xác thực. Vui lòng thử lại sau.', 'danger')
    except Exception as e:
        print(f"[verify-email] resend failed: {e}")
        flash('Không gửi được email xác thực. Vui lòng thử lại sau.', 'danger')
    return redirect(url_for('index'))

# Forgot password (POST) and reset password
@app.route('/forgot-password', methods=['POST'])
@rate_limit("3/minute")
def forgot_password_post():
    token = request.form.get('g-recaptcha-response')
    if not verify_recaptcha(token):
        flash('Vui lòng xác nhận bạn không phải robot (reCAPTCHA)!', 'danger')
        return render_template('forgot_password.html')
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    # Avoid user enumeration
    if user:
        token = serializer.dumps({'uid': user.id, 'email': user.email}, salt='reset-password')
        reset_link = url_for('reset_password', token=token, _external=True)
        html = render_template('emails/reset_password.html', username=user.username, reset_link=reset_link)
        send_email('Đặt lại mật khẩu', [user.email], html)
    flash('Nếu email tồn tại, liên kết đặt lại mật khẩu đã được gửi.', 'info')
    return redirect(url_for('login'))

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        data = serializer.loads(token, salt='reset-password', max_age=3600)
        user = User.query.get(data['uid'])
        if not user or user.email != data.get('email'):
            raise BadSignature('Invalid user')
    except (SignatureExpired, BadSignature):
        flash('Link đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.', 'danger')
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if not new_password or len(new_password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự.', 'danger')
            return render_template('reset_password.html')
        if new_password != confirm:
            flash('Mật khẩu nhập lại không khớp.', 'danger')
            return render_template('reset_password.html')
        user.set_password(new_password)
        db.session.commit()
        flash('Đổi mật khẩu thành công. Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html')

# Email verification flow
@app.route('/verify-email/<token>')
def verify_email(token):
    try:
        data = serializer.loads(token, salt='verify-email', max_age=86400)
        user = User.query.get(data['uid'])
        if not user or user.email != data.get('email'):
            raise BadSignature('Invalid user')
        if not getattr(user, 'email_verified', False):
            user.email_verified = True
            user.email_verified_at = datetime.utcnow()
            db.session.commit()
        flash('Xác thực email thành công. Bạn có thể sử dụng đầy đủ chức năng.', 'success')
        return redirect(url_for('login'))
    except (SignatureExpired, BadSignature):
        flash('Link xác thực không hợp lệ hoặc đã hết hạn.', 'danger')
        return redirect(url_for('index'))

# Chatbot API
@app.route('/api/chat', methods=['POST'])
@rate_limit("10/minute")
def chat():
    data = request.get_json()
    user_message = data.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    # Optionally check reCAPTCHA for API if desired
    # token = data.get('recaptcha_token')
    # if not verify_recaptcha(token):
    #     return jsonify({'error': 'reCAPTCHA verification failed'}), 400
    response = chatbot.get_response(user_message)
    interaction = ChatbotInteraction(
        user_input=user_message,
        bot_response=response,
        user_id=current_user.id if current_user.is_authenticated else None
    )
    db.session.add(interaction)
    db.session.commit()
    return jsonify({'response': response})

# Admin routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard_stats():
    if not current_user.role == 'admin':
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    stats = {
        'total_applications': Application.query.count(),
        'total_programs': Program.query.count(),
        'total_departments': Department.query.count(),
        'recent_applications': Application.query.order_by(Application.application_date.desc()).limit(5).all()
    }
    return render_template('admin/dashboard.html', stats=stats)

# Admin: Edit Contact Info

# --- AI API: CV Parsing ---
from flask import send_from_directory
import re

@app.route('/api/cv_parse', methods=['POST'])
@login_required
def api_cv_parse():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    if not allowed_doc(filename):
        return jsonify({'error': 'File type not allowed'}), 400
    # Đọc nội dung file (giả lập, chỉ đọc text)
    try:
        content = file.read().decode('utf-8', errors='ignore')
    except Exception:
        content = ''
    # Trích xuất mẫu (mock): họ tên, email, kỹ năng, học vấn, kinh nghiệm
    # Limit captures to the end of line to avoid spanning into next fields
    name = re.search(r'(?i)ho ten[:\s]*([^\r\n]+)', content)
    email = re.search(r'(?i)email[:\s]*([^\s]+@[\w\.-]+)', content)
    skills = re.findall(r'(?i)ky nang[:\s]*([^\r\n]+)', content)
    education = re.findall(r'(?i)hoc van[:\s]*([^\r\n]+)', content)
    exp = re.findall(r'(?i)kinh nghiem[:\s]*([^\r\n]+)', content)
    result = {
        'name': name.group(1).strip() if name else '',
        # Return only the email value (captured group), not the entire matched expression
        'email': email.group(1) if email else '',
        'skills': skills,
        'education': education,
        'experience': exp
    }
    return jsonify({'parsed': result})
@app.route('/admin/contact', methods=['GET', 'POST'])
@admin_required
def admin_contact():
    def get_setting(key, default=''):
        item = SiteSetting.query.filter_by(key=key).first()
        return item.value if item and item.value is not None else default
    if request.method == 'POST':
        updates = {
            'contact_address': request.form.get('address', ''),
            'contact_email': request.form.get('email', ''),
            'contact_hotline': request.form.get('hotline', ''),
        }
        for k, v in updates.items():
            setting = SiteSetting.query.filter_by(key=k).first()
            if not setting:
                setting = SiteSetting(key=k, value=v)
                db.session.add(setting)
            else:
                setting.value = v
        db.session.commit()
        flash('Cập nhật thông tin liên hệ thành công!', 'success')
        return redirect(url_for('admin_contact'))
    # GET
    form_data = {
        'address': get_setting('contact_address'),
        'email': get_setting('contact_email'),
        'hotline': get_setting('contact_hotline'),
    }
    return render_template('admin/contact_settings.html', form_data=form_data)

# Admin: Email test
@app.route('/admin/email-test', methods=['GET', 'POST'])
@admin_required
def admin_email_test():
    if request.method == 'POST':
        to = request.form.get('to') or current_user.email
        subject = request.form.get('subject') or 'Test SMTP from Admission System'
        body = request.form.get('body') or '<p>Đây là email kiểm tra cấu hình SMTP.</p>'
        ok = send_email(subject, [to], body)
        if ok:
            flash(f'Đã gửi email kiểm tra tới {to}.', 'success')
        else:
            flash('Không gửi được email. Kiểm tra cấu hình SMTP trong .env và thử lại.', 'danger')
        return redirect(url_for('admin_email_test'))
    return render_template('admin/email_test.html')

# Lightweight JSON mail test for quick verification
@app.route('/admin/mail-test')
@admin_required
def admin_mail_test():
    to = request.args.get('to') or (current_user.email if current_user.is_authenticated else None)
    subject = request.args.get('subject') or 'SMTP quick test'
    body = request.args.get('body') or '<p>This is a quick SMTP test from Admission System.</p>'
    if not to:
        return jsonify({'ok': False, 'error': 'missing to parameter'}), 400
    ok = send_email(subject, [to], body)
    return jsonify({'ok': bool(ok), 'to': to})

# Public (token-protected) mail test API
@app.route('/api/mail-test', methods=['GET', 'POST'])
def api_mail_test():
    """Send a quick test email without requiring admin login.
    Security: requires MAIL_TEST_TOKEN via query (?token=...), header (X-Mail-Test-Token), or JSON body {token: ...}.
    Params: to, subject, body (via query or JSON). Returns JSON {ok: bool, to, error?}.
    """
    expected = os.getenv('MAIL_TEST_TOKEN')
    token = (
        request.args.get('token')
        or request.headers.get('X-Mail-Test-Token')
        or ((request.get_json(silent=True) or {}).get('token') if request.is_json else None)
    )
    if not expected or token != expected:
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401

    if request.method == 'POST' and request.is_json:
        data = request.get_json(silent=True) or {}
        to = data.get('to') or request.args.get('to')
        subject = data.get('subject') or 'SMTP API test'
        body = data.get('body') or '<p>This is a quick SMTP test from Admission System.</p>'
    else:
        to = request.args.get('to')
        subject = request.args.get('subject') or 'SMTP API test'
        body = request.args.get('body') or '<p>This is a quick SMTP test from Admission System.</p>'

    if not to:
        return jsonify({'ok': False, 'error': 'missing to parameter'}), 400

    ok = send_email(subject, [to], body)
    return jsonify({'ok': bool(ok), 'to': to})

# Admin: Export CSV of core tables into data/
@app.route('/admin/export-csv')
@admin_required
def admin_export_csv():
    import csv, os
    base_dir = os.path.join(app.root_path, '..', 'data')
    os.makedirs(base_dir, exist_ok=True)
    def write_csv(filename, headers, rows):
        path = os.path.join(base_dir, filename)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
    # Users
    users = User.query.all()
    write_csv('users.csv', ['id','username','email','role','created_at'],
              [[u.id, u.username, u.email, u.role, u.created_at] for u in users])
    # Departments
    depts = Department.query.all()
    write_csv('departments.csv', ['id','name','description','head','contact_email'],
              [[d.id, d.name, d.description, d.head, d.contact_email] for d in depts])
    # Programs
    progs = Program.query.all()
    write_csv('programs.csv', ['id','name','code','department_id','description','duration','requirements','career_prospects','tuition_fee'],
              [[p.id, p.name, p.code, p.department_id, p.description, p.duration, p.requirements, p.career_prospects, p.tuition_fee] for p in progs])
    # Applicants
    appls = Applicant.query.all()
    write_csv('applicants.csv', ['id','full_name','email','phone','date_of_birth','address','high_school','registration_date'],
              [[a.id, a.full_name, a.email, a.phone, a.date_of_birth, a.address, a.high_school, a.registration_date] for a in appls])
    # Applications (wishes)
    apps = Application.query.all()
    write_csv('applications.csv', ['id','applicant_id','program_id','application_date','status'],
              [[ap.id, ap.applicant_id, ap.program_id, ap.application_date, ap.status] for ap in apps])
    # Settings
    settings = SiteSetting.query.all()
    write_csv('settings.csv', ['id','key','value'],
              [[s.id, s.key, s.value] for s in settings])
    flash('Đã xuất dữ liệu CSV vào thư mục data/.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/programs')
@admin_required
def admin_programs():
    programs = Program.query.all()
    departments = Department.query.all()
    return render_template('admin/programs.html', programs=programs, departments=departments)

@app.route('/admin/programs/add', methods=['GET', 'POST'])
@admin_required
def admin_add_program():
    departments = Department.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        department_id = request.form.get('department_id')
        description = request.form.get('description')
        duration = request.form.get('duration')
        requirements = request.form.get('requirements')
        career_prospects = request.form.get('career_prospects')
        tuition_fee = request.form.get('tuition_fee')
        if not name or not code or not department_id:
            flash('Vui lòng nhập đầy đủ thông tin!', 'danger')
            return render_template('admin/add_program.html', departments=departments)
        program = Program(
            name=name, code=code, department_id=department_id, description=description,
            duration=duration, requirements=requirements, career_prospects=career_prospects, tuition_fee=tuition_fee
        )
        db.session.add(program)
        db.session.commit()
        flash('Thêm ngành thành công!', 'success')
        return redirect(url_for('admin_programs'))
    return render_template('admin/add_program.html', departments=departments)

@app.route('/admin/programs/edit/<int:program_id>', methods=['GET','POST'])
@admin_required
def admin_edit_program(program_id):
    program = Program.query.get_or_404(program_id)
    departments = Department.query.all()
    if request.method == 'POST':
        program.name = request.form.get('name')
        program.code = request.form.get('code')
        program.department_id = request.form.get('department_id')
        program.description = request.form.get('description')
        program.duration = request.form.get('duration')
        program.requirements = request.form.get('requirements')
        program.career_prospects = request.form.get('career_prospects')
        tuition = request.form.get('tuition_fee')
        program.tuition_fee = float(tuition) if tuition else None
        db.session.commit()
        flash('Đã cập nhật ngành!', 'success')
        return redirect(url_for('admin_programs'))
    return render_template('admin/edit_program.html', program=program, departments=departments)

@app.route('/admin/programs/delete/<int:program_id>', methods=['POST'])
@admin_required
def admin_delete_program(program_id):
    program = Program.query.get(program_id)
    if program:
        db.session.delete(program)
        db.session.commit()
        flash('Đã xóa ngành!', 'success')
    return redirect(url_for('admin_programs'))

@app.route('/admin/departments')
@admin_required
def admin_departments():
    departments = Department.query.all()
    return render_template('admin/departments.html', departments=departments)

@app.route('/admin/departments/add', methods=['GET', 'POST'])
@admin_required
def admin_add_department():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        head = request.form.get('head')
        contact_email = request.form.get('contact_email')
        if not name:
            flash('Vui lòng nhập tên khoa/viện!', 'danger')
            return render_template('admin/add_department.html')
        department = Department(
            name=name, description=description, head=head, contact_email=contact_email
        )
        db.session.add(department)
        db.session.commit()
        flash('Thêm khoa/viện thành công!', 'success')
        return redirect(url_for('admin_departments'))
    return render_template('admin/add_department.html')

@app.route('/admin/departments/edit/<int:dept_id>', methods=['GET','POST'])
@admin_required
def admin_edit_department(dept_id):
    department = Department.query.get_or_404(dept_id)
    if request.method == 'POST':
        department.name = request.form.get('name')
        department.description = request.form.get('description')
        department.head = request.form.get('head')
        department.contact_email = request.form.get('contact_email')
        db.session.commit()
        flash('Đã cập nhật khoa/viện!', 'success')
        return redirect(url_for('admin_departments'))
    return render_template('admin/edit_department.html', dept=department)
@app.route('/admin/departments/delete/<int:dept_id>', methods=['POST'])
@admin_required
def admin_delete_department(dept_id):
    department = Department.query.get(dept_id)
    if department:
        db.session.delete(department)
        db.session.commit()
        flash('Đã xóa khoa/viện!', 'success')
    return redirect(url_for('admin_departments'))

@app.route('/admin/applications')
@admin_required
def admin_applications():
    applications = Application.query.order_by(Application.application_date.desc()).all()
    return render_template('admin/applications.html', applications=applications)


@app.route('/admin/applications/approve/<int:app_id>', methods=['POST'])
@admin_required
def admin_approve_application(app_id):
    application = Application.query.get(app_id)
    if application:
        application.status = 'Accepted'
        db.session.commit()
        flash('Đã duyệt hồ sơ (Đỗ)!', 'success')
    return redirect(url_for('admin_applications'))

@app.route('/admin/applications/reject/<int:app_id>', methods=['POST'])
@admin_required
def admin_reject_application(app_id):
    application = Application.query.get(app_id)
    if application:
        application.status = 'Rejected'
        db.session.commit()
        flash('Đã từ chối hồ sơ (Trượt)!', 'warning')
    return redirect(url_for('admin_applications'))

@app.route('/admin/statistics')
@admin_required
def admin_statistics():
    total_applicants = Applicant.query.count()
    total_applications = Application.query.count()
    total_accepted = Application.query.filter_by(status='Accepted').count()
    total_rejected = Application.query.filter_by(status='Rejected').count()
    # Thống kê theo ngành
    from sqlalchemy import func, case
    stats_by_program = db.session.query(
        Program.name,
        func.count(Application.id),
        func.sum(case((Application.status == 'Accepted', 1), else_=0)),
        func.sum(case((Application.status == 'Rejected', 1), else_=0))
    ).join(Application, Application.program_id == Program.id, isouter=True)
    stats_by_program = stats_by_program.group_by(Program.id).all()
    return render_template('admin/statistics.html',
        total_applicants=total_applicants,
        total_applications=total_applications,
        total_accepted=total_accepted,
        total_rejected=total_rejected,
        stats_by_program=stats_by_program)

# ============================================================================
# ADMIN USER MANAGEMENT ROUTES
# ============================================================================

@app.route('/admin/users')
@admin_required
def admin_users():
    """Quản lý tài khoản người dùng"""
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.contains(search)) | 
            (User.email.contains(search))
        )
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    users = query.order_by(User.created_at.desc()).all()
    
    return render_template('admin/users.html', 
                         users=users, 
                         search=search, 
                         role_filter=role_filter)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@admin_required
def admin_add_user():
    """Thêm tài khoản mới"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        email_verified = request.form.get('email_verified') == 'on'
        
        # Validate
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            return render_template('admin/add_user.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng!', 'danger')
            return render_template('admin/add_user.html')
        
        # Create user
        user = User(
            username=username,
            email=email,
            role=role,
            email_verified=email_verified
        )
        user.set_password(password)
        
        if email_verified:
            user.email_verified_at = datetime.utcnow()
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Đã tạo tài khoản {username} thành công!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/add_user.html')

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    """Chỉnh sửa tài khoản"""
    user = User.query.get_or_404(user_id)
    
    # Không cho phép admin tự sửa role của chính mình
    if user.id == current_user.id and request.method == 'POST':
        new_role = request.form.get('role')
        if new_role != user.role:
            flash('Bạn không thể thay đổi role của chính mình!', 'warning')
            return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.role = request.form.get('role', 'user')
        
        # Update email verification
        email_verified = request.form.get('email_verified') == 'on'
        if email_verified and not user.email_verified:
            user.email_verified = True
            user.email_verified_at = datetime.utcnow()
        elif not email_verified and user.email_verified:
            user.email_verified = False
            user.email_verified_at = None
        
        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash(f'Đã cập nhật tài khoản {user.username}!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/edit_user.html', user=user)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Xóa tài khoản"""
    user = User.query.get_or_404(user_id)
    
    # Không cho phép xóa chính mình
    if user.id == current_user.id:
        flash('Bạn không thể xóa tài khoản của chính mình!', 'danger')
        return redirect(url_for('admin_users'))
    
    # Không cho phép xóa admin cuối cùng
    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash('Không thể xóa admin duy nhất trong hệ thống!', 'danger')
            return redirect(url_for('admin_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Đã xóa tài khoản {username}!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/toggle-status/<int:user_id>', methods=['POST'])
@admin_required
def admin_toggle_user_status(user_id):
    """Bật/tắt xác thực email"""
    user = User.query.get_or_404(user_id)
    
    user.email_verified = not user.email_verified
    if user.email_verified:
        user.email_verified_at = datetime.utcnow()
    else:
        user.email_verified_at = None
    
    db.session.commit()
    
    status = "đã xác thực" if user.email_verified else "chưa xác thực"
    flash(f'Tài khoản {user.username} {status}!', 'success')
    return redirect(url_for('admin_users'))

# ============================================================================
# END ADMIN USER MANAGEMENT ROUTES
# ============================================================================

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
@rate_limit("5/minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        token = request.form.get('g-recaptcha-response')
        if not verify_recaptcha(token):
            flash('Vui lòng xác nhận bạn không phải robot (reCAPTCHA)!', 'danger')
            return render_template('login.html')
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Sai thông tin đăng nhập!', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất!')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@rate_limit("3/minute")
def register():
    if request.method == 'POST':
        token = request.form.get('g-recaptcha-response')
        if not verify_recaptcha(token):
            flash('Vui lòng xác nhận bạn không phải robot (reCAPTCHA)!', 'danger')
            return render_template('register.html')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not username or not email or not password:
            flash('Vui lòng điền đầy đủ thông tin!', 'danger')
            return render_template('register.html')
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Tên đăng nhập hoặc email đã tồn tại!', 'danger')
            return render_template('register.html')
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # Send verification email
        try:
            token = serializer.dumps({'uid': user.id, 'email': user.email}, salt='verify-email')
            verify_link = url_for('verify_email', token=token, _external=True)
            html = render_template('emails/verify_email.html', username=user.username, verify_link=verify_link)
            sent = send_email('Xác thực email tài khoản', [user.email], html)
            if sent:
                flash('Đăng ký thành công! Kiểm tra email để xác thực tài khoản.', 'success')
            else:
                flash('Đăng ký thành công! (Không gửi được email xác thực, thử lại sau)', 'warning')
        except Exception as e:
            print(f"[verify-email] send failed: {e}")
            flash('Đăng ký thành công! (Không gửi được email xác thực, thử lại sau)', 'warning')
        return redirect(url_for('login'))
    return render_template('register.html')

# Profile routes
@app.route('/profile')
@login_required
def view_profile():
    applicant = Applicant.query.filter_by(email=current_user.email).first()
    return render_template('profile/view.html', applicant=applicant)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    applicant = Applicant.query.filter_by(email=current_user.email).first()
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        date_of_birth_str = request.form.get('date_of_birth')
        address = request.form.get('address')
        high_school = request.form.get('high_school')
        
        # Convert date string to date object
        date_of_birth = None
        if date_of_birth_str:
            try:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Ngày sinh không hợp lệ!', 'danger')
                return render_template('profile/edit.html', applicant=applicant)
        
        if not applicant:
            applicant = Applicant(
                full_name=full_name,
                email=current_user.email,
                phone=phone,
                date_of_birth=date_of_birth,
                address=address,
                high_school=high_school
            )
            db.session.add(applicant)
        else:
            applicant.full_name = full_name
            applicant.phone = phone
            applicant.date_of_birth = date_of_birth
            applicant.address = address
            applicant.high_school = high_school
        db.session.commit()
        flash('Cập nhật hồ sơ thành công!', 'success')
        return redirect(url_for('view_profile'))
    return render_template('profile/edit.html', applicant=applicant)

@app.route('/profile/delete', methods=['POST'])
@login_required
def delete_profile():
    applicant = Applicant.query.filter_by(email=current_user.email).first()
    if applicant:
        db.session.delete(applicant)
        db.session.commit()
        flash('Đã xóa hồ sơ!', 'success')
    return redirect(url_for('view_profile'))

# Wishes routes
@app.route('/wishes')
@login_required
@verified_required
def view_wishes():
    applicant = Applicant.query.filter_by(email=current_user.email).first()
    if not applicant:
        flash('Bạn cần tạo hồ sơ trước khi nộp nguyện vọng!', 'warning')
        return redirect(url_for('edit_profile'))
    wishes = Application.query.filter_by(applicant_id=applicant.id).all()
    programs = Program.query.all()
    return render_template('wishes/view.html', wishes=wishes, programs=programs)

@app.route('/wishes/add', methods=['GET', 'POST'])
@login_required
@verified_required
def add_wish():
    applicant = Applicant.query.filter_by(email=current_user.email).first()
    if not applicant:
        flash('Bạn cần tạo hồ sơ trước khi nộp nguyện vọng!', 'warning')
        return redirect(url_for('edit_profile'))
    programs = Program.query.all()
    if request.method == 'POST':
        program_id = request.form.get('program_id')
        admission_method = request.form.get('admission_method')
        if not program_id:
            flash('Vui lòng chọn ngành!', 'danger')
            return render_template('wishes/add.html', programs=programs)
        if not admission_method:
            flash('Vui lòng chọn phương thức xét tuyển!', 'danger')
            return render_template('wishes/add.html', programs=programs)
        
        # Tạo nguyện vọng
        wish = Application(applicant_id=applicant.id, program_id=program_id, admission_method=admission_method)
        db.session.add(wish)
        db.session.flush()  # Get application ID
        
        # Lưu điểm tùy theo phương thức
        if admission_method == 'Xét theo điểm thi tốt nghiệp THPT':
            # Điểm 3 môn cơ bản
            score_toan = request.form.get('score_toan')
            score_van = request.form.get('score_van')
            score_ngoaingu = request.form.get('score_ngoaingu')
            # Điểm tổ hợp
            score_mon1 = request.form.get('score_mon1')
            score_mon2 = request.form.get('score_mon2')
            score_mon3 = request.form.get('score_mon3')
            score_tohop = request.form.get('score_tohop')
            
            if score_toan:
                db.session.add(Score(application_id=wish.id, subject='Toán', score=float(score_toan), score_type='thi_thpt'))
            if score_van:
                db.session.add(Score(application_id=wish.id, subject='Văn', score=float(score_van), score_type='thi_thpt'))
            if score_ngoaingu:
                db.session.add(Score(application_id=wish.id, subject='Ngoại ngữ', score=float(score_ngoaingu), score_type='thi_thpt'))
            if score_tohop and score_mon1 and score_mon2 and score_mon3:
                db.session.add(Score(application_id=wish.id, subject=f'Tổ hợp {score_tohop} - Môn 1', score=float(score_mon1), score_type='thi_thpt'))
                db.session.add(Score(application_id=wish.id, subject=f'Tổ hợp {score_tohop} - Môn 2', score=float(score_mon2), score_type='thi_thpt'))
                db.session.add(Score(application_id=wish.id, subject=f'Tổ hợp {score_tohop} - Môn 3', score=float(score_mon3), score_type='thi_thpt'))
        
        elif admission_method == 'Xét học bạ THPT':
            score_lop10 = request.form.get('score_lop10')
            score_lop11 = request.form.get('score_lop11')
            score_lop12 = request.form.get('score_lop12')
            
            if score_lop10:
                db.session.add(Score(application_id=wish.id, subject='Điểm TB lớp 10', score=float(score_lop10), score_type='hoc_ba'))
            if score_lop11:
                db.session.add(Score(application_id=wish.id, subject='Điểm TB lớp 11', score=float(score_lop11), score_type='hoc_ba'))
            if score_lop12:
                db.session.add(Score(application_id=wish.id, subject='Điểm TB lớp 12', score=float(score_lop12), score_type='hoc_ba'))
        
        elif admission_method == 'Xét theo điểm ĐGNL / đánh giá năng lực':
            score_dgnl = request.form.get('score_dgnl')
            score_dgnl_type = request.form.get('score_dgnl_type', 'ĐHQG HCM')
            
            if score_dgnl:
                db.session.add(Score(application_id=wish.id, subject=f'ĐGNL ({score_dgnl_type})', score=float(score_dgnl), score_type='dgnl'))
        
        elif admission_method == 'Xét tuyển thẳng / ưu tiên':
            score_uutien_type = request.form.get('score_uutien_type')
            score_uutien_desc = request.form.get('score_uutien_desc', '')
            
            if score_uutien_type:
                # Lưu dạng text mô tả
                db.session.add(Score(application_id=wish.id, subject=score_uutien_type, score=1.0, score_type='uutien'))
        
        db.session.commit()
        flash('Nộp nguyện vọng thành công!', 'success')
        return redirect(url_for('view_wishes'))
    return render_template('wishes/add.html', programs=programs)

@app.route('/wishes/delete/<int:wish_id>', methods=['POST'])
@login_required
@verified_required
def delete_wish(wish_id):
    applicant = Applicant.query.filter_by(email=current_user.email).first()
    wish = Application.query.filter_by(id=wish_id, applicant_id=applicant.id).first()
    if wish:
        db.session.delete(wish)
        db.session.commit()
        flash('Đã xóa nguyện vọng!', 'success')
    return redirect(url_for('view_wishes'))

# (Removed duplicate /results route to avoid endpoint conflict)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# ============================================================================
# NOTIFICATION API ROUTES
# ============================================================================

@app.route('/api/notifications')
@login_required
def get_notifications():
    """Get all notifications for current user"""
    from .models import Notification
    
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc())\
        .limit(50)\
        .all()
    
    unread_count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    return jsonify({
        'notifications': [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.type,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
            'link': n.link
        } for n in notifications],
        'unread_count': unread_count
    })

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    from .models import Notification
    
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({'ok': True})
    
    return jsonify({'ok': False, 'error': 'Notification not found'}), 404

@app.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    from .models import Notification
    
    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()
    
    return jsonify({'ok': True})

@app.route('/notifications')
@login_required
def notifications_page():
    """View all notifications page"""
    from .models import Notification
    
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc())\
        .all()
    
    return render_template('notifications/view.html', notifications=notifications)

def create_notification(user_id, title, message, notification_type='info', link=None):
    """Helper function to create a notification
    
    Args:
        user_id: ID of the user to notify
        title: Notification title
        message: Notification message
        notification_type: Type (info, success, warning, error)
        link: Optional link to related resource
    """
    from .models import Notification
    
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type,
        link=link
    )
    db.session.add(notif)
    db.session.commit()
    return notif

# ============================================================================
# DOCUMENT MANAGEMENT ROUTES
# ============================================================================

@app.route('/profile/documents', methods=['GET', 'POST'])
@login_required
@verified_required
def manage_documents():
    applicant = Applicant.query.filter_by(email=current_user.email).first()
    if not applicant:
        flash('Bạn cần tạo hồ sơ trước khi tải lên tài liệu!', 'warning')
        return redirect(url_for('edit_profile'))
    from .models import ApplicantDocument
    if request.method == 'POST':
        file = request.files.get('document')
        if not file or file.filename == '':
            flash('Vui lòng chọn tệp để tải lên.', 'danger')
            return redirect(url_for('manage_documents'))
        if not allowed_doc(file.filename):
            flash('Định dạng tệp không hợp lệ.', 'danger')
            return redirect(url_for('manage_documents'))
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > MAX_DOC_SIZE:
            flash('Tệp vượt quá dung lượng cho phép (5MB).', 'danger')
            return redirect(url_for('manage_documents'))
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(app.root_path, '..', 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        save_name = f"{applicant.id}_{timestamp}_{filename}"
        file_path = os.path.join('uploads', save_name)
        abs_path = os.path.join(app.root_path, '..', 'static', file_path)
        file.save(abs_path)
        doc = ApplicantDocument(
            applicant_id=applicant.id,
            filename=filename,
            file_path=file_path.replace('\\', '/'),
            file_type=file.mimetype,
            file_size=size
        )
        db.session.add(doc)
        db.session.commit()
        flash('Tải lên tài liệu thành công!', 'success')
        return redirect(url_for('manage_documents'))
    documents = ApplicantDocument.query.filter_by(applicant_id=applicant.id).order_by(ApplicantDocument.uploaded_at.desc()).all()
    return render_template('profile/documents.html', documents=documents)


@app.route('/profile/documents/delete/<int:doc_id>', methods=['POST'])
@login_required
@verified_required
def delete_document(doc_id):
    from .models import ApplicantDocument
    doc = ApplicantDocument.query.get(doc_id)
    applicant = Applicant.query.filter_by(email=current_user.email).first()
    if doc and applicant and doc.applicant_id == applicant.id:
        # Remove file from disk
        abs_path = os.path.join(app.root_path, '..', 'static', doc.file_path)
        try:
            if os.path.exists(abs_path):
                os.remove(abs_path)
        except Exception as e:
            print(f"[delete_document] file remove failed: {e}")
        db.session.delete(doc)
        db.session.commit()
        flash('Đã xóa tài liệu.', 'success')
    else:
        flash('Không tìm thấy tài liệu.', 'danger')
    return redirect(url_for('manage_documents'))

# ============================================================================
# END NOTIFICATION ROUTES
# ============================================================================

# ============================================================================
# AI ADVISOR ROUTES - Tư vấn ngành học thông minh
# ============================================================================

@app.route('/api/suggest-programs', methods=['POST'])
def suggest_programs():
    """
    API tư vấn ngành học phù hợp dựa trên điểm số
    Input: {
        "scores": {
            "toan": 8.5,
            "van": 7.5,
            "ngoai_ngu": 8.0,
            "ly": 9.0,
            "hoa": 8.5,
            "sinh": 7.0
        },
        "method": "thpt" | "hoc_ba" | "dgnl" | "tuyen_thang"
    }
    Output: List of suggested programs with admission probability
    """
    try:
        data = request.get_json()
        scores = data.get('scores', {})
        method = data.get('method', 'thpt')
        
        # Tính điểm các khối xét tuyển
        combinations = {}
        
        if method == 'thpt':
            # Khối A00: Toán, Lý, Hóa
            if all(k in scores for k in ['toan', 'ly', 'hoa']):
                combinations['A00'] = scores['toan'] + scores['ly'] + scores['hoa']
            
            # Khối A01: Toán, Lý, Anh
            if all(k in scores for k in ['toan', 'ly', 'ngoai_ngu']):
                combinations['A01'] = scores['toan'] + scores['ly'] + scores['ngoai_ngu']
            
            # Khối B00: Toán, Hóa, Sinh
            if all(k in scores for k in ['toan', 'hoa', 'sinh']):
                combinations['B00'] = scores['toan'] + scores['hoa'] + scores['sinh']
            
            # Khối C00: Văn, Sử, Địa (giả sử không có sử, địa trong input)
            # Khối D01: Toán, Văn, Anh
            if all(k in scores for k in ['toan', 'van', 'ngoai_ngu']):
                combinations['D01'] = scores['toan'] + scores['van'] + scores['ngoai_ngu']
        
        elif method == 'hoc_ba':
            # Điểm trung bình 3 năm
            tb_3_nam = scores.get('tb_3_nam', 0)
            # Quy đổi sang thang 30 (giả sử mỗi môn ~ 10 điểm)
            combinations['TB_3_NAM'] = tb_3_nam * 3
        
        elif method == 'dgnl':
            # Quy đổi điểm ĐGNL (thang 1200) sang thang 30
            dgnl_score = scores.get('dgnl', 0)
            combinations['DGNL'] = (dgnl_score / 1200) * 30
        
        # Lấy tất cả chương trình đào tạo
        programs = Program.query.all()
        suggestions = []
        
        for program in programs:
            # Lấy điểm chuẩn năm gần nhất
            latest_quota = AdmissionQuota.query.filter_by(
                program_id=program.id
            ).order_by(AdmissionQuota.year.desc()).first()
            
            if not latest_quota or not latest_quota.minimum_score:
                continue
            
            # So sánh điểm của thí sinh với điểm chuẩn
            min_score = latest_quota.minimum_score
            max_user_score = max(combinations.values()) if combinations else 0
            
            # Tính xác suất đỗ
            if max_user_score >= min_score + 2:
                probability = 95
                status = 'very_high'
            elif max_user_score >= min_score + 1:
                probability = 85
                status = 'high'
            elif max_user_score >= min_score:
                probability = 70
                status = 'medium'
            elif max_user_score >= min_score - 0.5:
                probability = 50
                status = 'low'
            else:
                probability = 20
                status = 'very_low'
            
            # Tìm khối xét tuyển phù hợp nhất
            best_combination = None
            best_score = 0
            for comb_name, comb_score in combinations.items():
                if comb_score > best_score:
                    best_score = comb_score
                    best_combination = comb_name
            
            suggestions.append({
                'id': program.id,
                'name': program.name,
                'code': program.code,
                'department': program.department.name if program.department else 'N/A',
                'minimum_score': min_score,
                'your_score': round(max_user_score, 2),
                'difference': round(max_user_score - min_score, 2),
                'probability': probability,
                'status': status,
                'best_combination': best_combination,
                'year': latest_quota.year,
                'quota': latest_quota.quota,
                'tuition_fee': program.tuition_fee,
                'duration': program.duration
            })
        
        # Sắp xếp theo xác suất đỗ
        suggestions.sort(key=lambda x: x['probability'], reverse=True)
        
        # Trả về top 10
        return jsonify({
            'success': True,
            'suggestions': suggestions[:10],
            'total': len(suggestions),
            'method': method,
            'combinations': {k: round(v, 2) for k, v in combinations.items()}
        })
    
    except Exception as e:
        print(f"[suggest_programs] Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/advisor', endpoint='advisor_page')
def advisor():
    """Trang tư vấn ngành học"""
    return render_template('advisor.html')


@app.route('/api/admission-statistics', methods=['GET'])
def admission_statistics():
    """API thống kê điểm chuẩn các năm"""
    try:
        program_id = request.args.get('program_id', type=int)
        
        if program_id:
            # Lấy điểm chuẩn của một ngành qua các năm
            quotas = AdmissionQuota.query.filter_by(
                program_id=program_id
            ).order_by(AdmissionQuota.year).all()
            
            program = Program.query.get(program_id)
            
            return jsonify({
                'success': True,
                'program': {
                    'id': program.id,
                    'name': program.name,
                    'code': program.code
                } if program else None,
                'history': [{
                    'year': q.year,
                    'minimum_score': q.minimum_score,
                    'quota': q.quota,
                    'actual_intake': q.actual_intake
                } for q in quotas]
            })
        else:
            # Lấy tổng quan tất cả các ngành
            programs = Program.query.all()
            overview = []
            
            for program in programs:
                latest = AdmissionQuota.query.filter_by(
                    program_id=program.id
                ).order_by(AdmissionQuota.year.desc()).first()
                
                if latest:
                    overview.append({
                        'id': program.id,
                        'name': program.name,
                        'code': program.code,
                        'department': program.department.name if program.department else 'N/A',
                        'latest_year': latest.year,
                        'minimum_score': latest.minimum_score,
                        'quota': latest.quota
                    })
            
            return jsonify({
                'success': True,
                'programs': overview
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# END AI ADVISOR ROUTES
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_initial_data()
    app.run(debug=True, use_reloader=False)
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from .models import db, User, Department, Program, AdmissionQuota
import json
import os

def init_db(app):
    """Initialize the database and create tables"""
    with app.app_context():
        db.create_all()

def populate_sample_data(app):
    """Populate the database with sample data"""
    with app.app_context():
        # Create departments
        departments = [
            {
                'name': 'Khoa Công nghệ Thông tin',
                'description': 'Đào tạo các chuyên ngành về công nghệ thông tin và khoa học máy tính',
                'head': 'PGS.TS. Nguyễn Văn A',
                'contact_email': 'cntt@university.edu.vn'
            },
            {
                'name': 'Khoa Kinh tế',
                'description': 'Đào tạo các chuyên ngành về kinh tế và quản trị kinh doanh',
                'head': 'TS. Trần Thị B',
                'contact_email': 'kinhte@university.edu.vn'
            }
        ]

        for dept_data in departments:
            dept = Department(**dept_data)
            db.session.add(dept)
        db.session.commit()

        # Create programs
        programs = [
            {
                'name': 'Kỹ thuật phần mềm',
                'code': 'KTPM',
                'department_id': 1,
                'description': 'Chương trình đào tạo kỹ sư phần mềm chuyên nghiệp',
                'duration': '4 năm',
                'requirements': 'Tốt nghiệp THPT, điểm thi đại học >= 24',
                'career_prospects': 'Lập trình viên, Kiến trúc sư phần mềm, Quản lý dự án',
                'tuition_fee': 25000000
            },
            {
                'name': 'Quản trị kinh doanh',
                'code': 'QTKD',
                'department_id': 2,
                'description': 'Chương trình đào tạo chuyên sâu về quản trị doanh nghiệp',
                'duration': '4 năm',
                'requirements': 'Tốt nghiệp THPT, điểm thi đại học >= 23',
                'career_prospects': 'Quản lý doanh nghiệp, Chuyên viên tư vấn, Khởi nghiệp',
                'tuition_fee': 23000000
            }
        ]

        for prog_data in programs:
            prog = Program(**prog_data)
            db.session.add(prog)
        db.session.commit()

        # Create admission quotas
        quotas = [
            {
                'program_id': 1,
                'year': 2023,
                'quota': 120,
                'minimum_score': 24.0,
                'actual_intake': 115
            },
            {
                'program_id': 2,
                'year': 2023,
                'quota': 150,
                'minimum_score': 23.0,
                'actual_intake': 145
            }
        ]

        for quota_data in quotas:
            quota = AdmissionQuota(**quota_data)
            db.session.add(quota)
        db.session.commit()

        # Create admin user
        admin = User(
            username='admin',
            email='admin@university.edu.vn',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

def load_chatbot_knowledge(app):
    """Load chatbot knowledge base from JSON file"""
    knowledge_base_path = app.config['CHATBOT_KNOWLEDGE_BASE']
    
    if not os.path.exists(knowledge_base_path):
        # Create sample knowledge base
        knowledge_base = {
            "intents": [
                {
                    "tag": "greeting",
                    "patterns": [
                        "Xin chào",
                        "Chào bạn",
                        "Hi",
                        "Hello"
                    ],
                    "responses": [
                        "Xin chào! Tôi có thể giúp gì cho bạn?",
                        "Chào bạn! Bạn cần tư vấn về vấn đề gì?",
                        "Rất vui được gặp bạn! Tôi có thể giúp bạn tìm hiểu về chương trình đào tạo."
                    ]
                },
                {
                    "tag": "programs",
                    "patterns": [
                        "Có những ngành nào",
                        "Các chương trình đào tạo",
                        "Ngành học",
                        "Chuyên ngành"
                    ],
                    "responses": [
                        "Trường có nhiều ngành đào tạo như: CNTT, Kinh tế, Kế toán... Bạn quan tâm đến ngành nào?",
                        "Hiện tại trường đang đào tạo các ngành: CNTT, Kinh tế, Kế toán. Bạn muốn tìm hiểu thêm về ngành nào?"
                    ]
                }
            ]
        }
        
        os.makedirs(os.path.dirname(knowledge_base_path), exist_ok=True)
        with open(knowledge_base_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, ensure_ascii=False, indent=4)

def init_app(app):
    """Initialize the application with database and sample data"""
    init_db(app)
    populate_sample_data(app)
    load_chatbot_knowledge(app)
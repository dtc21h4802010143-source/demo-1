"""
Import applications (nguyện vọng) từ dữ liệu mẫu
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

from backend.app import app, db
from backend.models import Applicant, Application, Program, Score

def import_applications():
    """Import applications from sample data"""
    
    # Dữ liệu mẫu
    applications_data = [
        {"name": "Nguyễn Văn An", "email": "an.nguyen@example.com", "phone": "0901234567", "gender": "Nam", "year": 1990, "score": 21.50, "program": "Công nghệ thông tin", "method": "Xét điểm thi THPT"},
        {"name": "Trần Thị Bích", "email": "bich.tran@example.com", "phone": "0912345678", "gender": "Nữ", "year": 1995, "score": 24.75, "program": "Khoa học máy tính", "method": "Xét học bạ THPT"},
        {"name": "Lê Minh Cường", "email": "cuong.le@example.com", "phone": "0987654321", "gender": "Nam", "year": 1988, "score": 18.20, "program": "Kỹ thuật phần mềm", "method": "Xét điểm thi THPT"},
        {"name": "Phạm Ngọc Dung", "email": "dung.pham@example.com", "phone": "0381234567", "gender": "Nữ", "year": 2000, "score": 27.80, "program": "Truyền thông đa phương tiện", "method": "Xét học bạ THPT"},
        {"name": "Hoàng Tuấn Em", "email": "em.hoang@example.com", "phone": "0398765432", "gender": "Nam", "year": 1992, "score": 22.00, "program": "Thương mại điện tử", "method": "Xét điểm thi ĐGNL"},
        {"name": "Huỳnh Anh Hà", "email": "ha.huynh@example.com", "phone": "0701234567", "gender": "Nữ", "year": 1997, "score": 25.15, "program": "Marketing số", "method": "Xét học bạ THPT"},
        {"name": "Phan Đức Hùng", "email": "hung.phan@example.com", "phone": "0867654321", "gender": "Nam", "year": 1985, "score": 17.50, "program": "Công nghệ ô tô", "method": "Xét điểm thi THPT"},
        {"name": "Vũ Thị Lan", "email": "lan.vu@example.com", "phone": "0934567890", "gender": "Nữ", "year": 1998, "score": 26.90, "program": "Thiết kế đồ họa", "method": "Xét học bạ THPT"},
        {"name": "Võ Minh Long", "email": "long.vo@example.com", "phone": "0945678901", "gender": "Nam", "year": 2001, "score": 23.45, "program": "An ninh mạng", "method": "Xét điểm thi THPT"},
        {"name": "Đặng Ngọc Mai", "email": "mai.dang@example.com", "phone": "0831234567", "gender": "Nữ", "year": 1993, "score": 20.85, "program": "Quản lý logistics và chuỗi cung ứng", "method": "Xét học bạ THPT"},
    ]
    
    with app.app_context():
        print("="*60)
        print("  IMPORT APPLICATIONS (NGUYỆN VỌNG)")
        print("="*60)
        
        # Lấy tất cả programs
        programs = {p.name: p for p in Program.query.all()}
        print(f"📋 Found {len(programs)} programs in database")
        
        imported = 0
        skipped = 0
        errors = 0
        
        for data in applications_data:
            try:
                # Tìm hoặc tạo applicant
                applicant = Applicant.query.filter_by(email=data['email']).first()
                
                if not applicant:
                    # Tạo applicant mới
                    birth_year = data['year']
                    applicant = Applicant(
                        full_name=data['name'],
                        email=data['email'],
                        phone=data['phone'],
                        date_of_birth=datetime(birth_year, 1, 1).date(),
                        address=f"Địa chỉ của {data['name']}",
                        high_school=f"THPT {data['name'].split()[-1]}"
                    )
                    db.session.add(applicant)
                    db.session.flush()
                    print(f"  ➕ Created applicant: {data['name']}")
                else:
                    print(f"  🔄 Found existing applicant: {data['name']}")
                
                # Tìm program
                program = programs.get(data['program'])
                if not program:
                    print(f"  ⚠️  Program not found: {data['program']}")
                    errors += 1
                    continue
                
                # Kiểm tra xem đã có application chưa
                existing_app = Application.query.filter_by(
                    applicant_id=applicant.id,
                    program_id=program.id
                ).first()
                
                if existing_app:
                    print(f"  ⏭️  Application already exists: {data['name']} -> {data['program']}")
                    skipped += 1
                    continue
                
                # Tạo application
                application = Application(
                    applicant_id=applicant.id,
                    program_id=program.id,
                    admission_method=data['method'],
                    status='Submitted'
                )
                db.session.add(application)
                db.session.flush()
                
                # Thêm điểm số
                total_score = data['score']
                
                if 'THPT' in data['method']:
                    # Điểm thi THPT - chia đều cho 3 môn
                    score_per_subject = total_score / 3
                    db.session.add(Score(
                        application_id=application.id,
                        subject='Toán',
                        score=round(score_per_subject, 2),
                        score_type='thi_thpt'
                    ))
                    db.session.add(Score(
                        application_id=application.id,
                        subject='Văn',
                        score=round(score_per_subject, 2),
                        score_type='thi_thpt'
                    ))
                    db.session.add(Score(
                        application_id=application.id,
                        subject='Ngoại ngữ',
                        score=round(score_per_subject, 2),
                        score_type='thi_thpt'
                    ))
                elif 'học bạ' in data['method']:
                    # Điểm học bạ - trung bình
                    avg_score = total_score / 3
                    db.session.add(Score(
                        application_id=application.id,
                        subject='Điểm TB lớp 12',
                        score=round(avg_score, 2),
                        score_type='hoc_ba'
                    ))
                elif 'ĐGNL' in data['method']:
                    # Điểm ĐGNL
                    db.session.add(Score(
                        application_id=application.id,
                        subject='ĐGNL (ĐHQG HCM)',
                        score=total_score,
                        score_type='dgnl'
                    ))
                
                print(f"  ✅ Added application: {data['name']} -> {data['program']} ({data['method']}) - Score: {total_score}")
                imported += 1
                
            except Exception as e:
                print(f"  ❌ Error processing {data['name']}: {e}")
                errors += 1
                db.session.rollback()
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            print("\n" + "="*60)
            print("✅ Import completed!")
            print(f"   - Imported: {imported} applications")
            print(f"   - Skipped: {skipped} (already exists)")
            print(f"   - Errors: {errors}")
            print("="*60)
            
            # Statistics
            total_applicants = Applicant.query.count()
            total_applications = Application.query.count()
            print(f"\n📊 Database Summary:")
            print(f"   Total Applicants: {total_applicants}")
            print(f"   Total Applications: {total_applications}")
            print("="*60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing to database: {e}")

if __name__ == '__main__':
    import_applications()

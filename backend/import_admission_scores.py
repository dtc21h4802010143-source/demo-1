"""
Script import dữ liệu điểm chuẩn và phương thức xét tuyển vào database
"""
import os
import sys
import csv

# Add parent directory to path for proper imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import app
from backend.models import db, Program, AdmissionScore, AdmissionMethod

def import_admission_scores():
    """Import điểm chuẩn từ file CSV"""
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'admission_scores.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ Không tìm thấy file: {csv_path}")
        return
    
    print(f"📂 Đang import từ: {csv_path}")
    
    with app.app_context():
        # Đảm bảo các bảng đã được tạo
        db.create_all()
        imported_count = 0
        skipped_count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                program_name = row['program_name'].strip()
                notes = row.get('notes', '').strip()
                
                # Tìm Program matching (nếu có)
                program = Program.query.filter(
                    db.func.lower(Program.name).like(f"%{program_name.lower()}%")
                ).first()
                
                program_id = program.id if program else None
                
                # Import điểm theo từng năm
                for year_col in ['year_2025', 'year_2024', 'year_2023', 'year_2022']:
                    year = int(year_col.split('_')[1])
                    score_str = row[year_col].strip()
                    
                    if score_str and score_str != '-':
                        try:
                            score = float(score_str)
                            
                            # Kiểm tra xem đã tồn tại chưa
                            existing = AdmissionScore.query.filter_by(
                                program_name=program_name,
                                year=year
                            ).first()
                            
                            if existing:
                                # Update existing record
                                existing.admission_score = score
                                existing.program_id = program_id
                                existing.notes = notes
                                skipped_count += 1
                            else:
                                # Create new record
                                admission_score = AdmissionScore(
                                    program_id=program_id,
                                    program_name=program_name,
                                    year=year,
                                    admission_score=score,
                                    notes=notes
                                )
                                db.session.add(admission_score)
                                imported_count += 1
                        
                        except ValueError:
                            print(f"⚠️  Lỗi chuyển đổi điểm: {program_name} - {year} - {score_str}")
        
        db.session.commit()
        print(f"✅ Đã import {imported_count} điểm chuẩn mới")
        print(f"🔄 Đã cập nhật {skipped_count} điểm chuẩn")

def import_admission_methods():
    """Import phương thức xét tuyển từ file CSV"""
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'admission_methods.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ Không tìm thấy file: {csv_path}")
        return
    
    print(f"📂 Đang import từ: {csv_path}")
    
    with app.app_context():
        # Đảm bảo các bảng đã được tạo
        db.create_all()
        imported_count = 0
        skipped_count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                method_name = row['method_name'].strip()
                year = int(row['year'])
                min_score_str = row['min_score'].strip()
                special_requirements = row.get('special_requirements', '').strip()
                description = row.get('description', '').strip()
                
                min_score = None
                if min_score_str and min_score_str != '-':
                    try:
                        min_score = float(min_score_str)
                    except ValueError:
                        print(f"⚠️  Lỗi chuyển đổi điểm: {method_name} - {year} - {min_score_str}")
                
                # Kiểm tra xem đã tồn tại chưa
                existing = AdmissionMethod.query.filter_by(
                    method_name=method_name,
                    year=year
                ).first()
                
                if existing:
                    # Update existing record
                    existing.min_score = min_score
                    existing.special_requirements = special_requirements if special_requirements != '-' else None
                    existing.description = description
                    skipped_count += 1
                else:
                    # Create new record
                    admission_method = AdmissionMethod(
                        method_name=method_name,
                        year=year,
                        min_score=min_score,
                        special_requirements=special_requirements if special_requirements != '-' else None,
                        description=description
                    )
                    db.session.add(admission_method)
                    imported_count += 1
        
        db.session.commit()
        print(f"✅ Đã import {imported_count} phương thức xét tuyển mới")
        print(f"🔄 Đã cập nhật {skipped_count} phương thức xét tuyển")

def show_statistics():
    """Hiển thị thống kê dữ liệu"""
    with app.app_context():
        total_scores = AdmissionScore.query.count()
        total_methods = AdmissionMethod.query.count()
        
        print("\n" + "="*60)
        print("📊 THỐNG KÊ DỮ LIỆU ĐIỂM CHUẨN")
        print("="*60)
        print(f"Tổng số điểm chuẩn: {total_scores}")
        print(f"Tổng số phương thức xét tuyển: {total_methods}")
        
        # Thống kê theo năm
        print("\n📅 Thống kê theo năm:")
        for year in [2025, 2024, 2023, 2022]:
            count = AdmissionScore.query.filter_by(year=year).count()
            if count > 0:
                avg_score = db.session.query(db.func.avg(AdmissionScore.admission_score))\
                    .filter_by(year=year).scalar()
                max_score = db.session.query(db.func.max(AdmissionScore.admission_score))\
                    .filter_by(year=year).scalar()
                min_score = db.session.query(db.func.min(AdmissionScore.admission_score))\
                    .filter_by(year=year).scalar()
                
                print(f"  Năm {year}: {count} ngành")
                print(f"    - Điểm TB: {avg_score:.2f}")
                print(f"    - Điểm cao nhất: {max_score:.2f}")
                print(f"    - Điểm thấp nhất: {min_score:.2f}")
        
        # Top ngành có điểm cao nhất 2025
        print("\n🏆 Top 5 ngành có điểm chuẩn cao nhất năm 2025:")
        top_programs = AdmissionScore.query.filter_by(year=2025)\
            .order_by(AdmissionScore.admission_score.desc())\
            .limit(5).all()
        
        for i, prog in enumerate(top_programs, 1):
            print(f"  {i}. {prog.program_name}: {prog.admission_score:.2f} điểm")
            if prog.notes:
                print(f"     📝 {prog.notes}")
        
        print("="*60 + "\n")

def main():
    """Hàm main"""
    print("\n" + "="*60)
    print("🚀 IMPORT DỮ LIỆU ĐIỂM CHUẨN VÀ PHƯƠNG THỨC XÉT TUYỂN")
    print("="*60 + "\n")
    
    # Import admission scores
    import_admission_scores()
    
    # Import admission methods
    import_admission_methods()
    
    # Show statistics
    show_statistics()
    
    print("✨ Hoàn thành!")

if __name__ == '__main__':
    main()

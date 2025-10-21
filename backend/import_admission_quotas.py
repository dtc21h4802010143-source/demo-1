"""
Import AdmissionQuota data from CSV
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

from backend.app import app
from backend.models import db, Program, AdmissionQuota
import unicodedata

def _normalize(text: str) -> str:
    if not text:
        return ''
    # lowercase, strip, remove accents, remove extra spaces and parentheses variants
    text = text.lower().strip()
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    # unify some synonyms
    replacements = {
        ' (ai)': '',
        '(ai)': '',
        '(chuyen nganh tri tue nhan tao va du lieu lon)': '',
        ' so': ' so',  # keep space
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # collapse spaces
    text = ' '.join(text.split())
    return text
import csv

def simple_match_program(program_name, programs):
    """Tìm program bằng exact match hoặc partial match"""
    program_name_lower = _normalize(program_name)
    
    # Try exact match first
    for program in programs:
        if _normalize(program.name) == program_name_lower:
            return program, 100
    
    # Try partial match (contains)
    for program in programs:
        pname = _normalize(program.name)
        if program_name_lower in pname or pname in program_name_lower:
            return program, 80
    
    return None, 0

def import_admission_quotas():
    """Import admission quotas from CSV file"""
    csv_file = os.path.join(parent_dir, 'data', 'admission_quotas.csv')
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: File not found: {csv_file}")
        return
    
    print(f"📂 Reading from: {csv_file}")
    
    with app.app_context():
        # Get all programs
        programs = Program.query.all()
        print(f"📋 Found {len(programs)} programs in database")
        
        # Read CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"📊 Found {len(rows)} rows in CSV")
        
        imported = 0
        skipped = 0
        errors = 0
        
        for row in rows:
            program_name = row['program_name'].strip()
            year = int(row['year'])
            quota = int(row['quota'])
            minimum_score = float(row['minimum_score'])

            # Simple match program
            program, match_score = simple_match_program(program_name, programs)
            
            if program:
                # Check if quota already exists
                existing = AdmissionQuota.query.filter_by(
                    program_id=program.id,
                    year=year
                ).first()
                
                if existing:
                    # Update existing
                    existing.quota = quota
                    existing.minimum_score = minimum_score
                    print(f"🔄 Updated: {program.name} ({year}) - Match: {match_score}%")
                    skipped += 1
                else:
                    # Create new
                    new_quota = AdmissionQuota(
                        program_id=program.id,
                        year=year,
                        quota=quota,
                            minimum_score=minimum_score
                    )
                    db.session.add(new_quota)
                    print(f"✅ Added: {program.name} ({year}) - Quota: {quota}, Score: {minimum_score} - Match: {match_score}%")
                    imported += 1
            else:
                print(f"⚠️  No match for: {program_name} (year {year})")
                errors += 1
        
        # Commit changes
        try:
            db.session.commit()
            print(f"\n{'='*60}")
            print(f"✅ Import completed!")
            print(f"   - Imported: {imported} new records")
            print(f"   - Updated: {skipped} existing records")
            print(f"   - Errors: {errors} unmatched programs")
            print(f"{'='*60}")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing to database: {e}")

def show_statistics():
    """Show statistics about imported data"""
    with app.app_context():
        total = AdmissionQuota.query.count()
        print(f"\n📊 AdmissionQuota Statistics:")
        print(f"   Total records: {total}")
        
        if total > 0:
            # Group by year
            years = db.session.query(AdmissionQuota.year).distinct().order_by(AdmissionQuota.year.desc()).all()
            for (year,) in years:
                count = AdmissionQuota.query.filter_by(year=year).count()
                avg_quota = db.session.query(db.func.avg(AdmissionQuota.quota)).filter_by(year=year).scalar()
                avg_score = db.session.query(db.func.avg(AdmissionQuota.minimum_score)).filter_by(year=year).scalar()
                print(f"   Year {year}: {count} programs, Avg quota: {avg_quota:.1f}, Avg score: {avg_score:.2f}")

if __name__ == '__main__':
    print("="*60)
    print("  IMPORT ADMISSION QUOTAS")
    print("="*60)
    import_admission_quotas()
    show_statistics()

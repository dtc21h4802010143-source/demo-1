"""
Import departments and programs from CSV files
Wrapper script to handle proper Python module execution
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

from backend.app import app, db
from backend.models import Department, Program, SiteSetting
import csv

DATA_DIR = os.path.join(parent_dir, 'data')

def _read_csv(path: str):
    if not os.path.exists(path):
        print(f"[skip] not found: {path}")
        return []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader]
    print(f"[read] {path} -> {len(rows)} rows")
    return rows

def upsert_departments(rows):
    count = 0
    for r in rows:
        name = (r.get('name') or '').strip()
        if not name:
            continue
        dept = Department.query.filter_by(name=name).first()
        if not dept:
            dept = Department(name=name)
            db.session.add(dept)
            print(f"  ➕ Created department: {name}")
        else:
            print(f"  🔄 Updated department: {name}")
        dept.description = r.get('description')
        dept.head = r.get('head')
        dept.contact_email = r.get('contact_email')
        count += 1
    db.session.commit()
    print(f"[upsert] departments: {count}")

def build_dept_map():
    return {d.name: d.id for d in Department.query.all()}

def upsert_programs(rows, dept_name_to_id):
    count = 0
    skipped = 0
    for r in rows:
        name = (r.get('name') or '').strip()
        code = (r.get('code') or '').strip()
        
        if not name:
            print(f"  ⚠️  Skipped: empty name")
            skipped += 1
            continue
            
        if not code:
            print(f"  ⚠️  Skipped {name}: no code")
            skipped += 1
            continue
        
        # Check if exists by name (unique identifier)
        prog = Program.query.filter_by(name=name).first()
        if not prog:
            # Create new
            prog = Program(code=code, name=name, department_id=None)
            db.session.add(prog)
            print(f"  ➕ Created: {name} ({code})")
        else:
            print(f"  🔄 Updated: {name} ({code})")
            prog.code = code
        
        prog.description = r.get('description')
        prog.duration = r.get('duration')
        prog.requirements = r.get('requirements')
        prog.career_prospects = r.get('career_prospects')
        try:
            prog.tuition_fee = float(r.get('tuition_fee')) if r.get('tuition_fee') else None
        except Exception as e:
            print(f"    ⚠️  Invalid tuition_fee: {e}")
        
        dept_name = (r.get('department') or '').strip()
        if dept_name:
            dept_id = dept_name_to_id.get(dept_name)
            if dept_id:
                prog.department_id = dept_id
            else:
                print(f"    ⚠️  Department not found: {dept_name}")
        count += 1
    
    db.session.commit()
    print(f"[upsert] programs: {count} imported, {skipped} skipped")

def upsert_settings(rows):
    count = 0
    for r in rows:
        key = (r.get('key') or '').strip()
        if not key:
            continue
        val = r.get('value')
        s = SiteSetting.query.filter_by(key=key).first()
        if not s:
            s = SiteSetting(key=key, value=val)
            db.session.add(s)
        else:
            s.value = val
        count += 1
    db.session.commit()
    print(f"[upsert] settings: {count}")

def import_all():
    with app.app_context():
        print("="*60)
        print("  IMPORT FROM CSV")
        print("="*60)
        
        # Departments
        depts = _read_csv(os.path.join(DATA_DIR, 'departments.csv'))
        if depts:
            upsert_departments(depts)

        # Build map for department name -> id
        dept_map = build_dept_map()
        print(f"[dept_map] {len(dept_map)} departments available")
        for k, v in dept_map.items():
            print(f"  - {k} -> ID {v}")

        # Programs
        progs = _read_csv(os.path.join(DATA_DIR, 'programs.csv'))
        if progs:
            upsert_programs(progs, dept_map)

        # Settings
        settings = _read_csv(os.path.join(DATA_DIR, 'settings.csv'))
        if settings:
            upsert_settings(settings)

        print("="*60)
        print("[done] CSV import finished.")
        
        # Show summary
        total_depts = Department.query.count()
        total_progs = Program.query.count()
        print(f"📊 Database Summary:")
        print(f"   Departments: {total_depts}")
        print(f"   Programs: {total_progs}")
        print("="*60)

if __name__ == '__main__':
    import_all()

import csv
import os
from typing import Dict

from app import app, db
from .models import Department, Program, SiteSetting


DATA_DIR = os.path.join(app.root_path, '..', 'data')


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
        dept.description = r.get('description')
        dept.head = r.get('head')
        dept.contact_email = r.get('contact_email')
        count += 1
    db.session.commit()
    print(f"[upsert] departments: {count}")


def upsert_programs(rows, dept_name_to_id: Dict[str, int]):
    count = 0
    for r in rows:
        code = (r.get('code') or '').strip()
        name = (r.get('name') or '').strip()
        if not code or not name:
            continue
        prog = Program.query.filter_by(code=code).first()
        if not prog:
            prog = Program(code=code, name=name, department_id=None)
            db.session.add(prog)
        prog.name = name
        prog.description = r.get('description')
        prog.duration = r.get('duration')
        prog.requirements = r.get('requirements')
        prog.career_prospects = r.get('career_prospects')
        try:
            prog.tuition_fee = float(r.get('tuition_fee')) if r.get('tuition_fee') else None
        except Exception:
            pass
        dept_name = (r.get('department') or '').strip()
        if dept_name:
            prog.department_id = dept_name_to_id.get(dept_name)
        count += 1
    db.session.commit()
    print(f"[upsert] programs: {count}")


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


def build_dept_map():
    return {d.name: d.id for d in Department.query.all()}


def import_all():
    with app.app_context():
        # Departments
        depts = _read_csv(os.path.join(DATA_DIR, 'departments.csv'))
        if depts:
            upsert_departments(depts)

        # Build map for department name -> id
        dept_map = build_dept_map()

        # Programs
        progs = _read_csv(os.path.join(DATA_DIR, 'programs.csv'))
        if progs:
            upsert_programs(progs, dept_map)

        # Settings
        settings = _read_csv(os.path.join(DATA_DIR, 'settings.csv'))
        if settings:
            upsert_settings(settings)

        print("[done] CSV import finished.")


if __name__ == '__main__':
    import_all()

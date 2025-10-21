import os
from typing import List, Tuple

from .app import app, db
from .models import Department, Program

def seed_faculties_and_programs():
    faculties = [
        {
            'name': 'Khoa Công nghệ thông tin',
            'description': 'Đào tạo các ngành cốt lõi về máy tính và công nghệ.',
            'head': 'Trưởng khoa CNTT',
            'contact_email': 'cntt@university.edu.vn',
            'programs': [
                ('Công nghệ thông tin', 'CNTT'),
                ('Kỹ thuật phần mềm', 'KTPM'),
                ('Khoa học máy tính (chuyên ngành Trí tuệ nhân tạo và Dữ liệu lớn)', 'KHMT_AI_DL'),
                ('An toàn thông tin (hoặc An ninh mạng)', 'ATTT'),
                ('Mạng máy tính và Truyền thông dữ liệu', 'MMT_TTDL'),
                ('Kỹ thuật máy tính', 'KTM'),
                ('Hệ thống thông tin', 'HTTT'),
                ('Khoa học dữ liệu', 'KHDL'),
            ]
        },
        {
            'name': 'Khoa Kỹ thuật và Công nghệ',
            'description': 'Tập trung vào kỹ thuật ứng dụng và công nghệ số.',
            'head': 'Trưởng khoa KTCN',
            'contact_email': 'ktcn@university.edu.vn',
            'programs': [
                ('Công nghệ kỹ thuật điện, điện tử', 'CNKT_DD'),
                ('Công nghệ kỹ thuật điều khiển và tự động hóa (Tự động hóa)', 'CNKT_TDH'),
                ('Công nghệ kỹ thuật điện tử - viễn thông', 'CNKT_DTVT'),
                ('Điện tử viễn thông', 'DTVT'),
                ('Công nghệ ôtô và Giao thông thông minh (Công nghệ ô tô)', 'CNOTO'),
                ('Kỹ thuật cơ điện tử thông minh và robot (Cơ điện tử)', 'KTCĐT'),
                ('Kỹ thuật y sinh', 'KTYS'),
                ('Vi mạch bán dẫn', 'VMB'),
            ]
        },
        {
            'name': 'Khoa Kinh tế và Quản trị',
            'description': 'Đào tạo các ngành kinh tế và quản lý ứng dụng công nghệ số.',
            'head': 'Trưởng khoa KTQT',
            'contact_email': 'ktqt@university.edu.vn',
            'programs': [
                ('Thương mại điện tử', 'TMDT'),
                ('Marketing số', 'MKTSO'),
                ('Quản trị kinh doanh số', 'QTDN_SO'),
                ('Logistics và Quản lý chuỗi cung ứng', 'LOG_SUP'),
                ('Quản trị văn phòng', 'QTVP'),
                ('Kinh tế số (hoặc Công nghệ tài chính)', 'KTSO_FINTECH'),
                ('Hệ thống thông tin quản lý', 'HTTQL'),
                ('Kế toán', 'KETOAN'),
                ('Tài chính ngân hàng', 'TCNH'),
            ]
        },
        {
            'name': 'Khoa Nghệ thuật và Truyền thông',
            'description': 'Phụ trách nhóm ngành mỹ thuật và truyền thông.',
            'head': 'Trưởng khoa NTTT',
            'contact_email': 'nttt@university.edu.vn',
            'programs': [
                ('Truyền thông đa phương tiện', 'TTDPT'),
                ('Thiết kế đồ họa', 'TKDH'),
                ('Công nghệ truyền thông', 'CNTRT'),
                ('Nghệ thuật số', 'NTSO'),
                ('Công nghệ đa phương tiện', 'CNDPT'),
            ]
        },
        {
            'name': 'Khoa Ngoại ngữ',
            'description': 'Đào tạo ngoại ngữ và truyền thông bằng tiếng Anh.',
            'head': 'Trưởng khoa Ngoại ngữ',
            'contact_email': 'nn@university.edu.vn',
            'programs': [
                ('Ngôn ngữ Anh', 'NNA'),
                ('Tiếng Anh truyền thông', 'TATTT'),
            ]
        },
    ]

    default_duration = '4 năm'
    default_requirements = 'Theo quy định tuyển sinh (ví dụ: Tổ hợp A00, A01, D01)'
    default_career = 'Cơ hội việc làm rộng mở trong lĩnh vực liên quan.'
    default_tuition = 12000000

    created_depts = 0
    created_programs = 0

    for fac in faculties:
        dept = Department.query.filter_by(name=fac['name']).first()
        if not dept:
            dept = Department(
                name=fac['name'],
                description=fac.get('description'),
                head=fac.get('head'),
                contact_email=fac.get('contact_email')
            )
            db.session.add(dept)
            db.session.flush()
            created_depts += 1
        # Ensure programs
        for prog_name, prog_code in fac['programs']:
            code = (prog_code or '').strip()[:20]
            # Check by code globally as it's unique; also check by name within department
            exists_by_code = Program.query.filter_by(code=code).first()
            exists_by_name = Program.query.filter_by(name=prog_name, department_id=dept.id).first()
            if exists_by_code or exists_by_name:
                continue
            db.session.add(Program(
                name=prog_name,
                code=code,
                department_id=dept.id,
                duration=default_duration,
                description=f"Ngành {prog_name}.",
                requirements=default_requirements,
                career_prospects=default_career,
                tuition_fee=default_tuition
            ))
            created_programs += 1

    db.session.commit()
    return created_depts, created_programs

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        depts, progs = seed_faculties_and_programs()
        print(f"✅ Đã seed: {depts} khoa, {progs} ngành.")

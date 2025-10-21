# Script: import_sample_news.py

from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app import app
from .models import db, News

sample_news = [
    {
        'title': 'Khai mạc tuyển sinh AI 2025',
        'content': 'Chương trình tuyển sinh AI 2025 chính thức bắt đầu. Đăng ký ngay để nhận nhiều ưu đãi!',
        'author': 'Ban tuyển sinh',
        'created_at': datetime(2025, 10, 1)
    },
    {
        'title': 'Cập nhật điểm chuẩn các ngành',
        'content': 'Điểm chuẩn các ngành đã được cập nhật trên hệ thống. Vui lòng tra cứu để biết thêm chi tiết.',
        'author': 'Phòng đào tạo',
        'created_at': datetime(2025, 10, 10)
    }
]

with app.app_context():
    for item in sample_news:
        news = News(**item)
        db.session.add(news)
    db.session.commit()
    print('✅ Đã import tin mẫu!')

# Script: import_sample_news_sqlite.py
# Import tin tức mẫu trực tiếp qua SQLite, không cần Flask context
import sqlite3
from datetime import datetime

DB_PATH = '../instance/app.db'

sample_news = [
    (
        'Khai mạc tuyển sinh AI 2025',
        'Chương trình tuyển sinh AI 2025 chính thức bắt đầu. Đăng ký ngay để nhận nhiều ưu đãi!',
        'Ban tuyển sinh',
        '2025-10-01 00:00:00',
        '2025-10-01 00:00:00'
    ),
    (
        'Cập nhật điểm chuẩn các ngành',
        'Điểm chuẩn các ngành đã được cập nhật trên hệ thống. Vui lòng tra cứu để biết thêm chi tiết.',
        'Phòng đào tạo',
        '2025-10-10 00:00:00',
        '2025-10-10 00:00:00'
    )
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Ensure table exists
c.execute('''CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME,
    updated_at DATETIME,
    author TEXT
)''')

# Insert data
c.executemany('INSERT INTO news (title, content, author, created_at, updated_at) VALUES (?, ?, ?, ?, ?)', sample_news)
conn.commit()
conn.close()
print('✅ Đã import tin mẫu (SQLite)!')

# Script: migrate_add_news.py
# Tạo bảng news (SQLite)
import sqlite3

DB_PATH = '../instance/app.db'
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

try:
    c.execute('''CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME,
        updated_at DATETIME,
        author TEXT
    )''')
    print('✅ Đã tạo bảng news!')
except Exception as e:
    print(f'⚠️ Lỗi: {e}')

conn.commit()
conn.close()

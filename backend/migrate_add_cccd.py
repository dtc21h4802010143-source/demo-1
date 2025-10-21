# Script: migrate_add_cccd.py
# Thêm trường cccd vào bảng applicant (SQLite)
import sqlite3

DB_PATH = '../instance/app.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

try:
    c.execute("ALTER TABLE applicant ADD COLUMN cccd TEXT UNIQUE")
    print("✅ Đã thêm trường cccd vào bảng applicant!")
except Exception as e:
    print(f"⚠️ Lỗi hoặc trường đã tồn tại: {e}")

conn.commit()
conn.close()

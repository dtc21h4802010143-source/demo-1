import os
from app import app, send_email

if __name__ == "__main__":
    to = os.getenv('MAIL_TEST_TO', 'dtc21h4802010143@ictu.edu.vn')
    subject = "SMTP quick test"
    body = "<p>Xin chào, đây là email test từ Admission System.</p>"
    with app.app_context():
        ok = send_email(subject, [to], body)
        print({"ok": bool(ok), "to": to})

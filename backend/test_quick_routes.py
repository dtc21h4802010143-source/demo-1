import json
import io
from contextlib import contextmanager

from app import app, db, seed_initial_data
from config import Config

@contextmanager
def client_ctx():
    with app.app_context():
        db.create_all()
        # Ensure defaults (admin user, sample data) exist
        try:
            seed_initial_data()
        except Exception as e:
            # If seeding fails, continue tests; some routes may still work
            print(f"[warn] seed_initial_data failed: {e}")
        with app.test_client() as c:
            yield c

def check(label, resp, expect_status=200, allow_redirect=False):
    ok = resp.status_code == expect_status or (allow_redirect and resp.status_code in (301,302,303,307))
    status = 'OK' if ok else f'FAIL({resp.status_code})'
    print(f"{label:<35} -> {status}")
    return ok

def login(client, username, password):
    return client.post('/login', data={
        'username_or_email': username,
        'password': password
    }, follow_redirects=True)

if __name__ == '__main__':
    print('=== Quick route checks ===')
    passed = True
    with client_ctx() as client:
        # Public
        passed &= check('GET /', client.get('/'))
        passed &= check('GET /programs', client.get('/programs'))
        passed &= check('GET /departments', client.get('/departments'))
        passed &= check('GET /contact', client.get('/contact'))
        passed &= check('GET /chatbot', client.get('/chatbot'))
        # New public info routes
        passed &= check('GET /guide', client.get('/guide'))
        passed &= check('GET /faq', client.get('/faq'))
        passed &= check('GET /scholarships', client.get('/scholarships'))
        passed &= check('GET /privacy', client.get('/privacy'))
        passed &= check('GET /forgot-password', client.get('/forgot-password'))
        passed &= check('GET /terms', client.get('/terms'))

        # Chatbot API
        r = client.post('/api/chat', json={'message': 'Xin chao'})
        if r.is_json and 'response' in r.get_json():
            print(f"POST /api/chat                     -> OK")
        else:
            print(f"POST /api/chat                     -> FAIL")
            passed &= False

        # Login as admin
        admin_user = Config.ADMIN_USERNAME
        admin_pass = Config.ADMIN_PASSWORD
        r = login(client, admin_user, admin_pass)
        passed &= check('POST /login (admin)', r, expect_status=200)

        # Admin pages
        passed &= check('GET /admin', client.get('/admin'))
        passed &= check('GET /admin/dashboard', client.get('/admin/dashboard'))
        passed &= check('GET /admin/programs', client.get('/admin/programs'))
        passed &= check('GET /admin/departments', client.get('/admin/departments'))
        passed &= check('GET /admin/applications', client.get('/admin/applications'))
        passed &= check('GET /admin/statistics', client.get('/admin/statistics'))
        passed &= check('GET /admin/export-csv', client.get('/admin/export-csv'), allow_redirect=True)
        passed &= check('GET /admin/contact', client.get('/admin/contact'))

        # Profile pages
        passed &= check('GET /profile', client.get('/profile'))
        # Wishes should redirect to edit_profile if no applicant
        passed &= check('GET /wishes', client.get('/wishes'), allow_redirect=True)

        # Create applicant profile (for admin user) so that document upload works
        form_data = {
            'full_name': 'Admin User',
            'phone': '0123456789',
            'date_of_birth': '2000-01-01',
            'address': '123 Street',
            'high_school': 'THPT ABC'
        }
        r = client.post('/profile/edit', data=form_data, follow_redirects=True)
        passed &= check('POST /profile/edit (create applicant)', r, expect_status=200)

        # Forgot password submit (reCAPTCHA bypassed in dev if secret not set)
        r = client.post('/forgot-password', data={'email': f"{Config.ADMIN_USERNAME}@example.com"}, follow_redirects=True)
        passed &= check('POST /forgot-password', r, expect_status=200)

        # Resend verification (requires login)
        r = client.get('/resend-verification', follow_redirects=True)
        passed &= check('GET /resend-verification', r, expect_status=200)

        # Upload a small PDF document
        data = {
            'document': (io.BytesIO(b"%PDF-1.4\n% test pdf content"), 'test.pdf')
        }
        r = client.post('/profile/documents', data=data, content_type='multipart/form-data', follow_redirects=True)
        passed &= check('POST /profile/documents (upload)', r, expect_status=200)
        # Confirm the filename appears in listing page
        page = client.get('/profile/documents')
        passed &= check('GET /profile/documents (list)', page, expect_status=200)
        if b'test.pdf' in page.data:
            print('Document listing contains uploaded filename -> OK')
        else:
            print('Document listing missing uploaded filename -> FAIL')
            passed &= False

        # Find the uploaded document id from DB and delete it
        try:
            from models import ApplicantDocument
            # We are still inside client_ctx() which already pushed app context
            doc = ApplicantDocument.query.order_by(ApplicantDocument.uploaded_at.desc()).first()
            if doc:
                del_resp = client.post(f'/profile/documents/delete/{doc.id}', follow_redirects=True)
                passed &= check('POST /profile/documents/delete/<id>', del_resp, expect_status=200)
            else:
                print('No ApplicantDocument found to delete -> FAIL')
                passed &= False
        except Exception as e:
            print(f"[tests] error while deleting document: {e}")
            passed &= False

        # Wishes: add, list, results view, and admin approve
        try:
            from models import Program, Application
            # Add a wish for the first program
            prog = Program.query.first()
            if prog is not None:
                r = client.post('/wishes/add', data={'program_id': str(prog.id)}, follow_redirects=True)
                passed &= check('POST /wishes/add', r, expect_status=200)
                # List wishes and check program name present
                wishes_page = client.get('/wishes')
                passed &= check('GET /wishes (after add)', wishes_page, expect_status=200)
                if prog.name.encode('utf-8') in wishes_page.data:
                    print('Wishes listing shows added program -> OK')
                else:
                    print('Wishes listing missing added program -> FAIL')
                    passed &= False
                # Results page
                results_page = client.get('/results')
                passed &= check('GET /results', results_page, expect_status=200)
                # Approve application as admin
                app_row = Application.query.order_by(Application.application_date.desc()).first()
                if app_row:
                    resp = client.post(f'/admin/applications/approve/{app_row.id}', follow_redirects=True)
                    passed &= check('POST /admin/applications/approve/<id>', resp, expect_status=200)
                else:
                    print('No Application found to approve -> FAIL')
                    passed &= False
            else:
                print('No Program found to add wish -> FAIL')
                passed &= False
        except Exception as e:
            print(f"[tests] wishes/admin approve flow error: {e}")
            passed &= False

        # Admin email test POST
        email_test = client.post('/admin/email-test', data={'to': f"{Config.ADMIN_USERNAME}@example.com", 'subject': 'Test', 'body': 'Hello'}, follow_redirects=True)
        passed &= check('POST /admin/email-test', email_test, expect_status=200)

        # CSV export actually writes files
        import os
        _ = client.get('/admin/export-csv', follow_redirects=True)
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        users_csv = os.path.abspath(os.path.join(data_dir, 'users.csv'))
        if os.path.exists(users_csv):
            print('users.csv exists after export -> OK')
        else:
            print('users.csv missing after export -> FAIL')
            passed &= False

        # --- Test AI API: CV Parsing (requires login) ---
        cv_content = (
            'Ho ten: Nguyen Van A\n'
            'Email: baccamngoc2002@gmail.com\n'
            'Ky nang: Python, Machine Learning, SQL\n'
            'Hoc van: DH Bach Khoa\n'
            'Kinh nghiem: 2 nam Data Analyst\n'
        )
        data = {
            'file': (io.BytesIO(cv_content.encode('utf-8')), 'cv.txt')
        }
        r = client.post('/api/cv_parse', data=data, content_type='multipart/form-data')
        if r.is_json and 'parsed' in r.get_json():
            parsed = r.get_json()['parsed']
            print('POST /api/cv_parse                -> OK')
            # Kiểm tra các trường chính
            if parsed.get('name') == 'Nguyen Van A' and parsed.get('email') == 'baccamngoc2002@gmail.com':
                print('CV parsing fields                -> OK')
            else:
                print('CV parsing fields                -> FAIL')
                passed &= False
        else:
            print('POST /api/cv_parse                -> FAIL')
            passed &= False

        # Invalid/expired token flows (basic sanity)
        passed &= check('GET /verify-email/<bad>', client.get('/verify-email/invalid-token'), allow_redirect=True)
        passed &= check('GET /reset-password/<bad>', client.get('/reset-password/invalid-token'), allow_redirect=True)
    print('\nRESULT:', 'ALL PASSED' if passed else 'SOME FAILED')


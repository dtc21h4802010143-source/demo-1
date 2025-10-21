import sys, json
# Thêm đường dẫn để import backend.app
sys.path.insert(0, r'c:\Users\Bạc Cầm Ngọc\ttks\TS2\admission_system')
sys.path.insert(0, r'c:\Users\Bạc Cầm Ngọc\ttks\TS2\admission_system\backend')

from backend.app import app

payload = {
    'total_score': 20.5,
    'math_score': 8.0,
    'subject_combination': 'A00',
    'interests': ['công nghệ', 'lập trình', 'AI'],
    'skills': ['logic'],
    'save_preference': False
}

with app.app_context():
    with app.test_client() as client:
        resp = client.post('/api/recommend-programs', json=payload)
        print('Status:', resp.status_code)
        try:
            data = resp.get_json()
            print(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception:
            print('Raw response:', resp.data.decode('utf-8', errors='ignore'))

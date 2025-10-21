"""
Script kiểm tra tất cả url_for() trong templates có tồn tại trong app.py hay không
"""

import re
from pathlib import Path
from collections import defaultdict

# Đọc tất cả routes từ app.py
app_py_path = Path('backend/app.py')
app_content = app_py_path.read_text(encoding='utf-8')

# Tìm tất cả function names có @app.route decorator
route_pattern = r'@app\.route\([^)]+\)(?:\s+@\w+(?:\([^)]*\))?)*\s+def\s+(\w+)'
endpoints = set(re.findall(route_pattern, app_content, re.MULTILINE))

print("=" * 60)
print("✅ TẤT CẢ ENDPOINTS TRONG APP.PY")
print("=" * 60)
for endpoint in sorted(endpoints):
    print(f"  • {endpoint}")
print(f"\nTổng: {len(endpoints)} endpoints\n")

# Tìm tất cả url_for() trong templates
templates_dir = Path('templates')
url_for_pattern = r"url_for\(['\"](\w+)['\"]"

templates_calls = defaultdict(list)
for template_file in templates_dir.rglob('*.html'):
    content = template_file.read_text(encoding='utf-8')
    matches = re.findall(url_for_pattern, content)
    for match in matches:
        templates_calls[match].append(str(template_file.relative_to(templates_dir)))

print("=" * 60)
print("📝 TẤT CẢ URL_FOR() TRONG TEMPLATES")
print("=" * 60)
for endpoint_name in sorted(templates_calls.keys()):
    files = templates_calls[endpoint_name]
    print(f"  • {endpoint_name} ({len(files)} files)")

print(f"\nTổng: {len(templates_calls)} unique url_for calls\n")

# Kiểm tra các url_for không tồn tại
print("=" * 60)
print("❌ CÁC URL_FOR() KHÔNG TỒN TẠI")
print("=" * 60)

missing = []
for endpoint_name, files in templates_calls.items():
    if endpoint_name not in endpoints:
        missing.append((endpoint_name, files))
        print(f"  ❌ {endpoint_name}")
        for file in files[:3]:  # Show first 3 files
            print(f"      → {file}")
        if len(files) > 3:
            print(f"      ... và {len(files) - 3} files khác")

if not missing:
    print("  ✅ TẤT CẢ URL_FOR() ĐỀU HỢP LỆ!")
else:
    print(f"\n⚠️  Tìm thấy {len(missing)} url_for() không hợp lệ!")

print("=" * 60)

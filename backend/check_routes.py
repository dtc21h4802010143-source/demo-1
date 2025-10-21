import sys
sys.path.insert(0, '.')

from app import app

print("\n=== Checking admin_users routes ===")
for rule in app.url_map.iter_rules():
    if 'user' in rule.endpoint.lower():
        print(f"{rule.rule:40s} -> {rule.endpoint}")

print("\n=== All admin routes ===")
for rule in app.url_map.iter_rules():
    if 'admin' in rule.endpoint.lower():
        print(f"{rule.rule:40s} -> {rule.endpoint}")

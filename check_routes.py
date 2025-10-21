#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to check all registered Flask routes
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app

print("=" * 80)
print("CHECKING ALL FLASK ROUTES")
print("=" * 80)

routes = []
for rule in app.url_map.iter_rules():
    routes.append((rule.rule, rule.endpoint, ','.join(rule.methods - {'HEAD', 'OPTIONS'})))

# Sort by endpoint name
routes.sort(key=lambda x: x[1])

print(f"\n📋 Total routes: {len(routes)}\n")

# Check for document-related routes
print("🔍 DOCUMENT-RELATED ROUTES:")
document_routes = [r for r in routes if 'document' in r[1].lower()]
if document_routes:
    for rule, endpoint, methods in document_routes:
        print(f"  ✅ {endpoint:30} -> {rule:40} [{methods}]")
else:
    print("  ❌ NO DOCUMENT ROUTES FOUND!")

print("\n🔍 PROFILE-RELATED ROUTES:")
profile_routes = [r for r in routes if 'profile' in r[1].lower()]
for rule, endpoint, methods in profile_routes:
    print(f"  ✅ {endpoint:30} -> {rule:40} [{methods}]")

print("\n🔍 ALL ROUTES (alphabetical by endpoint):")
for rule, endpoint, methods in routes:
    print(f"  {endpoint:35} -> {rule:45} [{methods}]")

#!/usr/bin/env python
"""
Quick test script để kiểm tra API endpoints
Chạy: python admission_system/test_api_quick.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import app
import json

def test_suggest_programs():
    """Test /api/suggest-programs endpoint"""
    print("\n=== Testing /api/suggest-programs ===")
    
    with app.test_client() as client:
        # Test data
        payload = {
            "scores": {
                "toan": 8.5,
                "van": 7.5,
                "ngoai_ngu": 8.0,
                "ly": 9.0,
                "hoa": 8.5,
                "sinh": 7.0
            },
            "method": "thpt"
        }
        
        print(f"Request: POST /api/suggest-programs")
        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = client.post(
            '/api/suggest-programs',
            json=payload,
            content_type='application/json'
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Content-Type: {response.content_type}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"\n✅ Success: {data.get('success')}")
            print(f"Total suggestions: {data.get('total', 0)}")
            print(f"Combinations: {data.get('combinations', {})}")
            
            suggestions = data.get('suggestions', [])
            if suggestions:
                print(f"\nTop 3 suggestions:")
                for i, s in enumerate(suggestions[:3], 1):
                    print(f"  {i}. {s['name']} - {s['probability']}% ({s['status']})")
            else:
                print("\n⚠️ No suggestions returned")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)[:500]}")

def test_recommend_programs():
    """Test /api/recommend-programs endpoint"""
    print("\n=== Testing /api/recommend-programs ===")
    
    with app.test_client() as client:
        payload = {
            "total_score": 21.5,
            "math_score": 8.0,
            "subject_combination": "A00",
            "interests": ["công nghệ", "lập trình", "AI"],
            "skills": ["logic"],
            "save_preference": False
        }
        
        print(f"Request: POST /api/recommend-programs")
        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = client.post(
            '/api/recommend-programs',
            json=payload,
            content_type='application/json'
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Content-Type: {response.content_type}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"\n✅ Success: {data.get('success')}")
            
            recs = data.get('data', {}).get('recommendations', [])
            print(f"Total recommendations: {len(recs)}")
            
            if recs:
                print(f"\nTop 3 recommendations:")
                for i, r in enumerate(recs[:3], 1):
                    print(f"  {i}. {r['program_name']} - Match: {r['match_score']}, Prob: {r['probability']}")
            else:
                print("\n⚠️ No recommendations returned (có thể chưa import dữ liệu điểm chuẩn)")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)[:500]}")

def check_routes():
    """List all API routes"""
    print("\n=== Registered API Routes ===")
    
    api_routes = [r for r in app.url_map.iter_rules() if r.rule.startswith('/api/')]
    
    for route in sorted(api_routes, key=lambda x: x.rule):
        methods = ', '.join(sorted([m for m in route.methods if m not in ['HEAD', 'OPTIONS']]))
        print(f"  {route.rule:50s} [{methods}]")
    
    print(f"\nTotal API routes: {len(api_routes)}")

if __name__ == '__main__':
    print("=" * 70)
    print("API Quick Test Script")
    print("=" * 70)
    
    with app.app_context():
        check_routes()
        test_suggest_programs()
        test_recommend_programs()
    
    print("\n" + "=" * 70)
    print("Tests completed!")
    print("=" * 70)

#!/usr/bin/env python
"""
Launcher script để khởi động Flask server
Chạy từ thư mục gốc: python admission_system/run_server.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import app from backend package
from backend.app import app

if __name__ == '__main__':
    print("=" * 70)
    print("  ADMISSION SYSTEM - Flask Development Server")
    print("=" * 70)
    print(f"  Server running at: http://localhost:5000")
    print(f"  API Documentation: http://localhost:5000/api/docs")
    print(f"  Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

@echo off
REM Script khởi động Flask server cho Windows
REM Chạy: start_server.bat

echo ============================================
echo  KHOI DONG FLASK SERVER - ADMISSION SYSTEM
echo ============================================
echo.

cd /d "%~dp0backend"

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo [2/3] Setting environment variables...
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=1

echo.
echo [3/3] Starting Flask server...
echo Server will run at: http://localhost:5000
echo Press Ctrl+C to stop
echo.
echo ============================================
echo.

python app.py

pause

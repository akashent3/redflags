@echo off
echo ========================================
echo RedFlag AI - Server Status Check
echo ========================================
echo.

echo Checking Backend (FastAPI)...
curl -s http://localhost:8000/docs >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Backend is running at http://localhost:8000
    echo     Swagger UI: http://localhost:8000/docs
) else (
    echo [ERROR] Backend is NOT running
    echo     Please start backend: cd backend ^&^& uvicorn app.main:app --reload
)
echo.

echo Checking Frontend (Next.js)...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Frontend is running at http://localhost:3000
) else (
    echo [ERROR] Frontend is NOT running
    echo     Please start frontend: cd frontend ^&^& npm run dev
)
echo.

echo ========================================
echo Ready to Test!
echo ========================================
echo.
echo Test URLs:
echo   Landing Page:  http://localhost:3000
echo   Signup Page:   http://localhost:3000/signup
echo   Login Page:    http://localhost:3000/login
echo   Dashboard:     http://localhost:3000/dashboard (login required)
echo   Analysis:      http://localhost:3000/analyze (login required)
echo.
echo API Documentation:
echo   Swagger UI:    http://localhost:8000/docs
echo.
echo Test Credentials:
echo   Email:    test@example.com
echo   Password: Test123!@#
echo.
pause

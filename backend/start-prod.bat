@echo off
echo Starting Physical AI Textbook Backend (Production)...
echo ===============================================

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found. Please create it with:
    echo.
    echo GEMINI_API_KEY=your_api_key_here
    echo SECRET_KEY=your_secret_key_here
    echo.
    pause
    exit /b 1
)

REM Load environment variables
for /f "tokens=1,2 delims==" %%i in (%~dp0.env) do set %%i=%%j

REM Check required variables
if "%GEMINI_API_KEY%"=="" (
    echo ERROR: GEMINI_API_KEY not set in .env file
    pause
    exit /b 1
)

if "%SECRET_KEY%"=="" (
    echo ERROR: SECRET_KEY not set in .env file
    pause
    exit /b 1
)

REM Set production environment
set ENVIRONMENT=production
set DEBUG=false

echo Starting production server on port 8000...
echo.

REM Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
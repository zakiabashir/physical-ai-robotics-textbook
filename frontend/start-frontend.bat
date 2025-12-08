@echo off
echo.
echo ===============================================
echo Physical AI & Humanoid Robotics Textbook
echo Frontend Startup Script
echo ===============================================
echo.

REM Check if node_modules exists
if not exist node_modules (
    echo Installing frontend dependencies...
    echo.
    npm install
    echo.
)

REM Check if .env exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Update .env with your API keys!
    echo.
)

echo Starting Docusaurus development server...
echo.
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ===============================================
echo.

npm start
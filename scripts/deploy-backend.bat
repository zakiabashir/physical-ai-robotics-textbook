@echo off
REM Backend Deployment Script for Railway (Windows)

echo 🚀 Deploying Physical AI Backend to Railway...

REM Check if Railway CLI is installed
where railway >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Railway CLI not found. Installing...
    npm install -g @railway/cli
)

REM Navigate to backend directory
cd backend

REM Deploy to Railway
echo 🚀 Deploying to Railway...
railway up

echo ✅ Deployment started! Check your Railway dashboard for status.
echo.
echo IMPORTANT: Make sure to set these environment variables in Railway dashboard:
echo   - GEMINI_API_KEY
echo   - COHERE_API_KEY
echo   - QDRANT_URL
echo   - QDRANT_API_KEY
echo   - SECRET_KEY
echo   - BETTER_AUTH_SECRET
echo   - BETTER_AUTH_URL=https://physical-ai-robotics-textbook-8tzi59hee-zakiabashirs-projects.vercel.app
echo.
pause
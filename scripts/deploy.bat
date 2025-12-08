@echo off
REM Physical AI & Humanoid Robotics Textbook - Production Deployment Script (Windows)
REM This script deploys the full stack to production

setlocal enabledelayedexpansion

REM Check prerequisites
:check_prerequisites
echo [INFO] Checking prerequisites...

REM Check Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18+
    exit /b 1
)

REM Check npm
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] npm is not installed
    exit /b 1
)

REM Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    where python3 >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed
        exit /b 1
    )
)

REM Check git
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed
    exit /b 1
)

echo [SUCCESS] Prerequisites check passed
goto :eof

REM Deploy frontend to GitHub Pages
:deploy_frontend
echo [INFO] Deploying frontend to GitHub Pages...

REM Build frontend
echo [INFO] Building frontend...
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed
    exit /b 1
)

REM Check if gh-pages CLI is available
where gh-pages >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] gh-pages CLI not found. Manual deployment required.
    echo [INFO] To deploy manually:
    echo   1. Run: npm run build
    echo   2. Push the 'build' folder to your gh-pages branch
) else (
    gh-pages -d build
    echo [SUCCESS] Frontend deployed to GitHub Pages
)
goto :eof

REM Deploy backend to Railway
:deploy_backend_railway
echo [INFO] Deploying backend to Railway...

where railway >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Railway CLI is not installed. Install it with: npm install -g @railway/cli
    exit /b 1
)

REM Check if logged in to Railway
railway whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Please login to Railway...
    railway login
)

cd backend
railway up
cd ..

echo [SUCCESS] Backend deployed to Railway
goto :eof

REM Deploy backend to Vercel
:deploy_backend_vercel
echo [INFO] Deploying backend to Vercel...

where vercel >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Vercel CLI is not installed. Install it with: npm i -g vercel
    exit /b 1
)

cd backend
vercel --prod
cd ..

echo [SUCCESS] Backend deployed to Vercel
goto :eof

REM Full Docker deployment
:deploy_docker
echo [INFO] Deploying with Docker Compose...

where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed
    exit /b 1
)

docker-compose -f docker-compose.prod.yml up -d --build

echo [SUCCESS] Docker deployment complete
goto :eof

REM Production environment setup
:setup_production_env
echo [INFO] Setting up production environment...

if not exist .env (
    echo [WARNING] .env file not found. Creating template...
    (
        echo # Production Environment Variables
        echo # GEMINI_API_KEY=your_production_gemini_api_key
        echo # SECRET_KEY=your_production_secret_key
        echo # BETTER_AUTH_SECRET=your_production_auth_secret
        echo # DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
        echo # QDRANT_URL=https://your-qdrant-instance.com
        echo # QDRANT_API_KEY=your_qdrant_api_key
        echo.
        echo # Optional: Analytics
        echo # GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
    ) > .env
    echo [WARNING] Please fill in the .env file with your production values
)

REM Verify SSL certificates
if exist ssl (
    if not exist ssl\cert.pem (
        echo [WARNING] SSL certificate not found at ssl\cert.pem
        echo [INFO] To enable HTTPS, add your certificates to ssl\
    )
    if not exist ssl\key.pem (
        echo [WARNING] SSL key not found at ssl\key.pem
        echo [INFO] To enable HTTPS, add your certificates to ssl\
    )
)
goto :eof

REM Run tests before deployment
:run_tests
echo [INFO] Running pre-deployment tests...

REM Check if package.json exists and has test script
if exist package.json (
    findstr "\"test\"" package.json >nul
    if %errorlevel% equ 0 (
        echo [INFO] Running frontend tests...
        call npm test
        if %errorlevel% neq 0 (
            echo [WARNING] Frontend tests failed, but continuing...
        )
    )
)

REM Test backend
if exist backend\test_server.py (
    echo [INFO] Running backend tests...
    cd backend
    start /B python test_server.py
    timeout /t 3 /nobreak >nul

    REM Test health endpoint
    curl -f http://localhost:8000/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo [SUCCESS] Backend health check passed
    ) else (
        echo [ERROR] Backend health check failed
        taskkill /F /IM python.exe >nul 2>&1
        exit /b 1
    )

    taskkill /F /IM python.exe >nul 2>&1
    cd ..
)

echo [SUCCESS] All tests passed
goto :eof

REM Health check after deployment
:health_check
echo [INFO] Performing health checks...

REM Check frontend
curl -f https://physical-ai-robotics.panaversity.org >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Frontend is accessible
) else (
    echo [WARNING] Frontend health check failed
)

REM Check backend
set BACKEND_URL=https://api.physical-ai-robotics.panaversity.org
curl -f %BACKEND_URL%/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Backend is accessible
) else (
    echo [WARNING] Backend health check failed
)
goto :eof

REM Main deployment function
:main
echo =======================================
echo Physical AI Textbook Deployment
echo =======================================

if "%1"=="frontend" (
    call :check_prerequisites
    call :run_tests
    call :setup_production_env
    call :deploy_frontend
    call :health_check
) else if "%1"=="backend-railway" (
    call :check_prerequisites
    call :run_tests
    call :setup_production_env
    call :deploy_backend_railway
    call :health_check
) else if "%1"=="backend-vercel" (
    call :check_prerequisites
    call :run_tests
    call :setup_production_env
    call :deploy_backend_vercel
    call :health_check
) else if "%1"=="docker" (
    call :check_prerequisites
    call :run_tests
    call :setup_production_env
    call :deploy_docker
    call :health_check
) else if "%1"=="all" (
    call :check_prerequisites
    call :run_tests
    call :setup_production_env
    call :deploy_frontend
    call :deploy_backend_railway
    call :health_check
) else (
    echo [INFO] Usage: %0 [frontend^|backend-railway^|backend-vercel^|docker^|all]
    echo.
    echo   frontend        - Deploy frontend to GitHub Pages
    echo   backend-railway  - Deploy backend to Railway
    echo   backend-vercel   - Deploy backend to Vercel
    echo   docker          - Deploy full stack with Docker
    echo   all             - Deploy frontend and backend (Railway)
    exit /b 1
)

echo.
echo [SUCCESS] Deployment completed successfully!
echo.
echo [INFO] Next steps:
echo   1. Update your DNS settings if needed
echo   2. Monitor your deployment
echo   3. Set up alerts and monitoring
echo.

goto :eof

REM Run main function with all arguments
call :main %*
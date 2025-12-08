@echo off
echo === Checking Frontend Setup ===
echo.

REM Check Node.js version
echo Node.js version:
node --version
echo.

REM Check npm version
echo npm version:
npm --version
echo.

REM Check if package.json exists
if exist package.json (
    echo ✓ package.json found
) else (
    echo ✗ package.json not found
)

REM Check if node_modules exists
if exist node_modules (
    echo ✓ node_modules exists
    dir /b node_modules | find /c /v ""
) else (
    echo ✗ node_modules not found
    echo Installing dependencies...
    npm install
)

REM Check Docusaurus config
if exist docusaurus.config.js (
    echo ✓ docusaurus.config.js found
) else (
    echo ✗ docusaurus.config.js not found
)

REM Check src directory
if exist src (
    echo ✓ src directory exists
) else (
    echo ✗ src directory not found
)

echo.
echo === Starting Frontend ===
echo Opening browser at: http://localhost:3000
echo.
npm start
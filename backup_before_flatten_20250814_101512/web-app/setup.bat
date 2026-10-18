@echo off
echo 🚀 Setting up AI Healthcare Platform Web App...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

REM Check Node.js version
for /f "tokens=1,2,3 delims=." %%a in ('node --version') do set NODE_VERSION=%%a
set NODE_VERSION=%NODE_VERSION:~1%
if %NODE_VERSION% lss 16 (
    echo ❌ Node.js version 16+ is required. Current version: 
    node --version
    pause
    exit /b 1
)

echo ✅ Node.js version: 
node --version

REM Clean up any existing node_modules and package-lock.json
echo 🧹 Cleaning up existing installation...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json

REM Install dependencies with legacy peer deps
echo 📦 Installing dependencies...
npm install --legacy-peer-deps

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    echo 💡 Trying alternative installation method...
    npm install --force
    if %errorlevel% neq 0 (
        echo ❌ Installation failed with both methods
        pause
        exit /b 1
    )
)

echo ✅ Dependencies installed successfully

REM Create .env file if it doesn't exist
if not exist .env (
    echo 🔧 Creating .env file...
    echo REACT_APP_API_URL=http://localhost:8000 > .env
    echo ✅ .env file created
) else (
    echo ✅ .env file already exists
)

REM Check if backend is running
echo 🔍 Checking backend connection...
curl -s http://localhost:8000/api/health/ >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is running
) else (
    echo ⚠️  Backend is not running on http://localhost:8000
    echo    Please start the Django backend server first
)

echo.
echo 🎉 Setup complete!
echo.
echo To start the development server:
echo   npm start
echo.
echo To build for production:
echo   npm run build
echo.
echo The web app will be available at: http://localhost:3000
echo.
echo Demo credentials:
echo   Username: patient1
echo   Password: testpass123
echo.
pause

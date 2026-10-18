@echo off
echo Running Android Development Environment Check...
echo.

REM Check if PowerShell is available
powershell -Command "Get-Host" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: PowerShell is not available on this system.
    echo Please run the setup manually by following the instructions in ANDROID_SETUP.md
    pause
    exit /b 1
)

REM Run the PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0setup-android-env.ps1"

echo.
echo Setup check completed. See the results above.
pause 
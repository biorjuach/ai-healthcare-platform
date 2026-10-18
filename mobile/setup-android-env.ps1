# Android Development Environment Setup Script for Windows
# This script helps verify and guide the setup of Android development tools

Write-Host "=== Android Development Environment Setup ===" -ForegroundColor Green
Write-Host "This script will help you verify your Android development setup." -ForegroundColor Yellow
Write-Host ""

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Function to check environment variable
function Test-EnvVar($varName) {
    $value = [Environment]::GetEnvironmentVariable($varName, "Machine")
    if (-not $value) {
        $value = [Environment]::GetEnvironmentVariable($varName, "User")
    }
    return $value
}

Write-Host "Checking Java Development Kit (JDK)..." -ForegroundColor Cyan

# Check Java
if (Test-Command "java") {
    $javaVersion = java -version 2>&1 | Select-String "version"
    Write-Host "✓ Java found: $javaVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Java not found in PATH" -ForegroundColor Red
    Write-Host "  Please install JDK 11 or higher from: https://adoptium.net/" -ForegroundColor Yellow
}

# Check Java compiler
if (Test-Command "javac") {
    $javacVersion = javac -version 2>&1
    Write-Host "✓ Java compiler found: $javacVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Java compiler (javac) not found in PATH" -ForegroundColor Red
    Write-Host "  Please install JDK 11 or higher from: https://adoptium.net/" -ForegroundColor Yellow
}

# Check JAVA_HOME
$javaHome = Test-EnvVar "JAVA_HOME"
if ($javaHome) {
    Write-Host "✓ JAVA_HOME is set: $javaHome" -ForegroundColor Green
} else {
    Write-Host "✗ JAVA_HOME environment variable not set" -ForegroundColor Red
    Write-Host "  Please set JAVA_HOME to your JDK installation directory" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Checking Android SDK..." -ForegroundColor Cyan

# Check ANDROID_HOME
$androidHome = Test-EnvVar "ANDROID_HOME"
if ($androidHome) {
    Write-Host "✓ ANDROID_HOME is set: $androidHome" -ForegroundColor Green
    
    # Check if the path exists
    if (Test-Path $androidHome) {
        Write-Host "✓ Android SDK directory exists" -ForegroundColor Green
    } else {
        Write-Host "✗ Android SDK directory does not exist: $androidHome" -ForegroundColor Red
    }
} else {
    Write-Host "✗ ANDROID_HOME environment variable not set" -ForegroundColor Red
    Write-Host "  Please set ANDROID_HOME to your Android SDK installation directory" -ForegroundColor Yellow
}

# Check ADB
if (Test-Command "adb") {
    $adbVersion = adb version | Select-String "Android Debug Bridge"
    Write-Host "✓ ADB found: $adbVersion" -ForegroundColor Green
} else {
    Write-Host "✗ ADB not found in PATH" -ForegroundColor Red
    Write-Host "  This usually means Android SDK platform-tools are not in PATH" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Checking Android Studio..." -ForegroundColor Cyan

# Check if Android Studio is installed in common locations
$androidStudioPaths = @(
    "${env:ProgramFiles}\Android\Android Studio\bin\studio64.exe",
    "${env:ProgramFiles(x86)}\Android\Android Studio\bin\studio64.exe",
    "${env:LOCALAPPDATA}\Android\Android Studio\bin\studio64.exe"
)

$androidStudioFound = $false
foreach ($path in $androidStudioPaths) {
    if (Test-Path $path) {
        Write-Host "✓ Android Studio found: $path" -ForegroundColor Green
        $androidStudioFound = $true
        break
    }
}

if (-not $androidStudioFound) {
    Write-Host "✗ Android Studio not found in common locations" -ForegroundColor Red
    Write-Host "  Please install Android Studio from: https://developer.android.com/studio" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Setup Instructions ===" -ForegroundColor Green

if (-not $javaHome -or -not (Test-Command "java")) {
    Write-Host "1. Install JDK 11 or higher:" -ForegroundColor Yellow
    Write-Host "   - Download from: https://adoptium.net/" -ForegroundColor White
    Write-Host "   - Run the installer and follow the setup wizard" -ForegroundColor White
    Write-Host ""
}

if (-not $androidHome -or -not $androidStudioFound) {
    Write-Host "2. Install Android Studio:" -ForegroundColor Yellow
    Write-Host "   - Download from: https://developer.android.com/studio" -ForegroundColor White
    Write-Host "   - Run the installer and follow the setup wizard" -ForegroundColor White
    Write-Host "   - Make sure to install Android SDK during setup" -ForegroundColor White
    Write-Host ""
}

Write-Host "3. Set Environment Variables:" -ForegroundColor Yellow
Write-Host "   - Open System Properties (Win + Pause/Break)" -ForegroundColor White
Write-Host "   - Click 'Advanced system settings'" -ForegroundColor White
Write-Host "   - Click 'Environment Variables'" -ForegroundColor White
Write-Host "   - Add JAVA_HOME pointing to your JDK installation" -ForegroundColor White
Write-Host "   - Add ANDROID_HOME pointing to your Android SDK" -ForegroundColor White
Write-Host "   - Add to PATH: %ANDROID_HOME%\platform-tools" -ForegroundColor White
Write-Host ""

Write-Host "4. Configure Android SDK:" -ForegroundColor Yellow
Write-Host "   - Open Android Studio" -ForegroundColor White
Write-Host "   - Go to Tools → SDK Manager" -ForegroundColor White
Write-Host "   - Install Android 13 (API level 33) and other required platforms" -ForegroundColor White
Write-Host ""

Write-Host "5. Verify Setup:" -ForegroundColor Yellow
Write-Host "   - Restart your terminal/command prompt" -ForegroundColor White
Write-Host "   - Run: npx react-native doctor" -ForegroundColor White
Write-Host ""

Write-Host "For detailed instructions, see: ANDROID_SETUP.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 
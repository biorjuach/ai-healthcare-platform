#!/usr/bin/env node

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 Verifying Android Development Environment Setup...\n');

// Colors for console output
const colors = {
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    cyan: '\x1b[36m',
    reset: '\x1b[0m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkCommand(command, description) {
    try {
        const result = execSync(command, { encoding: 'utf8', stdio: 'pipe' });
        log(`✅ ${description}: Found`, 'green');
        return true;
    } catch (error) {
        log(`❌ ${description}: Not found`, 'red');
        return false;
    }
}

function checkEnvironmentVariable(varName, description) {
    const value = process.env[varName];
    if (value) {
        log(`✅ ${description}: ${value}`, 'green');
        return true;
    } else {
        log(`❌ ${description}: Not set`, 'red');
        return false;
    }
}

function checkPathExists(pathToCheck, description) {
    if (fs.existsSync(pathToCheck)) {
        log(`✅ ${description}: Path exists`, 'green');
        return true;
    } else {
        log(`❌ ${description}: Path does not exist`, 'red');
        return false;
    }
}

// Check Java
log('\n📋 Checking Java Development Kit (JDK)...', 'cyan');
const javaOk = checkCommand('java -version', 'Java Runtime');
const javacOk = checkCommand('javac -version', 'Java Compiler');
const javaHomeOk = checkEnvironmentVariable('JAVA_HOME', 'JAVA_HOME environment variable');

// Check Android SDK
log('\n📱 Checking Android SDK...', 'cyan');
const androidHomeOk = checkEnvironmentVariable('ANDROID_HOME', 'ANDROID_HOME environment variable');
const adbOk = checkCommand('adb version', 'Android Debug Bridge (ADB)');

// Check Android Studio
log('\n🛠️  Checking Android Studio...', 'cyan');
let androidStudioOk = false;
const possiblePaths = [
    path.join(process.env.PROGRAMFILES || '', 'Android', 'Android Studio'),
    path.join(process.env['PROGRAMFILES(X86)'] || '', 'Android', 'Android Studio'),
    path.join(process.env.LOCALAPPDATA || '', 'Android', 'Android Studio')
];

for (const studioPath of possiblePaths) {
    if (fs.existsSync(studioPath)) {
        log(`✅ Android Studio: Found at ${studioPath}`, 'green');
        androidStudioOk = true;
        break;
    }
}

if (!androidStudioOk) {
    log('❌ Android Studio: Not found in common locations', 'red');
}

// Check React Native CLI
log('\n⚛️  Checking React Native...', 'cyan');
const rnOk = checkCommand('npx react-native --version', 'React Native CLI');

// Summary
log('\n📊 Setup Summary:', 'cyan');
const allChecks = [
    { name: 'Java Runtime', ok: javaOk },
    { name: 'Java Compiler', ok: javacOk },
    { name: 'JAVA_HOME', ok: javaHomeOk },
    { name: 'ANDROID_HOME', ok: androidHomeOk },
    { name: 'ADB', ok: adbOk },
    { name: 'Android Studio', ok: androidStudioOk },
    { name: 'React Native CLI', ok: rnOk }
];

const passed = allChecks.filter(check => check.ok).length;
const total = allChecks.length;

allChecks.forEach(check => {
    const status = check.ok ? '✅' : '❌';
    const color = check.ok ? 'green' : 'red';
    log(`${status} ${check.name}`, color);
});

log(`\n🎯 Overall: ${passed}/${total} checks passed`, passed === total ? 'green' : 'yellow');

if (passed === total) {
    log('\n🎉 All checks passed! Your Android development environment is ready.', 'green');
    log('You can now run: npm run android', 'cyan');
} else {
    log('\n⚠️  Some checks failed. Please follow the setup instructions in ANDROID_SETUP.md', 'yellow');
    log('Or run the setup checker: check-android-setup.bat', 'cyan');
}

// Additional helpful commands
log('\n🔧 Useful commands:', 'cyan');
log('• npm run android - Build and run on Android', 'reset');
log('• npx react-native doctor - Detailed environment check', 'reset');
log('• adb devices - List connected Android devices', 'reset');
log('• npx react-native start --reset-cache - Start Metro with clean cache', 'reset'); 
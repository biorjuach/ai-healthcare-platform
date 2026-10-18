# Android Development Environment Setup Guide

This guide will help you fix the Android development environment issues for your React Native project.

## Issues to Fix:
- ❌ JDK - Required to compile Java code
- ❌ Android Studio - Required for building and installing your app on Android
- ❌ Android SDK - Required for building and installing your app on Android
- ❌ ANDROID_HOME - Environment variable that points to your Android SDK installation

## Step 1: Install Java Development Kit (JDK)

### Option A: Install OpenJDK 11 or higher
1. Download OpenJDK from: https://adoptium.net/
2. Choose version 11 or higher (LTS recommended)
3. Run the installer and follow the setup wizard
4. Verify installation by opening Command Prompt and running:
   ```bash
   java -version
   javac -version
   ```

### Option B: Install Oracle JDK
1. Download from: https://www.oracle.com/java/technologies/downloads/
2. Choose JDK 11 or higher
3. Run the installer and follow the setup wizard

## Step 2: Install Android Studio

1. Download Android Studio from: https://developer.android.com/studio
2. Run the installer and follow the setup wizard
3. During installation, make sure to install:
   - Android SDK
   - Android SDK Platform
   - Android Virtual Device (AVD)
   - Performance (Intel HAXM)

## Step 3: Configure Android SDK

1. Open Android Studio
2. Go to **Tools** → **SDK Manager**
3. In the **SDK Platforms** tab, make sure you have:
   - Android 13 (API level 33) - **REQUIRED**
   - Android 12 (API level 31) - Recommended
   - Android 11 (API level 30) - Recommended

4. In the **SDK Tools** tab, make sure you have:
   - Android SDK Build-Tools
   - Android SDK Command-line Tools
   - Android Emulator
   - Android SDK Platform-Tools

## Step 4: Set Environment Variables

### For Windows:

1. Open **System Properties** (Win + Pause/Break)
2. Click **Advanced system settings**
3. Click **Environment Variables**
4. Under **System Variables**, add or update:

#### ANDROID_HOME
- Variable name: `ANDROID_HOME`
- Variable value: `C:\Users\[YOUR_USERNAME]\AppData\Local\Android\Sdk`
  (Replace [YOUR_USERNAME] with your actual username)

#### JAVA_HOME
- Variable name: `JAVA_HOME`
- Variable value: `C:\Program Files\Java\jdk-11.0.x`
  (Replace with your actual JDK installation path)

#### Update PATH
Add these to your PATH variable:
```
%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\tools
%ANDROID_HOME%\tools\bin
%JAVA_HOME%\bin
```

### For macOS/Linux:
Add these to your `~/.bash_profile` or `~/.zshrc`:
```bash
export ANDROID_HOME=$HOME/Library/Android/sdk
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$JAVA_HOME/bin
```

## Step 5: Verify Installation

After completing all steps, restart your terminal/command prompt and run:

```bash
# Check Java
java -version
javac -version

# Check Android SDK
adb version

# Check environment variables
echo $ANDROID_HOME  # macOS/Linux
echo %ANDROID_HOME% # Windows

# Check React Native CLI
npx react-native doctor
```

## Step 6: Test Your Setup

1. Navigate to your mobile project directory:
   ```bash
   cd mobile
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start Metro bundler:
   ```bash
   npm start
   ```

4. In a new terminal, run the Android app:
   ```bash
   npm run android
   ```

## Troubleshooting

### Common Issues:

1. **"adb not found"**
   - Make sure ANDROID_HOME is set correctly
   - Restart your terminal after setting environment variables

2. **"Java not found"**
   - Verify JAVA_HOME is set correctly
   - Make sure Java is in your PATH

3. **"Android SDK not found"**
   - Verify ANDROID_HOME points to the correct SDK location
   - Make sure you've installed the required SDK platforms

4. **"Build failed"**
   - Clean and rebuild: `cd android && ./gradlew clean && cd ..`
   - Try: `npx react-native run-android --reset-cache`

### Finding Your SDK Path:
- In Android Studio: **File** → **Settings** → **Appearance & Behavior** → **System Settings** → **Android SDK**
- Default locations:
  - Windows: `C:\Users\[USERNAME]\AppData\Local\Android\Sdk`
  - macOS: `~/Library/Android/sdk`
  - Linux: `~/Android/Sdk`

## Next Steps

Once your environment is properly set up, you should be able to:
1. Run `npx react-native doctor` without errors
2. Build and run your Android app
3. Use Android emulator or physical device for testing

For more help, refer to the official React Native documentation: https://reactnative.dev/docs/environment-setup 
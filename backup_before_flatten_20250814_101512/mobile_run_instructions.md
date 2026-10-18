# 🚀 How to Run the Mobile App

## 📋 Current Setup Status

✅ **Already Installed:**
- Java Runtime & Compiler
- JAVA_HOME environment variable
- ANDROID_HOME environment variable
- Android Debug Bridge (ADB)

❌ **Missing:**
- Android Studio
- React Native CLI

---

## 🔧 Step 1: Install Missing Components

### **Install React Native CLI**
```bash
# Install React Native CLI globally
npm install -g @react-native-community/cli

# Verify installation
npx react-native --version
```

### **Install Android Studio**
1. **Download Android Studio** from: https://developer.android.com/studio
2. **Run the installer** and follow the setup wizard
3. **During installation, make sure to install:**
   - Android SDK
   - Android SDK Platform
   - Android Virtual Device (AVD)
   - Performance (Intel HAXM)

4. **After installation, configure SDK:**
   - Open Android Studio
   - Go to **Tools** → **SDK Manager**
   - In **SDK Platforms** tab, install:
     - ✅ Android 13 (API level 33) - **REQUIRED**
     - ✅ Android 12 (API level 31) - Recommended
   - In **SDK Tools** tab, install:
     - ✅ Android SDK Build-Tools
     - ✅ Android SDK Command-line Tools
     - ✅ Android Emulator
     - ✅ Android SDK Platform-Tools

---

## 📱 Step 2: Set Up Android Device/Emulator

### **Option A: Use Physical Android Device**
1. **Enable Developer Options:**
   - Go to Settings → About Phone
   - Tap "Build Number" 7 times
   - Go back to Settings → Developer Options
   - Enable "USB Debugging"

2. **Connect Device:**
   - Connect your phone via USB
   - Allow USB debugging when prompted
   - Verify connection: `adb devices`

### **Option B: Use Android Emulator**
1. **Create Virtual Device:**
   - Open Android Studio
   - Go to **Tools** → **AVD Manager**
   - Click "Create Virtual Device"
   - Choose a device (e.g., Pixel 4)
   - Select Android 13 (API 33) system image
   - Click "Finish"

2. **Start Emulator:**
   - In AVD Manager, click the play button next to your device
   - Wait for emulator to fully boot

---

## 🚀 Step 3: Run the Mobile App

### **Navigate to Mobile Directory**
```bash
cd mobile
```

### **Install Dependencies**
```bash
npm install
```

### **Start Metro Bundler**
```bash
npm start
```
This will start the Metro bundler and show a QR code.

### **Run on Android**
In a **new terminal window** (keep Metro running):
```bash
npm run android
```

---

## 🔍 Step 4: Verify Everything Works

### **Check Setup Again**
```bash
npm run check-setup
```

### **Run React Native Doctor**
```bash
npx react-native doctor
```

### **List Connected Devices**
```bash
adb devices
```

---

## 🎯 Expected Results

### **When Metro Starts:**
```
Metro waiting on exp://192.168.x.x:8081
Scan the QR code above with Expo Go (Android) or the Camera app (iOS)
```

### **When App Builds Successfully:**
```
BUILD SUCCESSFUL in 45s
1 actionable task: 1 executed
```

### **App Should Open On Device/Emulator:**
- **Login Screen** - User authentication
- **Bottom Tab Navigation** with 4 tabs:
  - 🏠 **Home** - Health dashboard
  - 🩺 **Symptoms** - Symptom reporting
  - 📅 **Appointments** - Appointment management
  - 👤 **Profile** - User profile

---

## 🛠️ Troubleshooting

### **Common Issues & Solutions:**

#### **1. "adb not found"**
```bash
# Restart terminal after setting environment variables
# Or manually add to PATH:
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

#### **2. "Build failed"**
```bash
# Clean and rebuild
cd android && ./gradlew clean && cd ..
npx react-native run-android --reset-cache
```

#### **3. "Metro bundler not starting"**
```bash
# Clear Metro cache
npx react-native start --reset-cache
```

#### **4. "Device not detected"**
```bash
# Check connected devices
adb devices

# If no devices shown:
# - Enable USB debugging on phone
# - Install USB drivers for your phone
# - Try different USB cable
```

#### **5. "Java version issues"**
```bash
# Verify Java version (should be 11+)
java -version
javac -version

# Set JAVA_HOME if needed
export JAVA_HOME=/path/to/your/jdk
```

---

## 📱 App Features to Test

Once the app is running, test these features:

### **🏠 Home Screen**
- Health summary dashboard
- AI recommendations
- Emergency call button
- Health tips

### **🩺 Symptom Report**
- Multi-step symptom reporting
- AI analysis results
- Multi-language support (English/Swahili)
- Location services

### **📅 Appointments**
- View appointments
- Schedule new appointments
- Doctor selection

### **👤 Profile**
- User information
- Medical history
- Settings

---

## 🔗 Backend Integration

### **Ensure Backend is Running**
Make sure your Django backend is running on `http://localhost:8000`:
```bash
# In another terminal, from project root
cd ..
python manage.py runserver
```

### **Test API Connection**
The mobile app will automatically connect to your backend APIs:
- Health check endpoint
- Symptom analysis
- Appointment management
- User authentication

---

## 🎉 Success Indicators

✅ **App launches successfully** on device/emulator  
✅ **Login screen appears** with authentication  
✅ **Bottom navigation works** with 4 tabs  
✅ **Backend connection** shows healthy status  
✅ **Symptom reporting** works with AI analysis  
✅ **Appointments** can be viewed and managed  

**Your mobile app is now running and ready for testing!** 📱✨

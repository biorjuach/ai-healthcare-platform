# Healthcare Mobile App

A React Native mobile application for the AI Healthcare Platform.

## Prerequisites

Before running this app, you need to set up your Android development environment. The following tools are required:

- **JDK 11 or higher** - For compiling Java code
- **Android Studio** - For building and installing the app
- **Android SDK** - For building and installing the app (API level 33+)
- **ANDROID_HOME** - Environment variable pointing to your Android SDK

## Quick Setup

### 1. Check Your Current Setup

Run the setup checker to see what's missing:

```bash
# Windows (PowerShell)
.\check-android-setup.bat

# Or run the verification script
npm run check-setup
```

### 2. Install Missing Components

Follow the detailed setup guide: [ANDROID_SETUP.md](./ANDROID_SETUP.md)

### 3. Verify Installation

After completing the setup, verify everything is working:

```bash
npm run check-setup
npm run doctor
```

## Running the App

### Install Dependencies

```bash
npm install
```

### Start Metro Bundler

```bash
npm start
```

### Run on Android

```bash
npm run android
```

## Development

### Available Scripts

- `npm start` - Start Metro bundler
- `npm run android` - Build and run on Android
- `npm run ios` - Build and run on iOS (macOS only)
- `npm run check-setup` - Verify development environment
- `npm run doctor` - Run React Native doctor
- `npm test` - Run tests
- `npm run lint` - Run ESLint

### Project Structure

```
src/
├── components/     # Reusable UI components
├── screens/        # Screen components
├── navigation/     # Navigation configuration
├── services/       # API services
├── utils/          # Utility functions
└── types/          # TypeScript type definitions
```

## Troubleshooting

### Common Issues

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

### Reset Cache

If you encounter build issues, try clearing the cache:

```bash
# Clear Metro cache
npx react-native start --reset-cache

# Clear Gradle cache
cd android && ./gradlew clean && cd ..

# Clear npm cache
npm cache clean --force
```

### Environment Variables

Make sure these environment variables are set:

**Windows:**
```
ANDROID_HOME=C:\Users\[USERNAME]\AppData\Local\Android\Sdk
JAVA_HOME=C:\Program Files\Java\jdk-11.0.x
```

**macOS/Linux:**
```bash
export ANDROID_HOME=$HOME/Library/Android/sdk
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home
```

## Getting Help

1. Check the [Android Setup Guide](./ANDROID_SETUP.md)
2. Run `npm run check-setup` to diagnose issues
3. Run `npm run doctor` for detailed React Native environment check
4. Check the [React Native documentation](https://reactnative.dev/docs/environment-setup)

## Dependencies

This project uses React Native 0.72.6 with the following key dependencies:

- React Navigation for navigation
- React Native Paper for UI components
- Axios for API calls
- AsyncStorage for local storage
- Vector Icons for icons

See `package.json` for the complete list of dependencies. 
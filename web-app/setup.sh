#!/bin/bash

echo "🚀 Setting up AI Healthcare Platform Web App..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Clean up any existing node_modules and package-lock.json
echo "🧹 Cleaning up existing installation..."
rm -rf node_modules package-lock.json

# Install dependencies with legacy peer deps
echo "📦 Installing dependencies..."
npm install --legacy-peer-deps

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    echo "💡 Trying alternative installation method..."
    npm install --force
    if [ $? -ne 0 ]; then
        echo "❌ Installation failed with both methods"
        exit 1
    fi
fi

echo "✅ Dependencies installed successfully"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Check if backend is running
echo "🔍 Checking backend connection..."
if curl -s http://localhost:8000/api/health/ > /dev/null; then
    echo "✅ Backend is running"
else
    echo "⚠️  Backend is not running on http://localhost:8000"
    echo "   Please start the Django backend server first"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the development server:"
echo "  npm start"
echo ""
echo "To build for production:"
echo "  npm run build"
echo ""
echo "The web app will be available at: http://localhost:3000"
echo ""
echo "Demo credentials:"
echo "  Username: patient1"
echo "  Password: testpass123"

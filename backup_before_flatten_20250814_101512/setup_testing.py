#!/usr/bin/env python3
"""
Setup script for API testing
This script helps prepare the environment and test data for API testing.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def main():
    print("🏥 AI Healthcare Platform - Testing Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("backend"):
        print("❌ Error: Please run this script from the project root directory")
        print("   (where the 'backend' folder is located)")
        return
    
    # Install testing dependencies
    print("\n📦 Installing testing dependencies...")
    if not run_command("pip install -r test_requirements.txt", "Installing test requirements"):
        print("⚠️  You may need to install requests manually: pip install requests")
    
    # Check if Django server is running
    print("\n🔍 Checking if Django server is running...")
    try:
        import requests
        response = requests.get("http://localhost:8000/api/health/", timeout=5)
        if response.status_code == 200:
            print("✅ Django server is running on http://localhost:8000")
        else:
            print("⚠️  Django server responded but health check failed")
    except:
        print("❌ Django server is not running")
        print("\n🚀 To start the server:")
        print("   1. cd backend")
        print("   2. python manage.py runserver")
        print("   3. Keep the server running in a separate terminal")
        return
    
    # Add test data
    print("\n📊 Adding test data...")
    if run_command("cd backend && python manage.py add_test_data", "Adding test data"):
        print("✅ Test data added successfully")
    else:
        print("⚠️  Test data command failed - you may need to run it manually")
        print("   cd backend && python manage.py add_test_data")
    
    # Run API tests
    print("\n🧪 Running API tests...")
    if run_command("python test_apis.py", "Running API tests"):
        print("✅ API tests completed")
    else:
        print("❌ API tests failed")
    
    print("\n🎯 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Check the test results above")
    print("2. Review the generated JSON file for detailed results")
    print("3. Use the web dashboard at http://localhost:8000/dashboard/ for interactive testing")
    print("4. Check server logs for any errors")

if __name__ == "__main__":
    main()

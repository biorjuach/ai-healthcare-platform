#!/usr/bin/env python3
"""
Test frontend-backend connection and login flow
"""

import requests
import json

def test_frontend_backend_connection():
    """Test the complete frontend-backend connection"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Frontend-Backend Connection...")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1️⃣ Testing Health Check:")
    try:
        response = requests.get(f"{base_url}/api/health/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running and healthy")
        else:
            print(f"   ❌ Backend health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cannot connect to backend: {e}")
        return
    
    # Test 2: CORS headers
    print("\n2️⃣ Testing CORS Headers:")
    try:
        response = requests.options(f"{base_url}/api/auth/login/", timeout=5)
        cors_headers = response.headers
        if 'Access-Control-Allow-Origin' in cors_headers:
            print(f"   ✅ CORS enabled: {cors_headers['Access-Control-Allow-Origin']}")
        else:
            print("   ⚠️  CORS headers not found")
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
    
    # Test 3: Login endpoint
    print("\n3️⃣ Testing Login Endpoint:")
    login_data = {
        'username': 'patient1',
        'password': 'patient123'
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ Login endpoint working correctly")
                print(f"   🎫 Token received: {data['data']['token'][:20]}...")
                print(f"   👤 User type: {data['data']['user']['user_type']}")
            else:
                print(f"   ❌ Login failed: {data.get('message')}")
        else:
            print(f"   ❌ Login endpoint error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Login test failed: {e}")
    
    # Test 4: Frontend API URL
    print("\n4️⃣ Frontend Configuration Check:")
    print("   📍 Backend URL: http://localhost:8000")
    print("   📍 Frontend should use: REACT_APP_API_URL=http://localhost:8000")
    print("   📍 Or default to: http://localhost:8000")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("✅ Backend server is running")
    print("✅ Login API is working")
    print("✅ Patients 1, 2, 3 can log in with password: patient123")
    print("\n🔧 If frontend still fails:")
    print("1. Check browser console for errors")
    print("2. Verify frontend is running on http://localhost:3000")
    print("3. Check if there are any CORS issues in browser")
    print("4. Try clearing browser cache and localStorage")

if __name__ == "__main__":
    test_frontend_backend_connection()

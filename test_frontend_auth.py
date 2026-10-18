#!/usr/bin/env python3
"""
Script to test frontend authentication and identify issues
"""

import requests
import json
import time
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_auth():
    """Test backend authentication endpoints"""
    print("=== Testing Backend Authentication ===")
    
    # Test login endpoint
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(
            urljoin(BASE_URL, '/api/auth/login/'),
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Login Response Status: {response.status_code}")
        print(f"Login Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['token']
                user = data['data']['user']
                print(f"✅ Login successful!")
                print(f"Token: {token[:20]}...")
                print(f"User: {user.get('username')} ({user.get('first_name')} {user.get('last_name')})")
                return token, user
            else:
                print(f"❌ Login failed: {data.get('message')}")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    return None, None

def test_protected_endpoints(token):
    """Test protected endpoints with authentication"""
    print("\n=== Testing Protected Endpoints ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    endpoints = [
        '/api/patient/dashboard/',
        '/api/doctor/dashboard/',
        '/api/patients/',
        '/api/patient/symptoms/',
        '/api/patient/appointments/'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                urljoin(BASE_URL, endpoint),
                headers=headers,
                timeout=10
            )
            
            print(f"{endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ Success")
            elif response.status_code == 401:
                print(f"  ❌ Unauthorized")
            else:
                print(f"  ⚠️  Status: {response.status_code}")
                
        except Exception as e:
            print(f"{endpoint}: ❌ Error - {e}")

def test_public_endpoints():
    """Test public endpoints"""
    print("\n=== Testing Public Endpoints ===")
    
    endpoints = [
        '/api/health/',
        '/api/health-tips/',
        '/api/analytics/dashboard/',
        '/api/emergency/alerts/',
        '/api/hospital/capacity/'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                urljoin(BASE_URL, endpoint),
                timeout=10
            )
            
            print(f"{endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ Success")
            else:
                print(f"  ⚠️  Status: {response.status_code}")
                
        except Exception as e:
            print(f"{endpoint}: ❌ Error - {e}")

def create_test_user():
    """Create a test user if needed"""
    print("\n=== Creating Test User ===")
    
    user_data = {
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "1234567890"
    }
    
    try:
        response = requests.post(
            urljoin(BASE_URL, '/api/auth/register/'),
            json=user_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Register Response Status: {response.status_code}")
        print(f"Register Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Test user created successfully!")
                return True
            else:
                print(f"❌ User creation failed: {data.get('message')}")
        else:
            print(f"❌ User creation failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ User creation error: {e}")
    
    return False

def main():
    """Main test function"""
    print("🔍 Frontend Authentication Test")
    print("=" * 50)
    
    # Test public endpoints first
    test_public_endpoints()
    
    # Try to create test user
    user_created = create_test_user()
    
    # Test authentication
    token, user = test_backend_auth()
    
    if token and user:
        # Test protected endpoints
        test_protected_endpoints(token)
        
        print("\n=== Test Summary ===")
        print("✅ Backend authentication is working")
        print("✅ Token generation is working")
        print("✅ User data is being returned")
        print("\n📝 Next Steps:")
        print("1. Start your frontend: npm start")
        print("2. Try logging in with: testuser / testpass123")
        print("3. Check browser console for any errors")
        print("4. If it still crashes, check the network tab for failed requests")
    else:
        print("\n❌ Authentication test failed")
        print("Please check your backend server is running on http://localhost:8000")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test the actual API login endpoint for patients 1, 2, and 3
"""

import requests
import json

def test_api_login():
    """Test the API login endpoint"""
    
    base_url = "http://localhost:8000"
    login_url = f"{base_url}/api/auth/login/"
    
    print("🔍 Testing API login endpoint...")
    print("=" * 50)
    
    # Test each patient
    for patient_num in [1, 2, 3]:
        username = f'patient{patient_num}'
        password = 'patient123'
        
        print(f"\n👤 Testing API login for {username}:")
        
        try:
            # Test login request
            login_data = {
                'username': username,
                'password': password
            }
            
            response = requests.post(
                login_url,
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"   📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ Login successful!")
                    print(f"   🎫 Token: {data['data']['token']}")
                    print(f"   👤 User Type: {data['data']['user']['user_type']}")
                else:
                    print(f"   ❌ Login failed: {data.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📝 Error: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"   📝 Response: {response.text[:200]}")
                    
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection Error: Backend server not running on {base_url}")
            print(f"   💡 Start the backend server with: python manage.py runserver")
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout: Server took too long to respond")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 TROUBLESHOOTING:")
    print("1. If connection errors: Start backend with 'python manage.py runserver'")
    print("2. If login fails: Check if passwords are set correctly")
    print("3. If frontend still fails: Check CORS settings and API URL configuration")

if __name__ == "__main__":
    test_api_login()

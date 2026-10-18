#!/usr/bin/env python
import requests
import json

print("=== FINAL PATIENTS API TEST ===")

# Test login
print("\n1. Testing login...")
login_data = {
    "username": "doctor1",
    "password": "doctor123"
}

try:
    login_response = requests.post(
        "http://localhost:8000/api/auth/login/",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        if login_result.get('success'):
            token = login_result['data']['token']
            print(f"✅ Login successful - Token: {token[:20]}...")
            
            # Test patients API
            print("\n2. Testing patients API...")
            patients_response = requests.get(
                "http://localhost:8000/api/patients/",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }
            )
            
            print(f"Status Code: {patients_response.status_code}")
            
            if patients_response.status_code == 200:
                result = patients_response.json()
                if result.get('success'):
                    patients = result['data']
                    print(f"✅ API Success - Found {len(patients)} patients:")
                    
                    for i, patient in enumerate(patients, 1):
                        user = patient['user']
                        print(f"  {i}. {user['first_name']} {user['last_name']} ({user['username']})")
                        print(f"     Email: {user['email']}")
                        print(f"     Phone: {patient['phone_number']}")
                        print()
                else:
                    print(f"❌ API Error: {result.get('message', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {patients_response.status_code}")
                print(f"Response: {patients_response.text}")
        else:
            print("❌ Login failed - no success in response")
    else:
        print(f"❌ Login failed - status code: {login_response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n=== END TEST ===")


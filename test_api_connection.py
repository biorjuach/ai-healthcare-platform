#!/usr/bin/env python3
"""
Test script to verify API connections between frontend and backend
"""

import requests
import json
from datetime import datetime

# Base URL for the backend
BASE_URL = 'http://localhost:8000'

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/api/health/')
        print(f"Health Check Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Health Check Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Health Check Failed: {response.text}")
            return False
    except Exception as e:
        print(f"Health Check Error: {e}")
        return False

def test_landing_page():
    """Test the landing page endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/')
        print(f"Landing Page Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Landing Page Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Landing Page Failed: {response.text}")
            return False
    except Exception as e:
        print(f"Landing Page Error: {e}")
        return False

def test_doctors_endpoint():
    """Test the doctors endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/api/doctors/')
        print(f"Doctors Endpoint Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Doctors Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Doctors Endpoint Failed: {response.text}")
            return False
    except Exception as e:
        print(f"Doctors Endpoint Error: {e}")
        return False

def test_health_tips():
    """Test the health tips endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/api/health-tips/?language=en')
        print(f"Health Tips Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Health Tips Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Health Tips Failed: {response.text}")
            return False
    except Exception as e:
        print(f"Health Tips Error: {e}")
        return False

def test_login():
    """Test the login endpoint with sample credentials"""
    try:
        login_data = {
            'username': 'patient3',
            'password': 'patient123'
        }
        response = requests.post(f'{BASE_URL}/api/auth/login/', json=login_data)
        print(f"Login Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Login Response: {json.dumps(data, indent=2)}")
            return data.get('data', {}).get('token') if data.get('success') else None
        else:
            print(f"Login Failed: {response.text}")
            return None
    except Exception as e:
        print(f"Login Error: {e}")
        return None

def test_authenticated_endpoints(token):
    """Test authenticated endpoints"""
    if not token:
        print("No token available, skipping authenticated tests")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test patient dashboard
    try:
        response = requests.get(f'{BASE_URL}/api/patient/dashboard/', headers=headers)
        print(f"Patient Dashboard Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Patient Dashboard Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Patient Dashboard Failed: {response.text}")
    except Exception as e:
        print(f"Patient Dashboard Error: {e}")
    
    # Test notifications
    try:
        response = requests.get(f'{BASE_URL}/api/notifications/', headers=headers)
        print(f"Notifications Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Notifications Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Notifications Failed: {response.text}")
    except Exception as e:
        print(f"Notifications Error: {e}")

def main():
    """Run all tests"""
    print("=" * 50)
    print("API Connection Test")
    print("=" * 50)
    print(f"Testing backend at: {BASE_URL}")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Test basic endpoints
    print("1. Testing Health Check...")
    health_ok = test_health_check()
    print()
    
    print("2. Testing Landing Page...")
    landing_ok = test_landing_page()
    print()
    
    print("3. Testing Doctors Endpoint...")
    doctors_ok = test_doctors_endpoint()
    print()
    
    print("4. Testing Health Tips...")
    tips_ok = test_health_tips()
    print()
    
    print("5. Testing Login...")
    token = test_login()
    print()
    
    if token:
        print("6. Testing Authenticated Endpoints...")
        test_authenticated_endpoints(token)
        print()
    
    # Summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Health Check: {'✓' if health_ok else '✗'}")
    print(f"Landing Page: {'✓' if landing_ok else '✗'}")
    print(f"Doctors Endpoint: {'✓' if doctors_ok else '✗'}")
    print(f"Health Tips: {'✓' if tips_ok else '✗'}")
    print(f"Login: {'✓' if token else '✗'}")
    print()
    
    if health_ok and landing_ok:
        print("✅ Backend API is working correctly!")
        print("✅ Frontend should be able to connect to backend")
    else:
        print("❌ Some API endpoints are not working")
        print("❌ Check backend server and endpoints")

if __name__ == '__main__':
    main()

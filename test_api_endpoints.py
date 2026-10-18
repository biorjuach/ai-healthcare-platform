#!/usr/bin/env python3
"""
Test script to check API endpoints and identify issues
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None, headers=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        
        print(f"\n=== Testing {method} {endpoint} ===")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("Response (first 200 chars):", str(result)[:200])
            except:
                print("Response (text):", response.text[:200])
        else:
            print("Error Response:", response.text[:200])
            
    except Exception as e:
        print(f"Exception: {e}")

def main():
    print("Testing API Endpoints...")
    
    # Test health check
    test_endpoint("/api/health/")
    
    # Test health tips
    test_endpoint("/api/health-tips/")
    
    # Test hospital capacity
    test_endpoint("/api/hospital/capacity/")
    
    # Test patient dashboard (will fail without auth)
    test_endpoint("/api/patient/dashboard/")
    
    print("\n=== Testing Login ===")
    
    # Test login with a known user
    login_data = {
        "username": "patient1",
        "password": "testpass123"  # This might be wrong
    }
    
    test_endpoint("/api/auth/login/", method="POST", data=login_data)
    
    print("\n=== Testing with different password ===")
    
    # Try with a simple password
    login_data = {
        "username": "patient1",
        "password": "password123"
    }
    
    test_endpoint("/api/auth/login/", method="POST", data=login_data)

if __name__ == "__main__":
    main()

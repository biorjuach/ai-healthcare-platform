#!/usr/bin/env python3
"""
Script to test and fix API endpoint issues
"""

import requests
import json
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(url, method="GET", data=None, headers=None):
    """Test an endpoint and return the result"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            return f"Unsupported method: {method}"
        
        return {
            'status_code': response.status_code,
            'method': method,
            'url': url,
            'response': response.text[:200] if response.text else "No content"
        }
    except Exception as e:
        return {
            'status_code': 'ERROR',
            'method': method,
            'url': url,
            'response': str(e)
        }

def main():
    """Test all problematic endpoints"""
    
    # Endpoints that should be POST-only but are being accessed with GET
    post_only_endpoints = [
        '/api/sms/webhook/',
        '/api/voice/webhook/',
        '/api/symptoms/analyze/',
        '/api/symptoms/submit/',
        '/api/hospital/capacity/update/',
        '/api/emergency/update-status/'
    ]
    
    # Endpoints that require authentication
    auth_required_endpoints = [
        '/api/patients/',
        '/api/patient/dashboard/',
        '/api/patient/symptoms/',
        '/api/patient/appointments/',
        '/api/doctor/dashboard/'
    ]
    
    print("=== Testing POST-only endpoints with GET (should return 405) ===")
    for endpoint in post_only_endpoints:
        result = test_endpoint(urljoin(BASE_URL, endpoint), "GET")
        print(f"{result['method']} {result['url']}: {result['status_code']}")
    
    print("\n=== Testing POST-only endpoints with POST (should work) ===")
    for endpoint in post_only_endpoints:
        # Send minimal data for POST requests
        data = {"test": "data"}
        result = test_endpoint(urljoin(BASE_URL, endpoint), "POST", data=data)
        print(f"{result['method']} {result['url']}: {result['status_code']}")
    
    print("\n=== Testing auth-required endpoints (should return 401) ===")
    for endpoint in auth_required_endpoints:
        result = test_endpoint(urljoin(BASE_URL, endpoint), "GET")
        print(f"{result['method']} {result['url']}: {result['status_code']}")
    
    print("\n=== Testing public endpoints (should work) ===")
    public_endpoints = [
        '/api/health/',
        '/api/health-tips/',
        '/api/analytics/dashboard/',
        '/api/emergency/alerts/',
        '/api/hospital/capacity/'
    ]
    
    for endpoint in public_endpoints:
        result = test_endpoint(urljoin(BASE_URL, endpoint), "GET")
        print(f"{result['method']} {result['url']}: {result['status_code']}")

if __name__ == "__main__":
    main()

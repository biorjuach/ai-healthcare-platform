#!/usr/bin/env python3
"""
Simplified API Testing Script
Focuses on working APIs and provides detailed error analysis for failing ones.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 10

# Test data for POST requests
TEST_DATA = {
    "sms_webhook": {
        "from": "+254712345678",
        "text": "I have a headache and fever"
    },
    "voice_webhook": {
        "from": "+254712345678",
        "transcript": "I am experiencing chest pain and shortness of breath",
        "language": "english"
    },
    "analyze_symptoms": {
        "symptoms": ["headache", "fever", "fatigue"],
        "patient_id": 1,
        "severity": "moderate"
    },
    "submit_symptom_report": {
        "patient_id": 1,
        "symptoms": ["cough", "fever", "body aches"],
        "severity": "mild",
        "duration": "3 days",
        "additional_notes": "Started after exposure to sick family member"
    },
    "update_emergency_status": {
        "alert_id": 1,
        "status": "resolved",
        "notes": "Patient stabilized and transferred to ward"
    },
    "update_capacity": {
        "ward": "emergency",
        "available_beds": 5,
        "total_beds": 20,
        "status": "normal"
    }
}

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test a single endpoint with detailed error reporting"""
    url = f"{BASE_URL}{endpoint}"
    start_time = time.time()
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method.upper() == "POST":
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers, timeout=TIMEOUT)
        
        response_time = time.time() - start_time
        
        # Get response content
        try:
            response_data = response.json()
            response_text = json.dumps(response_data, indent=2)
        except:
            response_text = response.text[:1000]
        
        result = {
            'endpoint': endpoint,
            'method': method,
            'status': 'SUCCESS' if response.status_code == expected_status else 'FAILED',
            'status_code': response.status_code,
            'expected_status': expected_status,
            'response_time': round(response_time, 3),
            'response': response_text,
            'url': url
        }
        
        return result
        
    except Exception as e:
        return {
            'endpoint': endpoint,
            'method': method,
            'status': 'ERROR',
            'message': str(e),
            'response_time': 0,
            'url': url
        }

def main():
    print("🏥 AI Healthcare Platform - Simplified API Test")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print("=" * 60)
    
    # Test working endpoints first
    print("\n✅ Testing Working APIs:")
    working_endpoints = [
        ("GET", "/api/health/"),
        ("GET", "/api/emergency/alerts/"),
        ("GET", "/api/hospital/capacity/"),
        ("GET", "/api/analytics/dashboard/"),
        ("GET", "/api/analytics/symptoms/"),
        ("GET", "/api/patients/"),
        ("POST", "/api/voice/webhook/", TEST_DATA["voice_webhook"]),
        ("POST", "/api/emergency/update-status/", TEST_DATA["update_emergency_status"]),
    ]
    
    for method, endpoint, *args in working_endpoints:
        data = args[0] if args else None
        result = test_endpoint(method, endpoint, data)
        print(f"  {method} {endpoint} - {result['status']} ({result['status_code']}) - {result['response_time']}s")
    
    # Test problematic endpoints with detailed analysis
    print("\n🔍 Testing Problematic APIs (with detailed analysis):")
    problematic_endpoints = [
        ("POST", "/api/sms/webhook/", TEST_DATA["sms_webhook"]),
        ("POST", "/api/symptoms/analyze/", TEST_DATA["analyze_symptoms"]),
        ("POST", "/api/symptoms/submit/", TEST_DATA["submit_symptom_report"]),
        ("POST", "/api/hospital/capacity/update/", TEST_DATA["update_capacity"]),
    ]
    
    for method, endpoint, data in problematic_endpoints:
        print(f"\n🔍 Testing: {method} {endpoint}")
        result = test_endpoint(method, endpoint, data)
        
        if result['status'] == 'SUCCESS':
            print(f"  ✅ SUCCESS ({result['status_code']}) - {result['response_time']}s")
        elif result['status'] == 'FAILED':
            print(f"  ❌ FAILED ({result['status_code']}) - Expected {result['expected_status']}")
            print(f"  📄 Response: {result['response'][:300]}...")
        else:
            print(f"  ⚠️  ERROR: {result.get('message', 'Unknown error')}")
    
    # Test authentication endpoints
    print("\n🔐 Testing Authentication Endpoints:")
    auth_endpoints = [
        ("GET", "/admin/"),
        ("GET", "/dashboard/"),
    ]
    
    for method, endpoint in auth_endpoints:
        result = test_endpoint(method, endpoint)
        print(f"  {method} {endpoint} - {result['status']} ({result['status_code']}) - {result['response_time']}s")
    
    print("\n" + "=" * 60)
    print("🎯 Troubleshooting Guide:")
    print("=" * 60)
    print("1. For 500 errors - Check Django server logs for detailed error messages")
    print("2. For 400 errors - Verify the data format matches API requirements")
    print("3. For auth issues - Ensure test data exists: cd backend && python manage.py add_test_data")
    print("4. For missing services - Check if AI services are properly configured")
    print("\n📋 Next Steps:")
    print("1. Check your Django server console for error logs")
    print("2. Run: cd backend && python manage.py add_test_data")
    print("3. Verify all required services are running")
    print("4. Check the detailed response content above for specific error messages")

if __name__ == "__main__":
    main()



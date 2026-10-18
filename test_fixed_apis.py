#!/usr/bin/env python3
"""
Test script for the fixed API endpoints
Run this script to verify all APIs are working correctly
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_api_endpoint(method, endpoint, data=None, description=""):
    """Test a single API endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, data=json.dumps(data) if data else None)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        if response.status_code in [200, 201]:
            print(f"✅ {method} {endpoint} - {description} - Status: {response.status_code}")
            return True
        else:
            print(f"❌ {method} {endpoint} - {description} - Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Connection Error (Is Django server running?)")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {str(e)}")
        return False

def main():
    """Test all the fixed API endpoints"""
    print("🔬 Testing Fixed API Endpoints")
    print("=" * 50)
    
    tests = [
        # Doctor Dashboard
        {
            'method': 'GET',
            'endpoint': '/api/doctor/dashboard/',
            'description': 'Doctor Dashboard - Mock data for testing'
        },
        
        # Emergency Management
        {
            'method': 'POST',
            'endpoint': '/api/emergency/update-status/',
            'data': {
                'alert_id': 1,
                'status': 'in_progress',
                'notes': 'Test update from API'
            },
            'description': 'Update Emergency Status'
        },
        
        # Hospital Capacity
        {
            'method': 'POST',
            'endpoint': '/api/hospital/capacity/update/',
            'data': {
                'department': 'General Ward',
                'total_beds': 50,
                'occupied_beds': 35,
                'available_doctors': 8
            },
            'description': 'Update Hospital Capacity'
        },
        
        # Symptom Analysis
        {
            'method': 'POST',
            'endpoint': '/api/symptoms/analyze/',
            'data': {
                'symptoms': 'I have a severe headache and fever',
                'language': 'english'
            },
            'description': 'Analyze Symptoms'
        },
        
        # Symptom Submission
        {
            'method': 'POST',
            'endpoint': '/api/symptoms/submit/',
            'data': {
                'patient_id': 1,
                'symptoms': 'Chest pain and shortness of breath',
                'input_method': 'app',
                'language': 'english'
            },
            'description': 'Submit Symptom Report'
        },
        
        # SMS Webhook
        {
            'method': 'POST',
            'endpoint': '/api/sms/webhook/',
            'data': {
                'from': '+1234567890',
                'text': 'I have fever and headache'
            },
            'description': 'SMS Webhook Processing'
        },
        
        # Voice Webhook
        {
            'method': 'POST',
            'endpoint': '/api/voice/webhook/',
            'data': {
                'from': '+1234567890',
                'transcript': 'I am feeling dizzy and nauseous',
                'language': 'english'
            },
            'description': 'Voice Webhook Processing'
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        success = test_api_endpoint(
            test['method'],
            test['endpoint'],
            test.get('data'),
            test['description']
        )
        if success:
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} APIs working correctly")
    
    if passed == total:
        print("🎉 All APIs are working correctly!")
        return 0
    else:
        print(f"⚠️  {total - passed} APIs need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())

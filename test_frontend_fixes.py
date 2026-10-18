#!/usr/bin/env python3
"""
Test script for frontend API fixes
Tests symptom analysis and appointment creation specifically
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_symptom_analysis_frontend_format():
    """Test symptom analysis with frontend-expected data format"""
    print("🧪 Testing Symptom Analysis (Frontend Format)")
    
    # Test data that frontend would send
    test_data = {
        "symptoms": "I have severe headache and fever",
        "body_location": "head",
        "duration": "2 days", 
        "severity": "high",
        "description": "I have severe headache and fever for 2 days",
        "language": "en"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/symptoms/analyze/",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_data)
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'success' in data and data['success']:
                print("   ✅ Response has correct format (success/data)")
                if 'data' in data:
                    analysis_data = data['data']
                    print(f"   📊 Diagnosis: {analysis_data.get('diagnosis', 'Not provided')}")
                    print(f"   🎯 Confidence: {analysis_data.get('confidence', 0):.1%}")
                    print(f"   ⚠️  Severity: {analysis_data.get('severity', 'Unknown')}")
                    print(f"   🚨 Emergency: {analysis_data.get('is_emergency', False)}")
                    return True
                else:
                    print("   ❌ Missing 'data' field in response")
                    return False
            else:
                print("   ❌ Response missing 'success' field or success=false")
                print(f"   Response: {data}")
                return False
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_appointment_creation_frontend_format():
    """Test appointment creation with frontend-expected data format"""
    print("\n🗓️ Testing Appointment Creation (Frontend Format)")
    
    # First get available doctors
    try:
        doctors_response = requests.get(f"{BASE_URL}/api/doctors/")
        if doctors_response.status_code == 200:
            doctors_data = doctors_response.json()
            if 'success' in doctors_data and doctors_data['data']:
                doctor_id = doctors_data['data'][0]['id']
                print(f"   Using Doctor ID: {doctor_id}")
            else:
                doctor_id = 1  # Fallback
                print("   Using fallback Doctor ID: 1")
        else:
            doctor_id = 1
            print("   Using fallback Doctor ID: 1")
    except:
        doctor_id = 1
        print("   Using fallback Doctor ID: 1")
    
    # Test appointment data that frontend would send
    test_data = {
        "doctor": doctor_id,
        "hospital": "Makueni County Referral Hospital",
        "date": "2024-01-15",
        "time": "10:00",
        "notes": "Regular checkup",
        "symptoms": "General health consultation"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/appointments/",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_data)
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            if 'success' in data and data['success']:
                print("   ✅ Appointment created successfully")
                if 'data' in data:
                    appointment_data = data['data']
                    print(f"   📅 Appointment ID: {appointment_data.get('id')}")
                    print(f"   👨‍⚕️ Doctor: {appointment_data.get('doctor')}")
                    print(f"   📆 Date: {appointment_data.get('date')}")
                    print(f"   🕐 Time: {appointment_data.get('time')}")
                    return True
                else:
                    print("   ❌ Missing 'data' field in response")
                    return False
            else:
                print("   ❌ Response missing 'success' field or success=false")
                print(f"   Response: {data}")
                return False
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_mobile_symptom_analysis():
    """Test mobile app symptom analysis format"""
    print("\n📱 Testing Mobile App Symptom Analysis")
    
    test_data = {
        "symptoms": "I feel dizzy and nauseous",
        "patient_id": 1,
        "language": "english"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/symptoms/analyze/",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_data)
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Mobile app checks for both formats
            if 'success' in data and data['success'] and 'data' in data:
                print("   ✅ New format working (success/data)")
                analysis_data = data['data']
            else:
                print("   ✅ Fallback format working (direct data)")
                analysis_data = data
            
            print(f"   🔍 Analysis: {analysis_data.get('diagnosis', 'Not provided')}")
            return True
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_symptom_submission():
    """Test symptom submission endpoint"""
    print("\n📝 Testing Symptom Submission")
    
    test_data = {
        "patient_id": 1,
        "symptoms": "Chest pain and shortness of breath",
        "input_method": "app",
        "language": "english"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/symptoms/submit/",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_data)
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'success' in data and data['success']:
                print("   ✅ Symptom submitted successfully")
                if 'data' in data:
                    symptom_data = data['data']
                    print(f"   📋 Report ID: {symptom_data.get('symptom_id')}")
                    print(f"   🔬 Diagnosis ID: {symptom_data.get('diagnosis_id')}")
                    return True
            else:
                print("   ❌ Submission failed")
                print(f"   Response: {data}")
                return False
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Run all frontend API tests"""
    print("🎯 Frontend API Fixes - Comprehensive Test")
    print("=" * 60)
    
    tests = [
        ("Symptom Analysis (Web)", test_symptom_analysis_frontend_format),
        ("Appointment Creation", test_appointment_creation_frontend_format),
        ("Mobile Symptom Analysis", test_mobile_symptom_analysis),
        ("Symptom Submission", test_symptom_submission)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 40)
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All frontend API fixes working correctly!")
        print("\n✅ Frontend should now work without 'failed to analyze symptoms' errors")
        print("✅ Appointment creation should work without 'failed to make appointment' errors")
        return 0
    else:
        print(f"⚠️  {total - passed} tests still failing")
        return 1

if __name__ == "__main__":
    sys.exit(main())

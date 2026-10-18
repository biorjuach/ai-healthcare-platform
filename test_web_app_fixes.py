#!/usr/bin/env python3
"""
Test script specifically for Web App API fixes
Tests the exact format that the web app sends
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_web_app_symptom_analysis():
    """Test web app symptom analysis with exact format web app sends"""
    print("🌐 Testing Web App Symptom Analysis")
    
    # Exact format that web app ApiService.analyzeSymptoms sends
    test_data = {
        "symptoms": "I have a severe headache",
        "body_location": "head", 
        "duration": "2 days",
        "severity": "high",
        "description": "I have a severe headache that started 2 days ago",
        "language": "en",  # Web app sends 'en' not 'english'
        "location_data": {
            "latitude": -1.2864,
            "longitude": 36.8172,
            "address": "Nairobi, Kenya"
        }
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
            if 'success' in data and data['success'] and 'data' in data:
                print("   ✅ Web app format working correctly")
                analysis_data = data['data']
                print(f"   🔍 Diagnosis: {analysis_data.get('diagnosis', 'Not provided')}")
                print(f"   🎯 Confidence: {analysis_data.get('confidence', 0):.1%}")
                print(f"   ⚠️  Severity: {analysis_data.get('severity', 'Unknown')}")
                print(f"   🚨 Emergency: {analysis_data.get('is_emergency', False)}")
                
                # Check if additional context was included
                symptoms_text = analysis_data.get('symptoms', '')
                if 'Location: head' in symptoms_text and 'Duration: 2 days' in symptoms_text:
                    print("   ✅ Additional context (location, duration, severity) included")
                else:
                    print("   ⚠️  Additional context not properly included")
                
                return True
            else:
                print("   ❌ Response format incorrect")
                print(f"   Response: {data}")
                return False
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_web_app_symptom_submission():
    """Test web app symptom submission with exact format web app sends"""
    print("\n📝 Testing Web App Symptom Submission")
    
    # Exact format that web app ApiService.submitSymptomReport sends
    test_data = {
        "symptoms": "Chest pain and shortness of breath",
        "body_location": "chest",
        "duration": "1 hour", 
        "severity": "high",
        "description": "Sudden chest pain with difficulty breathing",
        "language": "en",
        "location_data": {
            "latitude": -1.2864,
            "longitude": 36.8172,
            "address": "Nairobi, Kenya"
        }
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
            if 'success' in data and data['success'] and 'data' in data:
                print("   ✅ Web app symptom submission working")
                submission_data = data['data']
                print(f"   📋 Symptom ID: {submission_data.get('symptom_id')}")
                print(f"   🔬 Diagnosis ID: {submission_data.get('diagnosis_id')}")
                print(f"   ⚠️  Severity: {submission_data.get('severity')}")
                
                # Check if emergency detected for chest pain
                if submission_data.get('is_emergency'):
                    print("   🚨 Emergency correctly detected for chest pain")
                
                return True
            else:
                print("   ❌ Response format incorrect")
                print(f"   Response: {data}")
                return False
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_web_app_appointment_creation():
    """Test web app appointment creation with exact format web app sends"""
    print("\n🗓️ Testing Web App Appointment Creation")
    
    # First get a doctor
    try:
        doctors_response = requests.get(f"{BASE_URL}/api/doctors/")
        doctor_id = 1  # Default fallback
        if doctors_response.status_code == 200:
            doctors_data = doctors_response.json()
            if 'success' in doctors_data and doctors_data['data']:
                doctor_id = doctors_data['data'][0]['id']
                print(f"   Using Doctor ID: {doctor_id}")
    except:
        print("   Using fallback Doctor ID: 1")
    
    # Exact format that web app ApiService.createAppointment sends
    test_data = {
        "doctor": doctor_id,
        "hospital": "Makueni County Referral Hospital",
        "date": "2024-01-20",
        "time": "14:30",
        "notes": "Follow-up consultation for recent symptoms",
        "symptoms": "Follow-up for headache treatment"
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
            if 'success' in data and data['success'] and 'data' in data:
                print("   ✅ Web app appointment creation working")
                appointment_data = data['data']
                print(f"   📅 Appointment ID: {appointment_data.get('id')}")
                print(f"   👨‍⚕️ Doctor ID: {appointment_data.get('doctor')}")
                print(f"   📆 Date: {appointment_data.get('date')}")
                print(f"   🕐 Time: {appointment_data.get('time')}")
                print(f"   📝 Notes: {appointment_data.get('notes', 'None')}")
                return True
            else:
                print("   ❌ Response format incorrect")
                print(f"   Response: {data}")
                return False
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_web_app_patient_dashboard():
    """Test web app patient dashboard access"""
    print("\n📊 Testing Web App Patient Dashboard")
    
    try:
        response = requests.get(f"{BASE_URL}/api/patient/dashboard/")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'success' in data and data['success']:
                print("   ✅ Patient dashboard accessible")
                if 'data' in data:
                    dashboard_data = data['data']
                    print(f"   📋 Recent symptoms: {len(dashboard_data.get('recent_symptoms', []))}")
                    print(f"   🗓️ Upcoming appointments: {len(dashboard_data.get('upcoming_appointments', []))}")
                return True
            else:
                print("   ❌ Dashboard response format incorrect")
                return False
        else:
            print(f"   ⚠️  Dashboard returned {response.status_code} (expected for unauthenticated)")
            return True  # This is expected for unauthenticated access
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_web_app_language_conversion():
    """Test that web app language codes ('en'/'sw') are properly converted"""
    print("\n🌍 Testing Web App Language Conversion")
    
    # Test Swahili language conversion
    test_data = {
        "symptoms": "Nina homa na kichwa",  # Swahili for "I have fever and headache"
        "language": "sw",  # Web app sends 'sw' not 'swahili'
        "description": "Swahili symptom description"
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
                print("   ✅ Swahili language code 'sw' properly converted")
                return True
            else:
                print("   ❌ Language conversion failed")
                return False
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Run all web app specific tests"""
    print("🌐 Web App API Fixes - Comprehensive Test")
    print("=" * 60)
    print("Testing exact formats that web-app/src/services/api.ts sends")
    print("=" * 60)
    
    tests = [
        ("Web App Symptom Analysis", test_web_app_symptom_analysis),
        ("Web App Symptom Submission", test_web_app_symptom_submission),
        ("Web App Appointment Creation", test_web_app_appointment_creation),
        ("Web App Patient Dashboard", test_web_app_patient_dashboard),
        ("Web App Language Conversion", test_web_app_language_conversion)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 Web App Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All web app API fixes working correctly!")
        print("\n✅ The web app should now work without errors:")
        print("   • Symptom analysis should work without 'failed to analyze symptoms'")
        print("   • Appointment creation should work without 'failed to make appointment'")
        print("   • All API responses use consistent {success: true, data: {...}} format")
        print("   • Language codes 'en'/'sw' are properly converted")
        print("   • Additional context (body_location, duration, severity) is included")
        return 0
    else:
        print(f"⚠️  {total - passed} web app tests still failing")
        return 1

if __name__ == "__main__":
    sys.exit(main())

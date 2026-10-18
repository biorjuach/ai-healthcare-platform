#!/usr/bin/env python3
"""
Improved API Testing Script - Multiple authentication methods
"""

import requests
import json
import time
import os
import sys
import django

# Setup Django
sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Patient, Doctor

BASE_URL = "http://localhost:8000"
TIMEOUT = 10

def find_users():
    """Find any available doctors and patients"""
    users = {"patient": None, "doctor": None}
    
    # Find any patient
    try:
        patient = Patient.objects.first()
        if patient:
            users["patient"] = {
                "username": patient.user.username,
                "password": "testpass123"
            }
            print(f"✅ Found patient: {patient.user.username}")
    except:
        print("❌ No patients found")
    
    # Find any doctor
    try:
        doctor = Doctor.objects.first()
        if doctor:
            users["doctor"] = {
                "username": doctor.user.username,
                "password": "testpass123"
            }
            print(f"✅ Found doctor: {doctor.user.username}")
    except:
        print("❌ No doctors found")
    
    return users

def try_login_methods(session, username, password):
    """Try different login methods"""
    methods = [
        # Method 1: Django admin login
        {
            'url': f"{BASE_URL}/admin/login/",
            'data': {'username': username, 'password': password, 'next': '/admin/'}
        },
        # Method 2: Try direct session login
        {
            'url': f"{BASE_URL}/admin/",
            'data': {'username': username, 'password': password}
        }
    ]
    
    for i, method in enumerate(methods, 1):
        try:
            print(f"  Trying login method {i}...")
            response = session.post(method['url'], data=method['data'], timeout=TIMEOUT)
            
            # Check if login was successful
            if response.status_code == 200:
                # Try to access a protected page to verify login
                test_response = session.get(f"{BASE_URL}/admin/", timeout=TIMEOUT)
                if 'logout' in test_response.text.lower() or 'welcome' in test_response.text.lower():
                    print(f"  ✅ Login method {i} successful!")
                    return True
                else:
                    print(f"  ❌ Login method {i} failed - not authenticated")
            else:
                print(f"  ❌ Login method {i} failed - status {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Login method {i} error: {e}")
    
    return False

def test_endpoint(session, method, endpoint, data=None):
    """Test endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = session.get(url, timeout=TIMEOUT)
        else:
            headers = {'Content-Type': 'application/json'}
            response = session.post(url, json=data, headers=headers, timeout=TIMEOUT)
        
        return {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'response': response.text[:200]
        }
    except Exception as e:
        return {'status_code': 0, 'success': False, 'response': str(e)}

def main():
    print("🏥 Improved API Testing - Multiple Auth Methods")
    print("=" * 55)
    
    # Find users
    users = find_users()
    
    # Setup sessions
    patient_session = requests.Session()
    doctor_session = requests.Session()
    anonymous_session = requests.Session()
    
    # Login users with multiple methods
    patient_auth = False
    doctor_auth = False
    
    if users["patient"]:
        print(f"\n🔐 Testing patient authentication for {users['patient']['username']}:")
        patient_auth = try_login_methods(patient_session, users["patient"]["username"], users["patient"]["password"])
        print(f"Patient auth: {'✅' if patient_auth else '❌'}")
    
    if users["doctor"]:
        print(f"\n🔐 Testing doctor authentication for {users['doctor']['username']}:")
        doctor_auth = try_login_methods(doctor_session, users["doctor"]["username"], users["doctor"]["password"])
        print(f"Doctor auth: {'✅' if doctor_auth else '❌'}")
    
    # Test endpoints
    endpoints = [
        # Public APIs
        ("GET", "/api/health/", None, "anonymous"),
        ("GET", "/api/emergency/alerts/", None, "anonymous"),
        ("GET", "/api/hospital/capacity/", None, "anonymous"),
        ("GET", "/api/analytics/dashboard/", None, "anonymous"),
        ("GET", "/api/patients/", None, "anonymous"),
        
        # Patient APIs (if auth works)
        ("GET", "/api/patient/dashboard/", None, "patient"),
        ("GET", "/api/patient/symptoms/", None, "patient"),
        
        # Doctor APIs (if auth works)
        ("GET", "/api/doctor/dashboard/", None, "doctor"),
    ]
    
    print("\n🧪 Testing APIs:")
    for method, endpoint, data, session_type in endpoints:
        if session_type == "patient" and not patient_auth:
            print(f"  ⚠️  {method} {endpoint} - SKIPPED (no patient auth)")
            continue
        elif session_type == "doctor" and not doctor_auth:
            print(f"  ⚠️  {method} {endpoint} - SKIPPED (no doctor auth)")
            continue
        
        session = patient_session if session_type == "patient" else doctor_session if session_type == "doctor" else anonymous_session
        result = test_endpoint(session, method, endpoint, data)
        
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {method} {endpoint} - {result['status_code']}")
    
    print("\n🎯 Summary:")
    print(f"- Patient authentication: {'✅ Working' if patient_auth else '❌ Failed'}")
    print(f"- Doctor authentication: {'✅ Working' if doctor_auth else '❌ Failed'}")
    print("- Script automatically found and used existing users")
    print("- Future users will be automatically detected")
    
    if not patient_auth or not doctor_auth:
        print("\n🔧 Authentication Troubleshooting:")
        print("1. Check if Django admin is accessible at: http://localhost:8000/admin/")
        print("2. Try logging in manually with the test credentials")
        print("3. Verify the users exist in Django admin")
        print("4. Check Django server logs for authentication errors")

if __name__ == "__main__":
    main()

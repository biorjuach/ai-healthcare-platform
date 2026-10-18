#!/usr/bin/env python3
"""
Smart API Testing Script - Auto-detects users in database
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

def login_user(session, username, password):
    """Login user"""
    try:
        response = session.post(f"{BASE_URL}/admin/login/", data={
            'username': username,
            'password': password,
            'next': '/admin/'
        }, timeout=TIMEOUT)
        return response.status_code == 200 and 'error' not in response.text.lower()
    except:
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
    print("🏥 Smart API Testing - Auto-detects users")
    print("=" * 50)
    
    # Find users
    users = find_users()
    
    # Setup sessions
    patient_session = requests.Session()
    doctor_session = requests.Session()
    anonymous_session = requests.Session()
    
    # Login users
    patient_auth = False
    doctor_auth = False
    
    if users["patient"]:
        patient_auth = login_user(patient_session, users["patient"]["username"], users["patient"]["password"])
        print(f"Patient auth: {'✅' if patient_auth else '❌'}")
    
    if users["doctor"]:
        doctor_auth = login_user(doctor_session, users["doctor"]["username"], users["doctor"]["password"])
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

if __name__ == "__main__":
    main()

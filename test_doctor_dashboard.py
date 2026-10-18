#!/usr/bin/env python3
"""
Test script to check doctor dashboard endpoint and appointment data
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Doctor, Patient, Appointment
from django.utils import timezone

def test_appointments_in_database():
    """Check what appointments exist in the database"""
    print("🔍 Checking appointments in database...")
    
    # Check all appointments
    all_appointments = Appointment.objects.all()
    print(f"Total appointments in database: {all_appointments.count()}")
    
    if all_appointments.count() > 0:
        print("\n📋 Recent appointments:")
        for appt in all_appointments.order_by('-appointment_date')[:5]:
            print(f"  - {appt.patient.user.first_name} {appt.patient.user.last_name}")
            print(f"    Date: {appt.appointment_date}")
            print(f"    Status: {appt.status}")
            print(f"    Doctor: {appt.doctor.user.first_name} {appt.doctor.user.last_name}")
            print()
    
    # Check today's appointments
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(
        appointment_date__date=today,
        status='scheduled'
    )
    print(f"Today's appointments: {today_appointments.count()}")
    
    # Check upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=today,
        status='scheduled'
    ).order_by('appointment_date')
    print(f"Upcoming appointments: {upcoming_appointments.count()}")
    
    if upcoming_appointments.count() > 0:
        print("\n📅 Upcoming appointments:")
        for appt in upcoming_appointments[:5]:
            print(f"  - {appt.patient.user.first_name} {appt.patient.user.last_name}")
            print(f"    Date: {appt.appointment_date}")
            print(f"    Doctor: {appt.doctor.user.first_name} {appt.doctor.user.last_name}")
            print()

def test_doctor_users():
    """Check doctor users in the database"""
    print("👨‍⚕️ Checking doctor users...")
    
    doctors = Doctor.objects.all()
    print(f"Total doctors: {doctors.count()}")
    
    for doctor in doctors:
        print(f"  - {doctor.user.username}: {doctor.user.first_name} {doctor.user.last_name}")
        print(f"    Specialization: {doctor.specialization}")
        print(f"    Email: {doctor.user.email}")
        print()

def test_api_endpoint():
    """Test the doctor dashboard API endpoint"""
    print("🌐 Testing API endpoint...")
    
    try:
        # Test without authentication
        response = requests.get('http://localhost:8000/api/doctor/dashboard/')
        print(f"Status without auth: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        # Test health endpoint
        health_response = requests.get('http://localhost:8000/api/health/')
        print(f"Health endpoint status: {health_response.status_code}")
        
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    print("🏥 Doctor Dashboard Test Script")
    print("=" * 50)
    
    test_appointments_in_database()
    print("-" * 30)
    test_doctor_users()
    print("-" * 30)
    test_api_endpoint()
    
    print("\n✅ Test completed!")

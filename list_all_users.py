#!/usr/bin/env python
"""
Script to list all users in the backend database with detailed information.
Shows regular users, patients, doctors, and their profiles.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Patient, Doctor, UserProfile

def list_all_users():
    """List all users in the database with detailed information"""
    print("👥 ALL USERS IN BACKEND DATABASE")
    print("=" * 60)
    
    # Get all users
    all_users = User.objects.all().order_by('date_joined')
    
    if not all_users.exists():
        print("❌ No users found in the database!")
        return
    
    print(f"📊 Total users found: {all_users.count()}")
    print()
    
    # Count by type
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    regular_users = User.objects.filter(patient__isnull=True, doctor__isnull=True)
    
    print(f"🏥 Doctors: {doctors.count()}")
    print(f"👤 Patients: {patients.count()}")
    print(f"👤 Regular Users: {regular_users.count()}")
    print()
    
    # List all users with details
    for i, user in enumerate(all_users, 1):
        print(f"{i:2d}. USER: {user.username}")
        print(f"    📧 Email: {user.email}")
        print(f"    👤 Name: {user.first_name} {user.last_name}")
        print(f"    📅 Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M')}")
        print(f"    ✅ Active: {'Yes' if user.is_active else 'No'}")
        print(f"    🔧 Staff: {'Yes' if user.is_staff else 'No'}")
        print(f"    👑 Superuser: {'Yes' if user.is_superuser else 'No'}")
        
        # Check if user is a patient
        try:
            patient = Patient.objects.get(user=user)
            print(f"    🏥 Role: PATIENT")
            print(f"    📱 Phone: {patient.phone_number}")
            print(f"    🎂 DOB: {patient.date_of_birth}")
            print(f"    ⚧ Gender: {patient.gender}")
            print(f"    📍 Address: {patient.address}")
            print(f"    🚨 Emergency Contact: {patient.emergency_contact}")
            print(f"    📍 Location: {patient.location}")
            print(f"    🩸 Blood Type: {patient.blood_type}")
            print(f"    ⚠️ Allergies: {patient.allergies}")
            print(f"    📋 Medical History: {patient.medical_history[:100]}{'...' if len(patient.medical_history) > 100 else ''}")
        except Patient.DoesNotExist:
            pass
        
        # Check if user is a doctor
        try:
            doctor = Doctor.objects.get(user=user)
            print(f"    🏥 Role: DOCTOR")
            print(f"    🎓 Specialization: {doctor.specialization}")
            print(f"    📜 License: {doctor.license_number}")
            print(f"    📅 Experience: {doctor.years_of_experience} years")
            print(f"    🏥 Hospital: {doctor.hospital_affiliation}")
            print(f"    ✅ Available: {'Yes' if doctor.is_available else 'No'}")
        except Doctor.DoesNotExist:
            pass
        
        # Check if user has a profile
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"    📋 Has UserProfile: Yes")
        except UserProfile.DoesNotExist:
            print(f"    📋 Has UserProfile: No")
        
        print("-" * 60)
    
    # Summary statistics
    print("\n📈 SUMMARY STATISTICS:")
    print(f"   • Total Users: {all_users.count()}")
    print(f"   • Active Users: {all_users.filter(is_active=True).count()}")
    print(f"   • Staff Users: {all_users.filter(is_staff=True).count()}")
    print(f"   • Superusers: {all_users.filter(is_superuser=True).count()}")
    print(f"   • Patients: {patients.count()}")
    print(f"   • Doctors: {doctors.count()}")
    print(f"   • Regular Users: {regular_users.count()}")
    
    # Show recent activity
    recent_users = all_users.order_by('-date_joined')[:5]
    print(f"\n🕒 RECENT USERS (Last 5):")
    for user in recent_users:
        print(f"   • {user.username} - {user.date_joined.strftime('%Y-%m-%d %H:%M')}")

def list_users_by_type(user_type):
    """List users filtered by type"""
    print(f"👥 {user_type.upper()} USERS")
    print("=" * 40)
    
    if user_type.lower() == 'patients':
        users = User.objects.filter(patient__isnull=False).order_by('date_joined')
        print(f"📊 Total patients: {users.count()}")
        for user in users:
            patient = Patient.objects.get(user=user)
            print(f"   • {user.username} ({user.email}) - {patient.phone_number}")
    
    elif user_type.lower() == 'doctors':
        users = User.objects.filter(doctor__isnull=False).order_by('date_joined')
        print(f"📊 Total doctors: {users.count()}")
        for user in users:
            doctor = Doctor.objects.get(user=user)
            print(f"   • {user.username} ({user.email}) - {doctor.specialization}")
    
    elif user_type.lower() == 'staff':
        users = User.objects.filter(is_staff=True).order_by('date_joined')
        print(f"📊 Total staff: {users.count()}")
        for user in users:
            print(f"   • {user.username} ({user.email}) - {'Superuser' if user.is_superuser else 'Staff'}")
    
    else:
        print(f"❌ Unknown user type: {user_type}")
        print("Available types: patients, doctors, staff")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        list_users_by_type(sys.argv[1])
    else:
        list_all_users()

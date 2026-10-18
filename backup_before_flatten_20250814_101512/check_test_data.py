#!/usr/bin/env python3
"""
Check Test Data Script
This script checks if test data exists and helps troubleshoot authentication issues.
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Patient, Doctor

def check_test_data():
    """Check if test data exists in the database"""
    print("🔍 Checking Test Data...")
    print("=" * 50)
    
    # Check for test users
    print("\n👥 Checking Test Users:")
    
    # Check patient1
    try:
        patient1_user = User.objects.get(username='patient1')
        print(f"✅ patient1 user exists (ID: {patient1_user.id})")
        
        # Check if patient1 has a Patient profile
        try:
            patient1_profile = Patient.objects.get(user=patient1_user)
            print(f"✅ patient1 has Patient profile (ID: {patient1_profile.id})")
            print(f"   - Name: {patient1_profile.user.get_full_name()}")
            print(f"   - Phone: {patient1_profile.phone_number}")
            print(f"   - Gender: {patient1_profile.gender}")
        except Patient.DoesNotExist:
            print("❌ patient1 user exists but NO Patient profile found!")
            print("   This is why /api/patient/dashboard/ returns 'Patient profile not found'")
    except User.DoesNotExist:
        print("❌ patient1 user does not exist")
    
    # Check testdoctor
    try:
        doctor_user = User.objects.get(username='testdoctor')
        print(f"✅ testdoctor user exists (ID: {doctor_user.id})")
        
        # Check if testdoctor has a Doctor profile
        try:
            doctor_profile = Doctor.objects.get(user=doctor_user)
            print(f"✅ testdoctor has Doctor profile (ID: {doctor_profile.id})")
            print(f"   - Name: {doctor_profile.user.get_full_name()}")
            print(f"   - Specialization: {doctor_profile.specialization}")
            print(f"   - License: {doctor_profile.license_number}")
        except Doctor.DoesNotExist:
            print("❌ testdoctor user exists but NO Doctor profile found!")
    except User.DoesNotExist:
        print("❌ testdoctor user does not exist")
    
    # Check other test patients
    print("\n👥 Checking Other Test Patients:")
    for username in ['patient2', 'patient3']:
        try:
            user = User.objects.get(username=username)
            print(f"✅ {username} user exists (ID: {user.id})")
            
            try:
                patient_profile = Patient.objects.get(user=user)
                print(f"✅ {username} has Patient profile (ID: {patient_profile.id})")
            except Patient.DoesNotExist:
                print(f"❌ {username} user exists but NO Patient profile found!")
        except User.DoesNotExist:
            print(f"❌ {username} user does not exist")
    
    # Summary
    print("\n📊 Summary:")
    total_users = User.objects.count()
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    
    print(f"Total Users: {total_users}")
    print(f"Total Patients: {total_patients}")
    print(f"Total Doctors: {total_doctors}")
    
    # Check if we need to run add_test_data
    if total_patients == 0 or total_doctors == 0:
        print("\n⚠️  Missing test data detected!")
        print("Run this command to add test data:")
        print("   cd backend && python manage.py add_test_data")
    else:
        print("\n✅ Test data appears to be properly set up")
    
    # Test credentials
    print("\n🔐 Test Credentials:")
    print("Patient Login:")
    print("   Username: patient1")
    print("   Password: testpass123")
    print("\nDoctor Login:")
    print("   Username: testdoctor")
    print("   Password: testpass123")

def fix_missing_profiles():
    """Try to fix missing patient/doctor profiles"""
    print("\n🔧 Attempting to fix missing profiles...")
    
    # Try to create missing patient profile for patient1
    try:
        patient1_user = User.objects.get(username='patient1')
        if not Patient.objects.filter(user=patient1_user).exists():
            Patient.objects.create(
                user=patient1_user,
                date_of_birth='1985-05-15',
                gender='Female',
                address='123 Main St, Nairobi',
                phone_number='+254712345678',
                emergency_contact='+254734567890'
            )
            print("✅ Created missing Patient profile for patient1")
    except User.DoesNotExist:
        print("❌ patient1 user not found - cannot create profile")
    
    # Try to create missing doctor profile for testdoctor
    try:
        doctor_user = User.objects.get(username='testdoctor')
        if not Doctor.objects.filter(user=doctor_user).exists():
            Doctor.objects.create(
                user=doctor_user,
                specialization='general',
                license_number='DOC123456',
                years_of_experience=10,
                hospital_affiliation='Makueni County Referral Hospital'
            )
            print("✅ Created missing Doctor profile for testdoctor")
    except User.DoesNotExist:
        print("❌ testdoctor user not found - cannot create profile")

def main():
    """Main function"""
    print("🏥 AI Healthcare Platform - Test Data Checker")
    print("=" * 60)
    
    check_test_data()
    
    # Ask if user wants to try to fix missing profiles
    print("\n" + "=" * 50)
    response = input("Would you like to attempt to fix missing profiles? (y/n): ")
    
    if response.lower() in ['y', 'yes']:
        fix_missing_profiles()
        print("\n🔄 Re-checking after fixes...")
        check_test_data()
    
    print("\n🎯 Next Steps:")
    print("1. If test data is missing, run: cd backend && python manage.py add_test_data")
    print("2. Use the enhanced testing script: python test_apis_with_auth.py")
    print("3. Check server logs for any additional errors")

if __name__ == "__main__":
    main()

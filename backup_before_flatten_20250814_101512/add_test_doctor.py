#!/usr/bin/env python3
"""
Add Test Doctor Script
Adds a test doctor to the database if one doesn't exist.
"""

import os
import sys
import django

# Setup Django
sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Doctor

def add_test_doctor():
    """Add a test doctor if one doesn't exist"""
    print("🔧 Adding test doctor...")
    
    # Check if testdoctor already exists
    try:
        existing_doctor = User.objects.get(username='testdoctor')
        print(f"✅ testdoctor already exists (ID: {existing_doctor.id})")
        return True
    except User.DoesNotExist:
        pass
    
    # Create test doctor user
    try:
        doctor_user = User.objects.create_user(
            username='testdoctor',
            email='doctor@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        doctor_user.is_staff = True
        doctor_user.save()
        
        # Create doctor profile
        doctor_profile = Doctor.objects.create(
            user=doctor_user,
            specialization='general',
            license_number='DOC123456',
            years_of_experience=10,
            hospital_affiliation='Makueni County Referral Hospital'
        )
        
        print(f"✅ Created test doctor: {doctor_user.username} (ID: {doctor_user.id})")
        print(f"✅ Created doctor profile: {doctor_profile.specialization}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating test doctor: {e}")
        return False

def main():
    print("🏥 Add Test Doctor")
    print("=" * 30)
    
    success = add_test_doctor()
    
    if success:
        print("\n🎯 Test doctor ready!")
        print("Username: testdoctor")
        print("Password: testpass123")
        print("\nYou can now run: python test_apis_smart.py")
    else:
        print("\n❌ Failed to create test doctor")

if __name__ == "__main__":
    main()

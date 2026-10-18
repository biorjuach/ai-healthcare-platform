#!/usr/bin/env python3
"""
Fix User Passwords Script
Sets consistent passwords for all users to enable authentication testing.
"""

import os
import sys
import django

# Setup Django
sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Patient, Doctor

def fix_user_passwords():
    """Set consistent passwords for all users"""
    print("🔧 Fixing user passwords...")
    
    # Default password for all users
    default_password = "testpass123"
    
    # Get all users
    users = User.objects.all()
    print(f"Found {users.count()} users in database")
    
    fixed_count = 0
    for user in users:
        try:
            # Set the password
            user.set_password(default_password)
            user.save()
            fixed_count += 1
            print(f"✅ Fixed password for: {user.username}")
        except Exception as e:
            print(f"❌ Error fixing password for {user.username}: {e}")
    
    print(f"\n🎯 Fixed passwords for {fixed_count} users")
    print(f"All users now have password: {default_password}")
    
    # Show available users for testing
    print("\n📋 Available users for testing:")
    
    patients = Patient.objects.all()
    if patients.exists():
        print("\n👥 Patients:")
        for patient in patients:
            print(f"  - {patient.user.username} (ID: {patient.user.id})")
    
    doctors = Doctor.objects.all()
    if doctors.exists():
        print("\n👨‍⚕️ Doctors:")
        for doctor in doctors:
            print(f"  - {doctor.user.username} (ID: {doctor.user.id})")
    
    return True

def main():
    print("🏥 Fix User Passwords")
    print("=" * 30)
    
    success = fix_user_passwords()
    
    if success:
        print("\n🎯 All users ready for testing!")
        print("Password for all users: testpass123")
        print("\nYou can now run: python test_apis_smart.py")
    else:
        print("\n❌ Failed to fix user passwords")

if __name__ == "__main__":
    main()

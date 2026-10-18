#!/usr/bin/env python3
"""
Script to check doctor password and set it if needed
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Doctor

def check_and_fix_doctor_password():
    """Check doctor password and set it if needed"""
    print("🔍 Checking doctor password...")
    
    try:
        # Get the doctor user
        doctor_user = User.objects.get(username='doctor1')
        print(f"Found doctor: {doctor_user.first_name} {doctor_user.last_name}")
        print(f"Email: {doctor_user.email}")
        print(f"Is active: {doctor_user.is_active}")
        
        # Check if password is set
        if doctor_user.check_password('password123'):
            print("✅ Password 'password123' is correct!")
        else:
            print("❌ Password 'password123' is incorrect")
            print("Setting password to 'password123'...")
            doctor_user.set_password('password123')
            doctor_user.save()
            print("✅ Password set to 'password123'")
        
        # Also check other common passwords
        test_passwords = ['password', '123456', 'admin', 'doctor', 'test']
        for pwd in test_passwords:
            if doctor_user.check_password(pwd):
                print(f"✅ Password '{pwd}' works!")
                break
        
    except User.DoesNotExist:
        print("❌ Doctor user 'doctor1' not found")
        return
    
    # Check other doctor users too
    print("\n👨‍⚕️ Checking other doctor users...")
    doctors = Doctor.objects.all()
    for doctor in doctors:
        user = doctor.user
        print(f"  - {user.username}: {user.first_name} {user.last_name}")
        if user.check_password('password123'):
            print(f"    ✅ Password 'password123' works")
        else:
            print(f"    ❌ Password 'password123' doesn't work")
            # Set password for this doctor too
            user.set_password('password123')
            user.save()
            print(f"    ✅ Set password to 'password123'")

if __name__ == "__main__":
    print("🏥 Doctor Password Checker")
    print("=" * 40)
    check_and_fix_doctor_password()
    print("\n✅ Done!")

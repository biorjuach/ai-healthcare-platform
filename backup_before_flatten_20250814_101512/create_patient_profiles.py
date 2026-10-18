#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Patient

def create_patient_profiles():
    """Create Patient profiles for users who don't have them"""
    users_without_patients = []
    
    for user in User.objects.all():
        try:
            Patient.objects.get(user=user)
            print(f"✅ User {user.username} already has a Patient profile")
        except Patient.DoesNotExist:
            users_without_patients.append(user)
            print(f"❌ User {user.username} needs a Patient profile")
    
    if not users_without_patients:
        print("🎉 All users already have Patient profiles!")
        return
    
    print(f"\n📝 Creating Patient profiles for {len(users_without_patients)} users...")
    
    for user in users_without_patients:
        try:
            # Create a basic Patient profile with default values
            patient = Patient.objects.create(
                user=user,
                date_of_birth=date(1990, 1, 1),  # Default date
                gender='Not specified',
                address='Address not provided',
                phone_number='Phone not provided',
                emergency_contact='Emergency contact not provided',
                medical_history='',
                allergies=''
            )
            print(f"✅ Created Patient profile for {user.username}")
        except Exception as e:
            print(f"❌ Failed to create Patient profile for {user.username}: {e}")
    
    print("\n🎉 Patient profile creation completed!")

if __name__ == '__main__':
    create_patient_profiles()

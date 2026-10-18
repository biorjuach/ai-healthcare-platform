#!/usr/bin/env python
"""
Script to find specific patients by username.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Patient

def find_specific_patients():
    """Find specific patients by username"""
    print("🔍 Searching for specific patients...")
    
    # List of patients to search for
    patients_to_find = [
        'patient1',
        'patient2', 
        'patient3',
        'demo_patient_1',
        'demo_patient_2',
        'demo_patient_3'
    ]
    
    found_patients = []
    not_found = []
    
    for username in patients_to_find:
        try:
            user = User.objects.get(username=username)
            try:
                patient = Patient.objects.get(user=user)
                found_patients.append({
                    'username': username,
                    'user': user,
                    'patient': patient
                })
                print(f"✅ Found: {username}")
            except Patient.DoesNotExist:
                print(f"⚠️  User exists but no patient profile: {username}")
        except User.DoesNotExist:
            not_found.append(username)
            print(f"❌ Not found: {username}")
    
    print(f"\n📊 Summary:")
    print(f"   • Found: {len(found_patients)} patients")
    print(f"   • Not found: {len(not_found)} users")
    
    if found_patients:
        print(f"\n👥 Found Patients:")
        for item in found_patients:
            user = item['user']
            patient = item['patient']
            print(f"   • {user.username} ({user.email})")
            print(f"     - Name: {user.first_name} {user.last_name}")
            print(f"     - Phone: {patient.phone_number}")
            print(f"     - DOB: {patient.date_of_birth}")
            print(f"     - Gender: {patient.gender}")
            print(f"     - Address: {patient.address}")
            print()
    
    if not_found:
        print(f"\n❌ Not Found:")
        for username in not_found:
            print(f"   • {username}")

if __name__ == '__main__':
    find_specific_patients()

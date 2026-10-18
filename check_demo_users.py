#!/usr/bin/env python
"""
Script to check for and optionally remove demo users from the database.
Run this to see what demo data exists and optionally clean it up.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Patient, Doctor

def check_demo_users():
    """Check for demo users in the database"""
    print("🔍 Checking for demo users in the database...")
    
    # Check for demo doctors
    demo_doctors = User.objects.filter(
        username__startswith='dr.',
        email__endswith='@demo.com'
    )
    
    print(f"\n📋 Found {demo_doctors.count()} demo doctors:")
    for doctor in demo_doctors:
        print(f"   - {doctor.username} ({doctor.email})")
    
    # Check for demo patients
    demo_patients = User.objects.filter(
        username__in=['patient1', 'patient2', 'patient3'],
        email__endswith='@demo.com'
    )
    
    print(f"\n👥 Found {demo_patients.count()} demo patients:")
    for patient in demo_patients:
        print(f"   - {patient.username} ({patient.email})")
    
    # Check for test users
    test_users = User.objects.filter(
        username__in=['testdoctor', 'test_patient', 'web_test_patient'],
        email__endswith='@example.com'
    )
    
    print(f"\n🧪 Found {test_users.count()} test users:")
    for user in test_users:
        print(f"   - {user.username} ({user.email})")
    
    total_demo = demo_doctors.count() + demo_patients.count() + test_users.count()
    
    if total_demo > 0:
        print(f"\n⚠️  Total demo/test users found: {total_demo}")
        print("\nTo remove these users, run: python check_demo_users.py --remove")
    else:
        print("\n✅ No demo users found in the database!")

def remove_demo_users():
    """Remove demo users from the database"""
    print("🗑️  Removing demo users from the database...")
    
    # Remove demo doctors
    demo_doctors = User.objects.filter(
        username__startswith='dr.',
        email__endswith='@demo.com'
    )
    demo_doctors_count = demo_doctors.count()
    demo_doctors.delete()
    print(f"   Removed {demo_doctors_count} demo doctors")
    
    # Remove demo patients
    demo_patients = User.objects.filter(
        username__in=['patient1', 'patient2', 'patient3'],
        email__endswith='@demo.com'
    )
    demo_patients_count = demo_patients.count()
    demo_patients.delete()
    print(f"   Removed {demo_patients_count} demo patients")
    
    # Remove test users
    test_users = User.objects.filter(
        username__in=['testdoctor', 'test_patient', 'web_test_patient'],
        email__endswith='@example.com'
    )
    test_users_count = test_users.count()
    test_users.delete()
    print(f"   Removed {test_users_count} test users")
    
    total_removed = demo_doctors_count + demo_patients_count + test_users_count
    print(f"\n✅ Removed {total_removed} demo/test users from the database!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--remove':
        remove_demo_users()
    else:
        check_demo_users()

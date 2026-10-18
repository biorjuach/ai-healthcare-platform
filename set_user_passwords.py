#!/usr/bin/env python3
"""
Script to set passwords for existing users
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
from django.contrib.auth.hashers import make_password

def set_user_passwords():
    """Set simple passwords for all users"""
    
    # Password for patients
    patient_password = 'patient123'
    
    # Password for doctors
    doctor_password = 'doctor123'
    
    # Password for admin
    admin_password = 'admin123'
    
    # Get all users
    users = User.objects.all()
    
    print("Setting passwords for existing users...")
    
    for user in users:
        if user.username == 'admin':
            user.password = make_password(admin_password)
            print(f"Set admin password for {user.username}")
        elif user.username.startswith('doctor') or user.username == 'testdoctor':
            user.password = make_password(doctor_password)
            print(f"Set doctor password for {user.username}")
        elif user.username.startswith('patient'):
            user.password = make_password(patient_password)
            print(f"Set patient password for {user.username}")
        else:
            # For other users, set a default password
            user.password = make_password('password123')
            print(f"Set default password for {user.username}")
        
        user.save()
    
    print("\nPassword setup complete!")
    print("\nYou can now log in with these credentials:")
    print("\nPatients:")
    for user in users:
        if user.username.startswith('patient'):
            print(f"  Username: {user.username} | Password: {patient_password}")
    
    print("\nDoctors:")
    for user in users:
        if user.username.startswith('doctor') or user.username == 'testdoctor':
            print(f"  Username: {user.username} | Password: {doctor_password}")
    
    print(f"\nAdmin:")
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        print(f"  Username: admin | Password: {admin_password}")

if __name__ == "__main__":
    set_user_passwords()

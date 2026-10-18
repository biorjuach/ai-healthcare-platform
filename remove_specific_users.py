#!/usr/bin/env python
"""
Script to remove specific demo users from the database.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

def remove_specific_users():
    """Remove specific demo users"""
    print("🗑️  Removing specific demo users...")
    
    # List of users to remove
    users_to_remove = [
        'demo_patient_1',
        'demo_patient_2', 
        'demo_patient_3',
        'dr.general',
        'dr.pediatrician',
        'dr.surgeon',
        'dr.cardiologist',
        'dr.neurologist',
        'dr.dermatologist',
        'dr.psychiatrist'
    ]
    
    removed_count = 0
    
    for username in users_to_remove:
        try:
            user = User.objects.get(username=username)
            user.delete()
            print(f"   ✅ Removed: {username}")
            removed_count += 1
        except User.DoesNotExist:
            print(f"   ⚠️  Not found: {username}")
    
    print(f"\n✅ Removed {removed_count} users from the database!")

if __name__ == '__main__':
    remove_specific_users()

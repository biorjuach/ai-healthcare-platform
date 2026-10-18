#!/usr/bin/env python
"""
Script to restore the original patient1, patient2, and patient3 users.
"""

import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Patient

def restore_original_patients():
    """Restore original patient1, patient2, patient3"""
    print("🔄 Restoring original patients...")
    
    # Original patients to restore
    original_patients = [
        {
            'username': 'patient1',
            'email': 'patient1@demo.com',
            'first_name': 'Alice',
            'last_name': 'Wanjiru',
            'date_of_birth': date(1990, 5, 14),
            'gender': 'Female',
            'address': '123 Main St',
            'phone_number': '0712345678',
            'emergency_contact': 'John Ochieng',
            'location': '',
            'blood_type': 'O+',
            'allergies': 'None',
            'medical_history': 'No major conditions'
        },
        {
            'username': 'patient2',
            'email': 'patient2@demo.com',
            'first_name': 'Bob',
            'last_name': 'Ochieng',
            'date_of_birth': date(1985, 8, 22),
            'gender': 'Male',
            'address': '456 Elm St',
            'phone_number': '0723456789',
            'emergency_contact': 'Samuel Mackenzie',
            'location': '',
            'blood_type': 'A+',
            'allergies': 'Penicillin',
            'medical_history': 'Asthma'
        },
        {
            'username': 'patient3',
            'email': 'patient3@demo.com',
            'first_name': 'Abdi',
            'last_name': 'Mohamed',
            'date_of_birth': date(2000, 1, 30),
            'gender': 'Female',
            'address': '789 Oak St',
            'phone_number': '0734567890',
            'emergency_contact': 'Abdi Mohamed',
            'location': '',
            'blood_type': 'B+',
            'allergies': 'Shellfish',
            'medical_history': 'Hypertension'
        }
    ]
    
    restored_count = 0
    
    # Restore original patients
    print("\n👥 Restoring original patients...")
    for patient_data in original_patients:
        try:
            # Create user
            user, created = User.objects.get_or_create(
                username=patient_data['username'],
                defaults={
                    'email': patient_data['email'],
                    'first_name': patient_data['first_name'],
                    'last_name': patient_data['last_name']
                }
            )
            
            # Create patient profile
            patient, created = Patient.objects.get_or_create(
                user=user,
                defaults={
                    'date_of_birth': patient_data['date_of_birth'],
                    'gender': patient_data['gender'],
                    'address': patient_data['address'],
                    'phone_number': patient_data['phone_number'],
                    'emergency_contact': patient_data['emergency_contact'],
                    'location': patient_data['location'],
                    'blood_type': patient_data['blood_type'],
                    'allergies': patient_data['allergies'],
                    'medical_history': patient_data['medical_history']
                }
            )
            
            if created:
                print(f"   ✅ Restored patient: {patient_data['username']}")
                restored_count += 1
            else:
                print(f"   ⚠️  Patient already exists: {patient_data['username']}")
                
        except Exception as e:
            print(f"   ❌ Error restoring patient {patient_data['username']}: {e}")
    
    print(f"\n✅ Restored {restored_count} original patients to the database!")

if __name__ == '__main__':
    restore_original_patients()

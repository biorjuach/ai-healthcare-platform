#!/usr/bin/env python
"""
Script to restore all the deleted demo users.
"""

import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Patient, Doctor

def restore_deleted_users():
    """Restore all deleted demo users"""
    print("🔄 Restoring deleted demo users...")
    
    # Demo patients to restore
    demo_patients = [
        {
            'username': 'demo_patient_1',
            'email': '',
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': date(1990, 1, 1),
            'gender': 'Other',
            'address': 'Sample Address',
            'phone_number': '+25470000001',
            'emergency_contact': 'Emergency Contact',
            'location': 'Makueni District Hospital',
            'blood_type': '',
            'allergies': '',
            'medical_history': ''
        },
        {
            'username': 'demo_patient_2',
            'email': '',
            'first_name': 'Mary',
            'last_name': 'Smith',
            'date_of_birth': date(1990, 1, 1),
            'gender': 'Other',
            'address': 'Sample Address',
            'phone_number': '+25470000002',
            'emergency_contact': 'Emergency Contact',
            'location': 'Community Health Center',
            'blood_type': '',
            'allergies': '',
            'medical_history': ''
        },
        {
            'username': 'demo_patient_3',
            'email': '',
            'first_name': 'David',
            'last_name': 'Johnson',
            'date_of_birth': date(1990, 1, 1),
            'gender': 'Other',
            'address': 'Sample Address',
            'phone_number': '+25470000003',
            'emergency_contact': 'Emergency Contact',
            'location': 'Home - GPS: -1.234, 37.567',
            'blood_type': '',
            'allergies': '',
            'medical_history': ''
        }
    ]
    
    # Demo doctors to restore
    demo_doctors = [
        {
            'username': 'dr.general',
            'email': 'dr.general@demo.com',
            'first_name': 'General',
            'last_name': 'Demo',
            'specialization': 'general',
            'license_number': 'LIC1001',
            'years_of_experience': 6,
            'hospital_affiliation': 'Makueni County Referral Hospital'
        },
        {
            'username': 'dr.pediatrician',
            'email': 'dr.pediatrician@demo.com',
            'first_name': 'Pediatrician',
            'last_name': 'Demo',
            'specialization': 'pediatrician',
            'license_number': 'LIC1002',
            'years_of_experience': 7,
            'hospital_affiliation': 'Makueni County Referral Hospital'
        },
        {
            'username': 'dr.surgeon',
            'email': 'dr.surgeon@demo.com',
            'first_name': 'Surgeon',
            'last_name': 'Demo',
            'specialization': 'surgeon',
            'license_number': 'LIC1003',
            'years_of_experience': 8,
            'hospital_affiliation': 'Makueni County Referral Hospital'
        },
        {
            'username': 'dr.cardiologist',
            'email': 'dr.cardiologist@demo.com',
            'first_name': 'Cardiologist',
            'last_name': 'Demo',
            'specialization': 'cardiologist',
            'license_number': 'LIC1004',
            'years_of_experience': 9,
            'hospital_affiliation': 'Makueni County Referral Hospital'
        },
        {
            'username': 'dr.neurologist',
            'email': 'dr.neurologist@demo.com',
            'first_name': 'Neurologist',
            'last_name': 'Demo',
            'specialization': 'neurologist',
            'license_number': 'LIC1005',
            'years_of_experience': 10,
            'hospital_affiliation': 'Makueni County Referral Hospital'
        },
        {
            'username': 'dr.dermatologist',
            'email': 'dr.dermatologist@demo.com',
            'first_name': 'Dermatologist',
            'last_name': 'Demo',
            'specialization': 'dermatologist',
            'license_number': 'LIC1006',
            'years_of_experience': 11,
            'hospital_affiliation': 'Makueni County Referral Hospital'
        },
        {
            'username': 'dr.psychiatrist',
            'email': 'dr.psychiatrist@demo.com',
            'first_name': 'Psychiatrist',
            'last_name': 'Demo',
            'specialization': 'psychiatrist',
            'license_number': 'LIC1007',
            'years_of_experience': 12,
            'hospital_affiliation': 'Makueni County Referral Hospital'
        }
    ]
    
    restored_count = 0
    
    # Restore demo patients
    print("\n👥 Restoring demo patients...")
    for patient_data in demo_patients:
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
    
    # Restore demo doctors
    print("\n🏥 Restoring demo doctors...")
    for doctor_data in demo_doctors:
        try:
            # Create user
            user, created = User.objects.get_or_create(
                username=doctor_data['username'],
                defaults={
                    'email': doctor_data['email'],
                    'first_name': doctor_data['first_name'],
                    'last_name': doctor_data['last_name']
                }
            )
            
            # Create doctor profile
            doctor, created = Doctor.objects.get_or_create(
                user=user,
                defaults={
                    'specialization': doctor_data['specialization'],
                    'license_number': doctor_data['license_number'],
                    'years_of_experience': doctor_data['years_of_experience'],
                    'hospital_affiliation': doctor_data['hospital_affiliation'],
                    'is_available': True
                }
            )
            
            if created:
                print(f"   ✅ Restored doctor: {doctor_data['username']}")
                restored_count += 1
            else:
                print(f"   ⚠️  Doctor already exists: {doctor_data['username']}")
                
        except Exception as e:
            print(f"   ❌ Error restoring doctor {doctor_data['username']}: {e}")
    
    print(f"\n✅ Restored {restored_count} users to the database!")

if __name__ == '__main__':
    restore_deleted_users()

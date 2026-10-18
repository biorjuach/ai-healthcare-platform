from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from backend.models import Patient, Doctor, TestResult
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Adds sample test data for patients'

    def handle(self, *args, **kwargs):
        # Create a test doctor if not exists
        doctor_user, created = User.objects.get_or_create(
            username='testdoctor',
            defaults={
                'email': 'doctor@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'is_staff': True
            }
        )
        if created:
            doctor_user.set_password('testpass123')
            doctor_user.save()

        doctor, _ = Doctor.objects.get_or_create(
            user=doctor_user,
            defaults={
                'specialization': 'general',
                'license_number': 'DOC123456',
                'years_of_experience': 10,
                'hospital_affiliation': 'Makueni County Referral Hospital'
            }
        )

        # Create test patients if they don't exist
        test_patients = [
            {
                'username': 'patient1',
                'email': 'patient1@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'dob': date(1985, 5, 15),
                'gender': 'Female',
                'phone': '+254712345678'
            },
            {
                'username': 'patient2',
                'email': 'patient2@example.com',
                'first_name': 'James',
                'last_name': 'Johnson',
                'dob': date(1978, 8, 22),
                'gender': 'Male',
                'phone': '+254723456789'
            },
            {
                'username': 'patient3',
                'email': 'patient3@example.com',
                'first_name': 'Mary',
                'last_name': 'Williams',
                'dob': date(1990, 3, 10),
                'gender': 'Female',
                'phone': '+254734567890'
            }
        ]

        for patient_data in test_patients:
            user, created = User.objects.get_or_create(
                username=patient_data['username'],
                defaults={
                    'email': patient_data['email'],
                    'first_name': patient_data['first_name'],
                    'last_name': patient_data['last_name']
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()

            patient, _ = Patient.objects.get_or_create(
                user=user,
                defaults={
                    'date_of_birth': patient_data['dob'],
                    'gender': patient_data['gender'],
                    'address': '123 Main St, Nairobi',
                    'phone_number': patient_data['phone'],
                    'emergency_contact': '+254734567890'
                }
            )

            # Add test results for each patient
            test_types = [
                {
                    'name': 'Blood Pressure',
                    'reference_range': {'systolic': '90-120', 'diastolic': '60-80'},
                    'possible_results': [
                        {'result': '120/80', 'is_abnormal': False},
                        {'result': '140/90', 'is_abnormal': True},
                        {'result': '110/70', 'is_abnormal': False}
                    ]
                },
                {
                    'name': 'Blood Glucose',
                    'reference_range': {'fasting': '70-100', 'postprandial': '70-140'},
                    'possible_results': [
                        {'result': '95 mg/dL', 'is_abnormal': False},
                        {'result': '150 mg/dL', 'is_abnormal': True},
                        {'result': '85 mg/dL', 'is_abnormal': False}
                    ]
                },
                {
                    'name': 'Complete Blood Count',
                    'reference_range': {
                        'hemoglobin': '12-15.5',
                        'white_blood_cells': '4.5-11.0',
                        'platelets': '150-450'
                    },
                    'possible_results': [
                        {'result': 'Normal', 'is_abnormal': False},
                        {'result': 'Low hemoglobin', 'is_abnormal': True},
                        {'result': 'Elevated WBC', 'is_abnormal': True}
                    ]
                },
                {
                    'name': 'Cholesterol Panel',
                    'reference_range': {
                        'total': '<200',
                        'hdl': '>40',
                        'ldl': '<100',
                        'triglycerides': '<150'
                    },
                    'possible_results': [
                        {'result': 'Normal', 'is_abnormal': False},
                        {'result': 'High LDL', 'is_abnormal': True},
                        {'result': 'Low HDL', 'is_abnormal': True}
                    ]
                }
            ]

            # Create 3-5 test results for each patient
            for _ in range(random.randint(3, 5)):
                test_type = random.choice(test_types)
                result_data = random.choice(test_type['possible_results'])
                
                TestResult.objects.create(
                    patient=patient,
                    doctor=doctor,
                    test_name=test_type['name'],
                    result=result_data['result'],
                    test_date=date.today() - timedelta(days=random.randint(1, 30)),
                    reference_range=test_type['reference_range'],
                    is_abnormal=result_data['is_abnormal'],
                    requires_follow_up=result_data['is_abnormal'],
                    notes='Regular checkup' if not result_data['is_abnormal'] else 'Follow-up recommended'
                )

        self.stdout.write(self.style.SUCCESS('Successfully added test data')) 
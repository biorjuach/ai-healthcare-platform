from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from backend.models import Doctor, Patient, UserProfile
from datetime import date

class Command(BaseCommand):
    help = 'Populate the database with demo doctors and patients.'

    def handle(self, *args, **options):
        # Doctor specializations
        specializations = [
            ('general', 'General Practitioner'),
            ('pediatrician', 'Pediatrician'),
            ('surgeon', 'Surgeon'),
            ('cardiologist', 'Cardiologist'),
            ('neurologist', 'Neurologist'),
            ('dermatologist', 'Dermatologist'),
            ('psychiatrist', 'Psychiatrist'),
        ]
        for idx, (spec_key, spec_name) in enumerate(specializations, start=1):
            username = f'dr.{spec_key}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@demo.com',
                    'password': 'doctor123',
                    'first_name': spec_name.split()[0],
                    'last_name': 'Demo'
                }
            )
            if not created:
                user.email = f'{username}@demo.com'
                user.first_name = spec_name.split()[0]
                user.last_name = 'Demo'
                user.save()
            
            doctor, created = Doctor.objects.get_or_create(
                user=user,
                defaults={
                    'specialization': spec_key,
                    'license_number': f'LIC{1000+idx}',
                    'years_of_experience': 5+idx,
                    'hospital_affiliation': 'Makueni County Referral Hospital',
                    'is_available': True
                }
            )
            if not created:
                doctor.specialization = spec_key
                doctor.license_number = f'LIC{1000+idx}'
                doctor.years_of_experience = 5+idx
                doctor.save()
            
            self.stdout.write(self.style.SUCCESS(f'Updated doctor: {username}'))

        # Demo patients
        patients = [
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
            },
        ]
        for pdata in patients:
            user, created = User.objects.get_or_create(
                username=pdata['username'],
                defaults={
                    'email': pdata['email'],
                    'password': 'patient123',
                    'first_name': pdata['first_name'],
                    'last_name': pdata['last_name']
                }
            )
            if not created:
                user.email = pdata['email']
                user.first_name = pdata['first_name']
                user.last_name = pdata['last_name']
                user.save()
            
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    ''
                }
            )
            if not created:
                profile.save()
            
            patient, created = Patient.objects.get_or_create(
                user=user,
                defaults={
                    'date_of_birth': pdata['date_of_birth'],
                    'gender': pdata['gender'],
                    'address': pdata['address'],
                    'phone_number': pdata['phone_number'],
                    'emergency_contact': pdata['emergency_contact']
                }
            )
            if not created:
                patient.date_of_birth = pdata['date_of_birth']
                patient.gender = pdata['gender']
                patient.address = pdata['address']
                patient.phone_number = pdata['phone_number']
                patient.emergency_contact = pdata['emergency_contact']
                patient.save()
            
            self.stdout.write(self.style.SUCCESS(f'Updated patient: {pdata["username"]}')) 
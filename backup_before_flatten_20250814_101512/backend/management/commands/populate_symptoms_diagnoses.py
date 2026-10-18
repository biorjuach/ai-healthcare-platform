from django.core.management.base import BaseCommand
from backend.models import Symptom, Diagnosis, Patient, Doctor
from django.contrib.auth.models import User
import itertools

class Command(BaseCommand):
    help = 'Populates the database with example symptoms and diagnoses.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('Attempting to retrieve patients and doctors for linking...'))

        patients = list(Patient.objects.all())
        if not patients:
            self.stdout.write(self.style.WARNING("No existing patients found. Creating a default patient for the first user."))
            user = User.objects.first()
            if user:
                patients = [Patient.objects.create(user=user, date_of_birth='2000-01-01', gender='Male', address='123 Main St', phone_number='1234567890', emergency_contact='John Doe')]
            else:
                self.stdout.write(self.style.ERROR("No users or patients found. Please run 'python manage.py createsuperuser' or 'python manage.py populate_demo_users' first."))
                return

        doctors = list(Doctor.objects.all())
        if not doctors:
            self.stdout.write(self.style.ERROR("No doctors found. Please run 'python manage.py populate_demo_users' to create demo doctors."))
            return

        doctor_cycle = itertools.cycle(doctors)

        base_symptoms = [
            {'description': 'Fever', 'severity': 'medium', 'input_method': 'app', 'body_location': 'General', 'duration': '2 days'},
            {'description': 'Cough', 'severity': 'low', 'input_method': 'app', 'body_location': 'Chest', 'duration': '1 week'},
            {'description': 'Headache', 'severity': 'high', 'input_method': 'app', 'body_location': 'Head', 'duration': '1 day'},
            {'description': 'Fatigue', 'severity': 'medium', 'input_method': 'app', 'duration': '3 days'},
            {'description': 'Sore Throat', 'severity': 'low', 'input_method': 'app', 'body_location': 'Throat', 'duration': '4 days'},
        ]

        base_diagnoses = [
            {'preliminary_diagnosis': 'Common Cold', 'description': 'A viral infectious disease of the upper respiratory tract.'},
            {'preliminary_diagnosis': 'Influenza', 'description': 'A common viral infection that can be deadly, especially in high-risk groups.'},
            {'preliminary_diagnosis': 'Bronchitis', 'description': 'Inflammation of the lining of your bronchial tubes.'},
            {'preliminary_diagnosis': 'Migraine', 'description': 'A headache of varying intensity, often accompanied by nausea and sensitivity to light and sound.'},
            {'preliminary_diagnosis': 'Gastroenteritis', 'description': 'An inflammation of the stomach and intestines, typically due to viral or bacterial infection.'},
        ]

        self.stdout.write(self.style.HTTP_INFO('Populating symptoms and diagnoses for each patient...'))

        for patient in patients:
            self.stdout.write(self.style.HTTP_INFO(f'-- Processing patient: {patient.user.username} --'))

            # Create a few unique symptoms for this patient
            for i, symptom_base in enumerate(base_symptoms):
                symptom_description = f"{symptom_base['description']} (for {patient.user.username})"
                symptom, created = Symptom.objects.get_or_create(
                    patient=patient,
                    description=symptom_description,
                    defaults={
                        'severity': symptom_base['severity'],
                        'input_method': symptom_base['input_method'],
                        'body_location': symptom_base.get('body_location', ''),
                        'duration': symptom_base.get('duration', ''),
                        'frequency': symptom_base.get('frequency', ''),
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  Created symptom: {symptom.description}'))
                else:
                    self.stdout.write(self.style.NOTICE(f'  Symptom already exists: {symptom.description}'))

                # Create a diagnosis for this symptom, assigned to a rotating doctor
                if i < len(base_diagnoses):
                    diagnosis_base = base_diagnoses[i]
                    diagnosis_prelim_diagnosis = f"{diagnosis_base['preliminary_diagnosis']} (for {patient.user.username})"
                    current_doctor = next(doctor_cycle)

                    diagnosis, created = Diagnosis.objects.get_or_create(
                        symptom=symptom,
                        preliminary_diagnosis=diagnosis_prelim_diagnosis,
                        defaults={
                            'doctor': current_doctor,
                            'confidence_score': 0.8,
                            'is_ai_generated': False,
                            'notes': diagnosis_base['description']
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'  Created diagnosis: {diagnosis.preliminary_diagnosis} by Dr. {diagnosis.doctor.user.username}'))
                    else:
                        self.stdout.write(self.style.NOTICE(f'  Diagnosis already exists: {diagnosis.preliminary_diagnosis}'))

        self.stdout.write(self.style.SUCCESS('\nFinished populating example symptoms and diagnoses for all patients.')) 
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
import json
import os
from datetime import datetime, timedelta
import random

from backend.models import Patient, Symptom, Diagnosis, Doctor


class Command(BaseCommand):
    help = 'Load enhanced dataset into the database for ML training'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dataset-file',
            type=str,
            default='enhanced_training_data.json',
            help='Path to the enhanced dataset JSON file'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing symptom and diagnosis data before loading'
        )
        parser.add_argument(
            '--create-patients',
            action='store_true',
            help='Create patient profiles for synthetic data'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process in each batch'
        )

    def handle(self, *args, **options):
        dataset_file = options['dataset_file']
        
        if not os.path.exists(dataset_file):
            self.stdout.write(
                self.style.ERROR(f'Dataset file not found: {dataset_file}')
            )
            return

        self.stdout.write('Loading enhanced dataset...')

        try:
            with open(dataset_file, 'r') as f:
                dataset = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Invalid JSON file: {e}')
            )
            return

        # Display dataset metadata
        if 'metadata' in dataset:
            metadata = dataset['metadata']
            self.stdout.write('\n📊 Dataset Information:')
            self.stdout.write(f'   Total Samples: {metadata.get("total_samples", "Unknown")}')
            self.stdout.write(f'   Quality Score: {metadata.get("quality_score", "Unknown")}')
            self.stdout.write(f'   Diseases Covered: {len(metadata.get("diseases_covered", []))}')
            self.stdout.write(f'   Created: {metadata.get("created_at", "Unknown")}')

        # Clear existing data if requested
        if options['clear_existing']:
            self.stdout.write('🗑️ Clearing existing symptom and diagnosis data...')
            with transaction.atomic():
                Diagnosis.objects.filter(is_ai_generated=True).delete()
                Symptom.objects.filter(input_method='enhanced_dataset').delete()
            self.stdout.write('✅ Existing data cleared')

        # Load the training data
        training_data = dataset.get('training_data', dataset.get('fixtures', []))
        
        if not training_data:
            self.stdout.write(
                self.style.ERROR('No training data found in dataset')
            )
            return

        self.stdout.write(f'📥 Loading {len(training_data)} records...')

        # Process data in batches
        batch_size = options['batch_size']
        total_batches = (len(training_data) + batch_size - 1) // batch_size
        
        patients_created = 0
        symptoms_created = 0
        diagnoses_created = 0

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(training_data))
            batch_data = training_data[start_idx:end_idx]
            
            self.stdout.write(f'Processing batch {batch_num + 1}/{total_batches}...')
            
            with transaction.atomic():
                batch_patients, batch_symptoms, batch_diagnoses = self._process_batch(
                    batch_data, options['create_patients']
                )
                patients_created += batch_patients
                symptoms_created += batch_symptoms
                diagnoses_created += batch_diagnoses

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Dataset loaded successfully!\n'
                f'   Patients created: {patients_created}\n'
                f'   Symptoms created: {symptoms_created}\n'
                f'   Diagnoses created: {diagnoses_created}'
            )
        )

        # Suggest next steps
        self.stdout.write('\n🚀 Next Steps:')
        self.stdout.write('1. Retrain your ML model:')
        self.stdout.write('   python manage.py train_symptom_model --force-retrain --min-samples 100')
        self.stdout.write('2. Update disease mappings:')
        self.stdout.write('   python manage.py update_disease_mappings --data-days 365')
        self.stdout.write('3. Evaluate the new model:')
        self.stdout.write('   python manage.py evaluate_models --compare-baseline')

    def _process_batch(self, batch_data, create_patients=False):
        """Process a batch of records"""
        
        patients_created = 0
        symptoms_created = 0
        diagnoses_created = 0

        for record in batch_data:
            try:
                # Handle different data formats
                if 'fields' in record:
                    # Django fixture format
                    fields = record['fields']
                    symptom_text = fields.get('description', '')
                    primary_diagnosis = fields.get('primary_diagnosis', 'general_consultation')
                    severity = fields.get('severity', 'medium')
                    confidence = fields.get('confidence_score', 0.8)
                    patient_age = fields.get('patient_age')
                    patient_gender = fields.get('patient_gender', 'unknown')
                    is_emergency = fields.get('is_emergency', False)
                    created_at = fields.get('created_at')
                else:
                    # Raw enhanced dataset format
                    if 'symptoms_english' in record:
                        symptom_text = ', '.join(record['symptoms_english'])
                    else:
                        symptom_text = record.get('description', '')
                    
                    primary_diagnosis = record.get('primary_diagnosis', 'general_consultation')
                    severity = record.get('severity', 'medium')
                    confidence = record.get('confidence_score', 0.8)
                    is_emergency = record.get('is_emergency', False)
                    created_at = record.get('created_at')
                    
                    # Patient demographics
                    demographics = record.get('patient_demographics', {})
                    patient_age = demographics.get('age')
                    patient_gender = demographics.get('gender', 'unknown')

                # Create or get patient
                patient = self._get_or_create_patient(
                    patient_age, patient_gender, create_patients
                )
                if patient and create_patients:
                    patients_created += 1

                # Parse created_at
                if created_at:
                    try:
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if created_at.tzinfo is None:
                            created_at = timezone.make_aware(created_at)
                    except (ValueError, TypeError):
                        created_at = timezone.now()
                else:
                    created_at = timezone.now()

                # Create symptom record
                symptom = Symptom.objects.create(
                    patient=patient,
                    description=symptom_text,
                    severity=severity,
                    input_method='app',  # Use valid choice from model
                    created_at=created_at
                )
                symptoms_created += 1

                # Create diagnosis record
                diagnosis = Diagnosis.objects.create(
                    symptom=symptom,
                    preliminary_diagnosis=primary_diagnosis,
                    confidence_score=confidence,
                    is_ai_generated=False,  # Mark as human-confirmed for training
                    created_at=created_at,
                    notes=f'Enhanced dataset - Quality score: {confidence:.2f}'
                )
                diagnoses_created += 1

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error processing record: {e}')
                )
                continue

        return patients_created, symptoms_created, diagnoses_created

    def _get_or_create_patient(self, age, gender, create_patients):
        """Get or create a patient for the symptom record"""
        
        # Always use existing patient to avoid transaction issues with large datasets
        try:
            return Patient.objects.first()
        except:
            # Create a simple default patient if none exists
            return self._create_default_patient()

    def _create_default_patient(self):
        """Create a default test patient"""
        
        try:
            # Try to get existing default patient first
            try:
                default_user = User.objects.get(username='dataset_default')
                return Patient.objects.get(user=default_user)
            except (User.DoesNotExist, Patient.DoesNotExist):
                pass
            
            # Create simple default user and patient
            default_user = User.objects.create_user(
                username='dataset_default',
                email='default@test.com',
                password='password123',
                first_name='Default',
                last_name='Patient'
            )
            
            patient = Patient.objects.create(
                user=default_user,
                date_of_birth=timezone.now().date() - timedelta(days=30*365),
                gender='other',
                phone_number='+254700000000',
                address='Default Location',
                emergency_contact='N/A',
                medical_history='Default patient for dataset'
            )
            
            return patient
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating default patient: {e}')
            )
            return None

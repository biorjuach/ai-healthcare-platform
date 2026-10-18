from django.core.management.base import BaseCommand
from django.db import transaction
from backend.models import Symptom, Diagnosis
import re

class Command(BaseCommand):
    help = 'Remove old symptoms and diagnoses created before CSV import, keeping the enhanced dataset'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion (required for actual deletion)'
        )
        parser.add_argument(
            '--pattern',
            type=str,
            default='for_username',
            choices=['for_username', 'demo_patients', 'before_date', 'by_patient'],
            help='Pattern to identify old data: for_username (default), demo_patients, before_date, by_patient'
        )
        parser.add_argument(
            '--before-date',
            type=str,
            help='Delete records created before this date (YYYY-MM-DD format)'
        )
        parser.add_argument(
            '--patient-usernames',
            type=str,
            nargs='+',
            help='Delete records for specific patient usernames'
        )

    def handle(self, *args, **options):
        self.stdout.write('🔍 Analyzing data to identify old records...\n')
        
        pattern = options['pattern']
        
        # Identify old data based on selected pattern
        if pattern == 'for_username':
            # Find symptoms/diagnoses with "(for username)" pattern
            old_symptoms = Symptom.objects.filter(
                description__regex=r'.+\s\(for\s.+\)$'
            )
            old_diagnoses = Diagnosis.objects.filter(
                preliminary_diagnosis__regex=r'.+\s\(for\s.+\)$'
            )
            description = "data with '(for username)' pattern"
            
        elif pattern == 'demo_patients':
            # Find data for demo patients (usernames containing 'demo', 'test', etc.)
            old_symptoms = Symptom.objects.filter(
                patient__user__username__iregex=r'(demo|test|sample|default)'
            )
            old_diagnoses = Diagnosis.objects.filter(
                symptom__patient__user__username__iregex=r'(demo|test|sample|default)'
            )
            description = "data for demo/test patients"
            
        elif pattern == 'before_date':
            if not options['before_date']:
                self.stdout.write(
                    self.style.ERROR('--before-date is required when using before_date pattern')
                )
                return
            
            try:
                from datetime import datetime
                cutoff_date = datetime.strptime(options['before_date'], '%Y-%m-%d')
                old_symptoms = Symptom.objects.filter(created_at__lt=cutoff_date)
                old_diagnoses = Diagnosis.objects.filter(created_at__lt=cutoff_date)
                description = f"data created before {options['before_date']}"
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Invalid date format. Use YYYY-MM-DD')
                )
                return
                
        elif pattern == 'by_patient':
            if not options['patient_usernames']:
                self.stdout.write(
                    self.style.ERROR('--patient-usernames is required when using by_patient pattern')
                )
                return
            
            usernames = options['patient_usernames']
            old_symptoms = Symptom.objects.filter(
                patient__user__username__in=usernames
            )
            old_diagnoses = Diagnosis.objects.filter(
                symptom__patient__user__username__in=usernames
            )
            description = f"data for patients: {', '.join(usernames)}"
        
        # Also find diagnoses linked to old symptoms
        diagnoses_of_old_symptoms = Diagnosis.objects.filter(
            symptom__in=old_symptoms
        )
        
        # Combine all old diagnoses (get IDs to avoid distinct() issue)
        old_diagnosis_ids = set(old_diagnoses.values_list('id', flat=True))
        old_diagnosis_ids.update(diagnoses_of_old_symptoms.values_list('id', flat=True))
        all_old_diagnoses = Diagnosis.objects.filter(id__in=old_diagnosis_ids)
        
        self.stdout.write(f'📊 Summary of {description}:')
        self.stdout.write(f'   Old symptoms: {old_symptoms.count()}')
        self.stdout.write(f'   Old diagnoses: {all_old_diagnoses.count()}')
        
        if old_symptoms.exists():
            self.stdout.write('\n📋 Examples of old symptoms to be removed:')
            for symptom in old_symptoms[:5]:
                self.stdout.write(f'   - {symptom.description} (ID: {symptom.id})')
            if old_symptoms.count() > 5:
                self.stdout.write(f'   ... and {old_symptoms.count() - 5} more')
        
        if all_old_diagnoses.exists():
            self.stdout.write('\n🏥 Examples of old diagnoses to be removed:')
            for diagnosis in all_old_diagnoses[:5]:
                self.stdout.write(f'   - {diagnosis.preliminary_diagnosis} (ID: {diagnosis.id})')
            if all_old_diagnoses.count() > 5:
                self.stdout.write(f'   ... and {all_old_diagnoses.count() - 5} more')
        
        # Show what will be kept
        remaining_symptoms = Symptom.objects.exclude(id__in=old_symptoms)
        remaining_diagnoses = Diagnosis.objects.exclude(id__in=all_old_diagnoses)
        
        self.stdout.write('\n✅ Data that will be preserved:')
        self.stdout.write(f'   Symptoms from CSV/enhanced dataset: {remaining_symptoms.count()}')
        self.stdout.write(f'   Diagnoses from CSV/enhanced dataset: {remaining_diagnoses.count()}')
        
        if remaining_symptoms.exists():
            self.stdout.write('\n📋 Examples of symptoms that will be kept:')
            for symptom in remaining_symptoms[:3]:
                self.stdout.write(f'   - {symptom.description[:60]}{"..." if len(symptom.description) > 60 else ""} (ID: {symptom.id})')
        
        # Safety check
        if not remaining_symptoms.exists() and not remaining_diagnoses.exists():
            self.stdout.write(
                self.style.WARNING('\n⚠️  WARNING: This would delete ALL symptoms and diagnoses!')
            )
            self.stdout.write('This suggests that either:')
            self.stdout.write('1. No CSV data has been imported yet')
            self.stdout.write('2. The CSV data has a similar naming pattern')
            self.stdout.write('\nPlease verify your data before proceeding.')
            return
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('\n🔍 DRY RUN MODE: No data will be deleted.')
            )
            self.stdout.write('To actually delete the data, run:')
            self.stdout.write('python manage.py clean_old_data --confirm')
            return
        
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING('\n⚠️  Please add --confirm flag to actually delete the data.')
            )
            self.stdout.write('Example: python manage.py clean_old_data --confirm')
            self.stdout.write('Or run with --dry-run to see what would be deleted first.')
            return
        
        # Perform deletion
        self.stdout.write('\n🗑️  Deleting old data...')
        
        try:
            with transaction.atomic():
                # Delete diagnoses first (they reference symptoms)
                diagnoses_deleted, _ = all_old_diagnoses.delete()
                symptoms_deleted, _ = old_symptoms.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n🎉 Successfully cleaned old data!\n'
                        f'   Deleted {symptoms_deleted} symptoms\n'
                        f'   Deleted {diagnoses_deleted} diagnoses\n'
                        f'   Preserved {remaining_symptoms.count()} symptoms from CSV data\n'
                        f'   Preserved {remaining_diagnoses.count()} diagnoses from CSV data'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Error during deletion: {e}')
            )
            self.stdout.write('No data was deleted due to the error.')
            return
        
        self.stdout.write('\n✨ Database cleanup completed successfully!')
        self.stdout.write('Your CSV-imported data has been preserved.')

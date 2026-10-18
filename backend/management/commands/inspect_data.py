from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from backend.models import Symptom, Diagnosis
from collections import Counter
import re

class Command(BaseCommand):
    help = 'Inspect symptoms and diagnoses data to identify patterns'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Inspecting symptoms and diagnoses data...\n')
        
        # Count total records
        total_symptoms = Symptom.objects.count()
        total_diagnoses = Diagnosis.objects.count()
        
        self.stdout.write(f'📊 Total Records:')
        self.stdout.write(f'   Symptoms: {total_symptoms}')
        self.stdout.write(f'   Diagnoses: {total_diagnoses}')
        
        if total_symptoms == 0:
            self.stdout.write(self.style.WARNING('No symptoms found in database.'))
            return
        
        # Analyze symptom patterns
        self.stdout.write('\n🔬 Symptom Pattern Analysis:')
        
        # Find symptoms with "(for username)" pattern
        old_pattern_symptoms = Symptom.objects.filter(
            description__regex=r'.+\s\(for\s.+\)$'
        )
        self.stdout.write(f'   Symptoms with "(for username)" pattern: {old_pattern_symptoms.count()}')
        
        # Show examples of different symptom types
        self.stdout.write('\n📋 Sample Symptoms:')
        for i, symptom in enumerate(Symptom.objects.all()[:10]):
            pattern = "OLD" if re.search(r'.+\s\(for\s.+\)$', symptom.description) else "NEW"
            self.stdout.write(f'   [{pattern}] {symptom.description[:80]}{"..." if len(symptom.description) > 80 else ""}')
        
        # Analyze input methods
        input_methods = Symptom.objects.values('input_method').annotate(count=Count('input_method'))
        self.stdout.write('\n📱 Input Methods:')
        for method in input_methods:
            self.stdout.write(f'   {method["input_method"]}: {method["count"]}')
        
        # Analyze severities
        severities = Symptom.objects.values('severity').annotate(count=Count('severity'))
        self.stdout.write('\n🚨 Severity Distribution:')
        for severity in severities:
            self.stdout.write(f'   {severity["severity"]}: {severity["count"]}')
        
        # Analyze diagnosis patterns
        self.stdout.write('\n🏥 Diagnosis Pattern Analysis:')
        
        old_pattern_diagnoses = Diagnosis.objects.filter(
            preliminary_diagnosis__regex=r'.+\s\(for\s.+\)$'
        )
        self.stdout.write(f'   Diagnoses with "(for username)" pattern: {old_pattern_diagnoses.count()}')
        
        # AI vs Human generated
        ai_generated = Diagnosis.objects.filter(is_ai_generated=True).count()
        human_generated = Diagnosis.objects.filter(is_ai_generated=False).count()
        self.stdout.write(f'   AI Generated: {ai_generated}')
        self.stdout.write(f'   Human Generated: {human_generated}')
        
        # Show sample diagnoses
        self.stdout.write('\n🩺 Sample Diagnoses:')
        for i, diagnosis in enumerate(Diagnosis.objects.all()[:10]):
            pattern = "OLD" if re.search(r'.+\s\(for\s.+\)$', diagnosis.preliminary_diagnosis) else "NEW"
            ai_flag = "AI" if diagnosis.is_ai_generated else "Human"
            self.stdout.write(f'   [{pattern}|{ai_flag}] {diagnosis.preliminary_diagnosis[:60]}{"..." if len(diagnosis.preliminary_diagnosis) > 60 else ""}')
        
        # Patient analysis
        patients_with_symptoms = Symptom.objects.values('patient__user__username').annotate(
            symptom_count=Count('id')
        ).order_by('-symptom_count')
        
        self.stdout.write('\n👥 Patients with Most Symptoms:')
        for patient in patients_with_symptoms[:5]:
            username = patient['patient__user__username'] or 'Unknown'
            count = patient['symptom_count']
            self.stdout.write(f'   {username}: {count} symptoms')
        
        # Recommendations
        self.stdout.write('\n💡 Recommendations:')
        
        if old_pattern_symptoms.exists() or old_pattern_diagnoses.exists():
            self.stdout.write('   1. Found old data with "(for username)" pattern')
            self.stdout.write('   2. Run: python manage.py clean_old_data --dry-run')
            self.stdout.write('   3. Then: python manage.py clean_old_data --confirm')
        else:
            self.stdout.write('   1. No obvious old data pattern found')
            self.stdout.write('   2. You may need to identify old data by other criteria')
            self.stdout.write('   3. Consider creation dates or specific patient usernames')
        
        # Timeline analysis if possible
        if Symptom.objects.exists():
            earliest_symptom = Symptom.objects.earliest('created_at')
            latest_symptom = Symptom.objects.latest('created_at')
            self.stdout.write(f'\n📅 Data Timeline:')
            self.stdout.write(f'   Earliest symptom: {earliest_symptom.created_at}')
            self.stdout.write(f'   Latest symptom: {latest_symptom.created_at}')
        
        self.stdout.write('\n✅ Inspection complete!')

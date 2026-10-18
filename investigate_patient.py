#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models import Patient, Symptom
from django.contrib.auth.models import User

print("🔍 Investigating patient with 1013 symptoms...\n")

# Get patient3
try:
    patient3 = Patient.objects.get(user__username='patient3')
    
    print("👤 Patient3 Details:")
    print(f"   Name: {patient3.user.first_name} {patient3.user.last_name}")
    print(f"   Username: {patient3.user.username}")
    print(f"   Email: {patient3.user.email}")
    print(f"   Phone: {patient3.phone_number}")
    print(f"   Location: {patient3.location}")
    print(f"   Created: {patient3.user.date_joined}")
    
    symptoms = patient3.symptom_set.all()
    print(f"\n📊 Symptoms Analysis:")
    print(f"   Total symptoms: {symptoms.count()}")
    
    # Check creation dates
    first_symptom = symptoms.earliest('created_at')
    last_symptom = symptoms.latest('created_at')
    print(f"   First symptom: {first_symptom.created_at}")
    print(f"   Last symptom: {last_symptom.created_at}")
    
    # Show sample symptoms
    print(f"\n📋 Sample Symptoms:")
    for i, symptom in enumerate(symptoms[:10]):
        print(f"   {i+1}. {symptom.description[:80]}{'...' if len(symptom.description) > 80 else ''}")
        print(f"      Severity: {symptom.severity}, Created: {symptom.created_at.date()}")
    
    if symptoms.count() > 10:
        print(f"   ... and {symptoms.count() - 10} more")
    
    # Check input methods
    print(f"\n📱 Input Methods:")
    methods = symptoms.values('input_method').distinct()
    for method in methods:
        count = symptoms.filter(input_method=method['input_method']).count()
        print(f"   {method['input_method']}: {count}")
    
    # Check severities
    print(f"\n🚨 Severity Distribution:")
    severities = symptoms.values('severity').distinct()
    for severity in severities:
        count = symptoms.filter(severity=severity['severity']).count()
        print(f"   {severity['severity']}: {count}")
        
except Patient.DoesNotExist:
    print("❌ Patient3 not found")

# Check all patients for comparison
print(f"\n👥 All Patients Comparison:")
all_patients = Patient.objects.all()
for patient in all_patients:
    symptom_count = patient.symptom_set.count()
    print(f"   {patient.user.username}: {symptom_count} symptoms")

print(f"\n💡 Analysis:")
print("This high number suggests that when you imported your CSV data,")
print("most/all records were assigned to patient3 instead of being")
print("distributed across multiple patients or creating new patient profiles.")

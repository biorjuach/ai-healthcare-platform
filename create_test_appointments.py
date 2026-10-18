#!/usr/bin/env python3
"""
Script to create test appointments for the doctor dashboard
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Doctor, Patient, Appointment
from django.utils import timezone

def create_test_appointments():
    """Create test appointments for the next few days"""
    print("🏥 Creating test appointments...")
    
    # Get a doctor (Abdalla Kassim)
    try:
        doctor = Doctor.objects.get(user__username='doctor1')
        print(f"Using doctor: {doctor.user.first_name} {doctor.user.last_name}")
    except Doctor.DoesNotExist:
        print("❌ Doctor 'doctor1' not found")
        return
    
    # Get patients
    patients = Patient.objects.all()[:3]
    if not patients:
        print("❌ No patients found")
        return
    
    print(f"Found {len(patients)} patients")
    
    # Create appointments for the next few days
    today = timezone.now().date()
    appointment_times = [
        (today + timedelta(days=1), "09:00"),  # Tomorrow
        (today + timedelta(days=1), "14:30"),  # Tomorrow afternoon
        (today + timedelta(days=2), "10:15"),  # Day after tomorrow
        (today + timedelta(days=3), "16:00"),  # 3 days from now
        (today + timedelta(days=5), "11:30"),  # 5 days from now
    ]
    
    created_count = 0
    for i, (date, time) in enumerate(appointment_times):
        if i < len(patients):
            patient = patients[i]
            
            # Create appointment datetime
            appointment_datetime = datetime.combine(date, datetime.strptime(time, "%H:%M").time())
            appointment_datetime = timezone.make_aware(appointment_datetime)
            
            # Create appointment
            appointment, created = Appointment.objects.get_or_create(
                doctor=doctor,
                patient=patient,
                appointment_date=appointment_datetime,
                defaults={
                    'status': 'scheduled',
                    'reason': f'Follow-up consultation for {patient.user.first_name}',
                    'notes': f'Regular checkup appointment scheduled for {date.strftime("%B %d, %Y")}'
                }
            )
            
            if created:
                print(f"✅ Created appointment: {patient.user.first_name} {patient.user.last_name}")
                print(f"   Date: {appointment_datetime.strftime('%Y-%m-%d %H:%M')}")
                print(f"   Status: {appointment.status}")
                created_count += 1
            else:
                print(f"⚠️  Appointment already exists for {patient.user.first_name} on {date}")
    
    print(f"\n🎉 Created {created_count} new appointments!")
    
    # Show summary
    upcoming = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__gte=today,
        status='scheduled'
    ).order_by('appointment_date')
    
    print(f"\n📅 Doctor {doctor.user.first_name} now has {upcoming.count()} upcoming appointments:")
    for appt in upcoming:
        print(f"  - {appt.patient.user.first_name} {appt.patient.user.last_name}")
        print(f"    Date: {appt.appointment_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"    Status: {appt.status}")

if __name__ == "__main__":
    print("🏥 Test Appointment Creator")
    print("=" * 40)
    create_test_appointments()
    print("\n✅ Done!")

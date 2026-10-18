from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    emergency_contact = models.CharField(max_length=100)
    medical_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=200, blank=True)  # For emergency alerts
    emergency_contacts = models.JSONField(default=list)  # List of emergency contacts
    blood_type = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True)
    insurance_info = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - Patient"

class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('general', 'General Practitioner'),
        ('pediatrician', 'Pediatrician'),
        ('surgeon', 'Surgeon'),
        ('cardiologist', 'Cardiologist'),
        ('neurologist', 'Neurologist'),
        ('dermatologist', 'Dermatologist'),
        ('psychiatrist', 'Psychiatrist'),
        ('other', 'Other')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES)
    license_number = models.CharField(max_length=50)
    years_of_experience = models.IntegerField()
    hospital_affiliation = models.CharField(max_length=200, default='Makueni County Referral Hospital')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"

class Symptom(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='low')
    input_method = models.CharField(max_length=20, choices=[
        ('sms', 'SMS'),
        ('voice', 'Voice Call'),
        ('app', 'Mobile App')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    is_emergency = models.BooleanField(default=False)
    body_location = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    triggers = models.TextField(blank=True)
    associated_symptoms = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Symptom: {self.description[:50]} - {self.patient}"

class Diagnosis(models.Model):
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)
    preliminary_diagnosis = models.TextField()
    confidence_score = models.FloatField(default=0.0)
    is_ai_generated = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    recommended_tests = models.JSONField(default=list, blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Diagnosis for {self.symptom.patient} - {self.preliminary_diagnosis[:50]}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled')
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.SET_NULL, null=True, blank=True)
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    reason = models.TextField()
    notes = models.TextField(blank=True)
    is_emergency = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.IntegerField(default=30)  # Duration in minutes
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    def __str__(self):
        return f"Appointment: {self.patient} with Dr. {self.doctor} on {self.appointment_date}"

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.SET_NULL, null=True, blank=True)
    treatment = models.TextField()
    prescription = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    medications = models.JSONField(default=list, blank=True)
    allergies_noted = models.TextField(blank=True)
    vital_signs = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Medical Record: {self.patient} - {self.created_at}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('appointment', 'Appointment'),
        ('reminder', 'Reminder'),
        ('result', 'Test Result'),
        ('system', 'System'),
        ('emergency', 'Emergency Alert'),
        ('prescription', 'Prescription'),
        ('follow_up', 'Follow-up')
    ]

    DELIVERY_METHODS = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('app', 'Mobile App'),
        ('all', 'All Methods')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS, default='app')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium')
    action_required = models.BooleanField(default=False)
    action_url = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.notification_type}: {self.title}"

class TestResult(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=200)
    result = models.TextField()
    test_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reference_range = models.JSONField(default=dict, blank=True)
    is_abnormal = models.BooleanField(default=False)
    requires_follow_up = models.BooleanField(default=False)
    follow_up_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.test_name} - {self.patient} - {self.test_date}"

class EmergencyAlert(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('false_alarm', 'False Alarm'),
        ('in_progress', 'In Progress')
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    location = models.CharField(max_length=200)
    assigned_responder = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    response_time = models.IntegerField(null=True, blank=True)  # Time in minutes
    response_notes = models.TextField(blank=True)
    emergency_type = models.CharField(max_length=50, blank=True)
    severity_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], default='medium')

    def __str__(self):
        return f"Emergency Alert: {self.patient} - {self.created_at}"

class HospitalCapacity(models.Model):
    department = models.CharField(max_length=100)
    total_beds = models.IntegerField()
    occupied_beds = models.IntegerField()
    available_doctors = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    waiting_list = models.IntegerField(default=0)
    average_wait_time = models.IntegerField(default=0)  # Time in minutes
    emergency_capacity = models.IntegerField(default=0)
    is_accepting_patients = models.BooleanField(default=True)
    special_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.department} - {self.available_beds} beds available"

    @property
    def available_beds(self):
        return self.total_beds - self.occupied_beds

    @property
    def occupancy_rate(self):
        return (self.occupied_beds / self.total_beds) * 100 if self.total_beds > 0 else 0 
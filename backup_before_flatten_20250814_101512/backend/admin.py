from django.contrib import admin
from .models import Patient, Doctor, Appointment, MedicalRecord, Notification, TestResult, Symptom, Diagnosis, EmergencyAlert, HospitalCapacity

admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(MedicalRecord)
admin.site.register(Notification)
admin.site.register(TestResult)
admin.site.register(Symptom)
admin.site.register(Diagnosis)
admin.site.register(EmergencyAlert)
admin.site.register(HospitalCapacity) 
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Patient, Doctor, Appointment, MedicalRecord,
    Notification, TestResult, Symptom, Diagnosis,
    EmergencyAlert, HospitalCapacity, UserProfile
)
from django.utils import timezone

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = []

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        try:
            user = User.objects.create_user(**validated_data)
            return user
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile
        
        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update UserProfile fields
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        
        return instance

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    emergency_contacts = serializers.JSONField(required=False, default=[])
    insurance_info = serializers.JSONField(required=False)
    allergies = serializers.CharField(required=False, allow_blank=True)
    blood_type = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Patient
        fields = '__all__'

    def create(self, validated_data):
        try:
            user_data = validated_data.pop('user')
            emergency_contacts_data = validated_data.pop('emergency_contacts', [])
            if emergency_contacts_data is None:
                emergency_contacts_data = []
            user = User.objects.create_user(**user_data)
            patient = Patient.objects.create(user=user, emergency_contacts=emergency_contacts_data, **validated_data)
            return patient
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        return value

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Doctor
        fields = '__all__'

    def create(self, validated_data):
        try:
            user_data = validated_data.pop('user')
            user = User.objects.create_user(**user_data)
            doctor = Doctor.objects.create(user=user, **validated_data)
            return doctor
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_license_number(self, value):
        if Doctor.objects.filter(license_number=value).exists():
            raise serializers.ValidationError("A doctor with this license number already exists.")
        return value

class SymptomSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        write_only=True,
        source='patient'
    )
    associated_symptoms = serializers.JSONField(required=False)
    body_location = serializers.CharField(required=False, allow_blank=True)
    duration = serializers.CharField(required=False, allow_blank=True)
    frequency = serializers.CharField(required=False, allow_blank=True)
    triggers = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Symptom
        fields = '__all__'

    def validate_severity(self, value):
        if value not in dict(Symptom.SEVERITY_CHOICES):
            raise serializers.ValidationError("Invalid severity level.")
        return value

class DiagnosisSerializer(serializers.ModelSerializer):
    symptom = SymptomSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    symptom_id = serializers.PrimaryKeyRelatedField(
        queryset=Symptom.objects.all(),
        write_only=True,
        source='symptom'
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        write_only=True,
        source='doctor',
        required=False
    )
    recommended_tests = serializers.JSONField(required=False)
    follow_up_date = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Diagnosis
        fields = '__all__'

    def validate_confidence_score(self, value):
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Confidence score must be between 0 and 1.")
        return value

class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    diagnosis = DiagnosisSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        write_only=True,
        source='patient'
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        write_only=True,
        source='doctor'
    )
    diagnosis_id = serializers.PrimaryKeyRelatedField(
        queryset=Diagnosis.objects.all(),
        write_only=True,
        source='diagnosis',
        required=False
    )
    appointment_date = serializers.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S%z'],
        help_text='Format: YYYY-MM-DD HH:MM'
    )
    follow_up_date = serializers.DateTimeField(required=False, allow_null=True)
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Appointment
        fields = '__all__'

    def validate_appointment_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Appointment date cannot be in the past.")
        return value

    def validate_duration(self, value):
        if value < 15 or value > 120:
            raise serializers.ValidationError("Duration must be between 15 and 120 minutes.")
        return value

class MedicalRecordSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    diagnosis = DiagnosisSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        read_only=False,
        source='patient'
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        read_only=False,
        source='doctor'
    )
    diagnosis_id = serializers.PrimaryKeyRelatedField(
        queryset=Diagnosis.objects.all(),
        read_only=False,
        source='diagnosis',
        required=False
    )
    medications = serializers.JSONField(required=False)
    allergies_noted = serializers.CharField(required=False, allow_blank=True)
    vital_signs = serializers.JSONField(required=False)
    follow_up_date = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = MedicalRecord
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    priority = serializers.CharField(required=False)
    action_required = serializers.BooleanField(required=False)
    action_url = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Notification
        fields = '__all__'

    def validate_priority(self, value):
        if value not in ['low', 'medium', 'high', 'urgent']:
            raise serializers.ValidationError("Invalid priority level.")
        return value

class TestResultSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        write_only=True,
        source='patient'
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        write_only=True,
        source='doctor'
    )
    reference_range = serializers.JSONField(required=False)
    follow_up_notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = TestResult
        fields = '__all__'

    def validate_test_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Test date cannot be in the future.")
        return value

class EmergencyAlertSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    symptom = SymptomSerializer(read_only=True)
    assigned_responder = DoctorSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        write_only=True,
        source='patient'
    )
    symptom_id = serializers.PrimaryKeyRelatedField(
        queryset=Symptom.objects.all(),
        write_only=True,
        source='symptom'
    )
    assigned_responder_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        write_only=True,
        source='assigned_responder',
        required=False
    )
    response_notes = serializers.CharField(required=False, allow_blank=True)
    emergency_type = serializers.CharField(required=False, allow_blank=True)
    severity_level = serializers.CharField(required=False)

    class Meta:
        model = EmergencyAlert
        fields = '__all__'

    def validate_severity_level(self, value):
        if value not in ['low', 'medium', 'high', 'critical']:
            raise serializers.ValidationError("Invalid severity level.")
        return value

class HospitalCapacitySerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalCapacity
        fields = '__all__'
        read_only_fields = ('available_beds', 'occupancy_rate')

    def validate(self, data):
        if data['occupied_beds'] > data['total_beds']:
            raise serializers.ValidationError("Occupied beds cannot exceed total beds.")
        return data 
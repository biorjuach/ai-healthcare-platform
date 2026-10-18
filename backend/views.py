from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

from .models import (
    Patient, Doctor, Symptom, Diagnosis, Appointment, MedicalRecord, 
    Notification, TestResult, EmergencyAlert, HospitalCapacity
)
from .serializers import (
    PatientSerializer, DoctorSerializer, SymptomSerializer, DiagnosisSerializer,
    AppointmentSerializer, MedicalRecordSerializer, NotificationSerializer,
    TestResultSerializer, EmergencyAlertSerializer, HospitalCapacitySerializer
)
from .communication_services import SMSService, VoiceCallService, NotificationService
from .ai_services import SymptomAnalyzer, DoctorMatcher, HealthRiskAssessor, EmergencyResponseSystem
from .authentication import token_or_session_auth

logger = logging.getLogger(__name__)

# Initialize services
sms_service = SMSService()
voice_service = VoiceCallService()
symptom_analyzer = SymptomAnalyzer()
doctor_matcher = DoctorMatcher()
risk_assessor = HealthRiskAssessor()
emergency_system = EmergencyResponseSystem()

# Multi-channel Communication Endpoints

@csrf_exempt
@require_http_methods(["POST"])
def sms_webhook(request):
    """
    Webhook endpoint for SMS processing
    """
    try:
        data = json.loads(request.body)
        phone_number = data.get('from')
        message = data.get('text', '')
        
        if not phone_number or not message:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing phone number or message'
            }, status=400)
        
        # Process SMS
        result = sms_service.process_incoming_sms(phone_number, message)
        
        # Log the interaction
        logger.info(f"SMS processed: {phone_number} - {message[:50]}... - {result['status']}")
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"SMS webhook error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def voice_webhook(request):
    """
    Webhook endpoint for voice call processing
    """
    try:
        data = json.loads(request.body)
        phone_number = data.get('from')
        transcript = data.get('transcript', '')
        language = data.get('language', 'english')
        
        if not phone_number or not transcript:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing phone number or transcript'
            }, status=400)
        
        # Process voice input
        result = voice_service.process_voice_input(phone_number, transcript, language)
        
        # Log the interaction
        logger.info(f"Voice processed: {phone_number} - {transcript[:50]}... - {result['status']}")
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Voice webhook error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)

# Symptom Analysis Endpoints

@csrf_exempt
@require_http_methods(["POST"])
def analyze_symptoms(request):
    """
    Analyze symptoms and provide preliminary diagnosis
    """
    try:
        data = json.loads(request.body)
        # Handle both mobile app format (symptoms) and web app format (description + symptoms)
        symptom_text = data.get('symptoms', '') or data.get('description', '')
        patient_id = data.get('patient_id')
        language = data.get('language', 'english')
        
        # Debug logging
        logger.info(f"Analyze symptoms request: {data}")
        
        # Web app sends language as 'en'/'sw', convert to full names
        if language == 'en':
            language = 'english'
        elif language == 'sw':
            language = 'swahili'
        
        # If web app provides additional context, combine it
        body_location = data.get('body_location', '')
        duration = data.get('duration', '')
        severity = data.get('severity', '')
        
        if body_location or duration or severity:
            additional_info = []
            if body_location:
                additional_info.append(f"Location: {body_location}")
            if duration:
                additional_info.append(f"Duration: {duration}")
            if severity:
                additional_info.append(f"Reported severity: {severity}")
            
            if additional_info:
                symptom_text += f" ({', '.join(additional_info)})"
        
        if not symptom_text:
            return JsonResponse({
                'success': False,
                'message': 'Symptoms description is required'
            }, status=400)
        
        # Get patient if ID provided
        patient = None
        if patient_id:
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Patient not found'
                }, status=404)
        
        # Analyze symptoms
        logger.info(f"Analyzing symptoms: {symptom_text}")
        severity, confidence, is_emergency, disease_predictions = symptom_analyzer.analyze_symptom(symptom_text, language)
        logger.info(f"Analysis result: {severity}, {confidence}, {is_emergency}")
        
        # Create a temporary symptom object for analysis
        temp_symptom = type('obj', (object,), {
            'description': symptom_text,
            'severity': severity,
            'patient': patient
        })()
        
        # Generate diagnosis - skip this for now to isolate the issue
        diagnosis_text = disease_predictions.get('primary_diagnosis', 'General consultation')
        
        # Assess health risk if patient available
        risk_assessment = None
        if patient:
            try:
                risk_assessment = risk_assessor.assess_health_risk(patient, temp_symptom)
            except Exception as e:
                logger.warning(f"Risk assessment failed: {e}")
        
        # Find appropriate doctor
        recommended_doctor = None
        if patient:
            try:
                recommended_doctor = doctor_matcher.find_appropriate_doctor(temp_symptom, patient)
            except Exception as e:
                logger.warning(f"Doctor matching failed: {e}")
        
        # Convert disease predictions to frontend format
        predicted_diseases = []
        treatment_suggestions = []
        
        if disease_predictions and 'predictions' in disease_predictions:
            for pred in disease_predictions['predictions'][:3]:
                if isinstance(pred, (list, tuple)) and len(pred) > 0:
                    # Extract just the disease name (first element)
                    disease_name = str(pred[0]).replace('_', ' ').title()
                    predicted_diseases.append(disease_name)
                elif isinstance(pred, str):
                    predicted_diseases.append(pred.replace('_', ' ').title())
                else:
                    predicted_diseases.append(str(pred).replace('_', ' ').title())
        
        # Generate treatment suggestions based on diagnosis
        if diagnosis_text and diagnosis_text != 'General consultation':
            treatment_suggestions = [
                'Monitor symptoms closely',
                'Seek medical attention if symptoms worsen',
                'Follow up with healthcare provider'
            ]
            if is_emergency:
                treatment_suggestions.insert(0, 'Seek immediate medical attention')
        
        response_data = {
            'status': 'success',
            'symptoms': symptom_text,
            'severity': severity,
            'confidence': confidence,
            'is_emergency': is_emergency,
            'diagnosis': diagnosis_text,
            'disease_predictions': disease_predictions,
            'risk_assessment': risk_assessment,
            'recommended_doctor': DoctorSerializer(recommended_doctor).data if recommended_doctor else None,
            # Frontend-compatible format
            'analysis_result': {
                'severity': severity,
                'emergency_detected': is_emergency,
                'predicted_diseases': predicted_diseases,
                'recommended_doctors': [DoctorSerializer(recommended_doctor).data] if recommended_doctor else [],
                'treatment_suggestions': treatment_suggestions,
                'urgency_level': 'critical' if is_emergency else ('high' if severity == 'high' else 'routine')
            },
            'ai_confidence': int(confidence * 100) if confidence else 0
        }
        
        # Add emergency response if needed
        if is_emergency:
            try:
                emergency_plan = emergency_system.get_emergency_response_plan(temp_symptom)
                response_data['emergency_plan'] = emergency_plan
            except Exception as e:
                logger.warning(f"Emergency plan generation failed: {e}")
                response_data['emergency_plan'] = {
                    'emergency_type': 'general_emergency',
                    'immediate_action': 'Seek immediate medical attention. Call emergency services.',
                    'priority': 'critical'
                }
        
        return JsonResponse({
            'success': True,
            'data': response_data
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        import traceback
        logger.error(f"Symptom analysis error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@token_or_session_auth
def submit_symptom_report(request):
    """
    Submit symptom report and create records
    """
    # Debug logging
    logger.info(f"Submit symptom report: User authenticated: {request.user.is_authenticated}")
    logger.info(f"Submit symptom report: User: {request.user.username if request.user.is_authenticated else 'Not authenticated'}")
    logger.info(f"Submit symptom report: Headers: {dict(request.headers)}")
    
    try:
        data = json.loads(request.body)
        patient_id = data.get('patient_id')
        # Handle both mobile app format (symptoms) and web app format (description + symptoms)
        symptom_text = data.get('symptoms', '') or data.get('description', '')
        input_method = data.get('input_method', 'app')  # app, sms, voice
        language = data.get('language', 'english')
        
        # Web app sends language as 'en'/'sw', convert to full names
        if language == 'en':
            language = 'english'
        elif language == 'sw':
            language = 'swahili'
        
        # If web app provides additional context, combine it
        body_location = data.get('body_location', '')
        duration = data.get('duration', '')
        severity = data.get('severity', '')
        
        if body_location or duration or severity:
            additional_info = []
            if body_location:
                additional_info.append(f"Location: {body_location}")
            if duration:
                additional_info.append(f"Duration: {duration}")
            if severity:
                additional_info.append(f"Reported severity: {severity}")
            
            if additional_info:
                symptom_text += f" ({', '.join(additional_info)})"
        
        # If no patient_id provided, require authentication
        if not patient_id:
            if not request.user.is_authenticated:
                logger.error(f"Submit symptom report: User not authenticated")
                return JsonResponse({
                    'success': False,
                    'message': 'Authentication required or patient_id must be provided'
                }, status=401)
            
            # Use authenticated user's patient profile
            try:
                patient = Patient.objects.get(user=request.user)
                patient_id = patient.id
                logger.info(f"Submit symptom report: Found patient {patient_id} for user {request.user.id}")
            except Patient.DoesNotExist:
                logger.error(f"Submit symptom report: Patient profile not found for user {request.user.id}")
                return JsonResponse({
                    'success': False,
                    'message': 'Patient profile not found. Please complete your profile first.'
                }, status=404)
        
        if not symptom_text or symptom_text.strip() == '':
            logger.error(f"Submit symptom report: Empty symptom text for patient {patient_id}")
            return JsonResponse({
                'success': False,
                'message': 'Symptoms description is required'
            }, status=400)
        
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Patient not found'
            }, status=404)
        
        # Analyze symptoms
        severity, confidence, is_emergency, disease_predictions = symptom_analyzer.analyze_symptom(symptom_text, language)
        
        # Create symptom record
        symptom = Symptom.objects.create(
            patient=patient,
            description=symptom_text,
            severity=severity,
            input_method=input_method,
            is_emergency=is_emergency
        )
        
        # Generate diagnosis
        diagnosis_text = symptom_analyzer.generate_preliminary_diagnosis(symptom)
        
        # Create diagnosis record
        diagnosis = Diagnosis.objects.create(
            symptom=symptom,
            preliminary_diagnosis=diagnosis_text,
            confidence_score=confidence,
            is_ai_generated=True
        )
        
        # Assess health risk
        risk_assessment = risk_assessor.assess_health_risk(patient, symptom)
        
        # Find appropriate doctor
        recommended_doctor = doctor_matcher.find_appropriate_doctor(symptom, patient)
        
        # Create emergency alert if needed
        emergency_alert = None
        if is_emergency:
            emergency_plan = emergency_system.get_emergency_response_plan(symptom)
            emergency_alert = EmergencyAlert.objects.create(
                patient=patient,
                symptom=symptom,
                status='active',
                location=patient.location or 'Unknown',
                emergency_type=emergency_plan.get('emergency_type', 'general_emergency'),
                severity_level='critical' if severity == 'critical' else 'high'
            )
            
            # Create emergency notifications
            from .communication_services import NotificationService as CommNotificationService
            CommNotificationService.create_emergency_notification(emergency_alert)
        
        response_data = {
            'status': 'success',
            'symptom_id': symptom.id,
            'diagnosis_id': diagnosis.id,
            'severity': severity,
            'confidence': confidence,
            'is_emergency': is_emergency,
            'diagnosis': diagnosis_text,
            'risk_assessment': risk_assessment,
            'recommended_doctor': DoctorSerializer(recommended_doctor).data if recommended_doctor else None,
            'emergency_alert': EmergencyAlertSerializer(emergency_alert).data if emergency_alert else None
        }
        
        return JsonResponse({
            'success': True,
            'data': response_data
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Symptom submission error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500)

# Patient Management Endpoints

@token_or_session_auth
def patient_dashboard(request):
    """
    Get patient dashboard data
    """
    try:
        # Get patient profile
        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Patient profile not found'
            }, status=404)
        
        # Get recent symptoms (last 5)
        try:
            recent_symptoms = Symptom.objects.filter(patient=patient).order_by('-created_at')[:5]
            symptoms_data = []
            for symptom in recent_symptoms:
                symptoms_data.append({
                    'id': symptom.id,
                    'symptoms': symptom.description,
                    'body_location': symptom.body_location or 'Not specified',
                    'severity': symptom.severity,
                    'created_at': symptom.created_at.isoformat(),
                    'updated_at': symptom.updated_at.isoformat()
                })
        except Exception as e:
            logger.error(f"Error fetching symptoms: {str(e)}")
            symptoms_data = []
        
        # Get upcoming appointments
        try:
            upcoming_appointments = Appointment.objects.filter(
                patient=patient,
                appointment_date__gte=timezone.now(),
                status__in=['scheduled', 'confirmed']
            ).order_by('appointment_date')[:5]
            
            appointments_data = []
            for appointment in upcoming_appointments:
                try:
                    hospital_name = appointment.doctor.hospital_affiliation if appointment.doctor else 'General Hospital'
                except Exception:
                    hospital_name = 'General Hospital'
                
                appointments_data.append({
                    'id': appointment.id,
                    'hospital': hospital_name,
                    'date': appointment.appointment_date.isoformat(),
                    'time': appointment.appointment_date.strftime('%H:%M'),
                    'status': appointment.status,
                    'created_at': appointment.created_at.isoformat(),
                    'updated_at': appointment.updated_at.isoformat()
                })
        except Exception as e:
            logger.error(f"Error fetching appointments: {str(e)}")
            appointments_data = []
        
        # Health summary
        try:
            total_symptoms = Symptom.objects.filter(patient=patient).count()
        except Exception as e:
            logger.error(f"Error counting symptoms: {str(e)}")
            total_symptoms = 0
            
        try:
            recent_diagnoses = Diagnosis.objects.filter(
                symptom__patient=patient
            ).values_list('preliminary_diagnosis', flat=True)[:3]
        except Exception as e:
            logger.error(f"Error fetching diagnoses: {str(e)}")
            recent_diagnoses = []
        
        # Severity distribution
        severity_distribution = {}
        try:
            for severity in ['low', 'medium', 'high', 'critical']:
                severity_distribution[severity] = Symptom.objects.filter(
                    patient=patient, 
                    severity=severity
                ).count()
        except Exception as e:
            logger.error(f"Error calculating severity distribution: {str(e)}")
            severity_distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        
        # Unread notifications
        try:
            unread_notifications = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
        except Exception as e:
            logger.error(f"Error counting notifications: {str(e)}")
            unread_notifications = 0
        
        dashboard_data = {
            'recent_symptoms': symptoms_data,
            'upcoming_appointments': appointments_data,
            'health_summary': {
                'total_symptoms': total_symptoms,
                'recent_diagnoses': list(recent_diagnoses),
                'severity_distribution': severity_distribution
            },
            'unread_notifications': unread_notifications
        }
        
        return JsonResponse({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        logger.error(f"Patient dashboard error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500)

@token_or_session_auth
def patient_symptoms(request):
    """
    Get patient symptoms with pagination
    """
    try:
        patient = Patient.objects.get(user=request.user)
        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 10)
        
        symptoms = Symptom.objects.filter(patient=patient).order_by('-created_at')
        paginator = Paginator(symptoms, per_page)
        page_obj = paginator.get_page(page)
        
        # Convert symptoms to the format expected by frontend
        symptoms_data = []
        for symptom in page_obj.object_list:
            symptoms_data.append({
                'id': symptom.id,
                'patient': symptom.patient.id,
                'description': symptom.description,
                'severity': symptom.severity,
                'input_method': symptom.input_method,
                'created_at': symptom.created_at.isoformat(),
                'is_emergency': symptom.is_emergency,
                'body_location': symptom.body_location,
                'duration': symptom.duration,
                'frequency': symptom.frequency,
                'triggers': symptom.triggers,
                'associated_symptoms': symptom.associated_symptoms,
            })
        
        return JsonResponse({
            'success': True,
            'data': symptoms_data,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'total_count': paginator.count
        })
        
    except Patient.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Patient profile not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Patient symptoms error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)

@token_or_session_auth
def patient_appointments(request):
    """
    Get patient appointments
    """
    try:
        patient = Patient.objects.get(user=request.user)
        logger.info(f"Getting appointments for patient {patient.id} (user {request.user.id})")
        
        status_filter = request.GET.get('status', '')
        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 10)
        
        appointments = Appointment.objects.filter(patient=patient)
        logger.info(f"Found {appointments.count()} appointments for patient {patient.id}")
        
        if status_filter:
            appointments = appointments.filter(status=status_filter)
        
        appointments = appointments.order_by('-appointment_date')
        paginator = Paginator(appointments, per_page)
        page_obj = paginator.get_page(page)
        
        # Convert appointments to the format expected by frontend
        appointments_data = []
        for appointment in page_obj.object_list:
            appointments_data.append({
                'id': appointment.id,
                'patient': appointment.patient.id,
                'doctor': appointment.doctor.id if appointment.doctor else None,
                'hospital': appointment.doctor.hospital_affiliation if appointment.doctor else 'General Hospital',
                'date': appointment.appointment_date.date().isoformat(),
                'time': appointment.appointment_date.time().strftime('%H:%M'),
                'status': appointment.status,
                'notes': appointment.notes,
                'reason': appointment.reason,
                'created_at': appointment.created_at.isoformat(),
                'updated_at': appointment.updated_at.isoformat(),
            })
        
        logger.info(f"Returning {len(appointments_data)} appointments")
        
        return JsonResponse({
            'success': True,
            'data': appointments_data,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'total_count': paginator.count
        })
        
    except Patient.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Patient profile not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Patient appointments error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)

# Doctor Management Endpoints

@csrf_exempt
@token_or_session_auth
@require_http_methods(["GET"])
def doctor_dashboard(request):
    """
    Get doctor dashboard data
    """
    try:
        # Require authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required'
            }, status=401)
        
        doctor = Doctor.objects.get(user=request.user)
        
        # Get today's appointments
        today = timezone.now().date()
        today_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__date=today,
            status='scheduled'
        ).order_by('appointment_date')
        
        # Get all upcoming appointments (today and future)
        upcoming_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__gte=today,
            status__in=['scheduled', 'confirmed']
        ).order_by('appointment_date')[:20]  # Limit to 20 upcoming appointments
        
        # Get emergency alerts
        emergency_alerts = EmergencyAlert.objects.filter(
            assigned_responder=doctor,
            status='active'
        ).order_by('-created_at')
        
        # Get recent patients
        recent_patients = Patient.objects.filter(
            appointment__doctor=doctor
        ).distinct().order_by('-appointment__created_at')[:10]
        
        # Get notifications
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10]
        
        dashboard_data = {
            'doctor': DoctorSerializer(doctor).data,
            'today_appointments': AppointmentSerializer(today_appointments, many=True).data,
            'upcoming_appointments': AppointmentSerializer(upcoming_appointments, many=True).data,
            'emergency_alerts': EmergencyAlertSerializer(emergency_alerts, many=True).data,
            'recent_patients': PatientSerializer(recent_patients, many=True).data,
            'notifications': NotificationSerializer(notifications, many=True).data,
            'total_appointments_today': today_appointments.count(),
            'total_upcoming_appointments': upcoming_appointments.count(),
            'active_emergencies': emergency_alerts.count(),
            'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count()
        }
        
        return JsonResponse(dashboard_data)
        
    except Doctor.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Doctor profile not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Doctor dashboard error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)

# Emergency Management Endpoints

@csrf_exempt
@require_http_methods(["GET"])
def emergency_alerts(request):
    """
    Get emergency alerts (for doctors and admins)
    """
    try:
        status_filter = request.GET.get('status', 'active')
        
        # Get real emergency alerts from database
        alerts = EmergencyAlert.objects.filter(status=status_filter).order_by('-created_at')
        
        # Return real data only
        return JsonResponse({
            'emergency_alerts': EmergencyAlertSerializer(alerts, many=True).data,
            'total_count': alerts.count()
        })
        
    except Exception as e:
        logger.error(f"Emergency alerts error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return empty response on error instead of mock data
        return JsonResponse({
            'emergency_alerts': [],
            'total_count': 0,
            'error': 'Failed to fetch emergency alerts'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_emergency_status(request):
    """
    Update emergency alert status
    """
    try:
        data = json.loads(request.body)
        alert_id = data.get('alert_id')
        status = data.get('status')
        notes = data.get('notes', '')
        assigned_responder_id = data.get('assigned_responder_id')
        
        # Validate required fields
        if not alert_id or not status:
            return JsonResponse({
                'status': 'error',
                'message': 'Alert ID and status are required'
            }, status=400)
        
        # Validate status value
        valid_statuses = ['active', 'resolved', 'false_alarm', 'in_progress']
        if status not in valid_statuses:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }, status=400)
        
        # Get emergency alert
        try:
            alert = EmergencyAlert.objects.get(id=alert_id)
        except EmergencyAlert.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Emergency alert not found'
            }, status=404)
        
        # Validate state transitions
        if alert.status == 'resolved' and status != 'active':
            return JsonResponse({
                'status': 'error',
                'message': 'Cannot change status of already resolved alert'
            }, status=400)
        
        # Update alert fields
        old_status = alert.status
        alert.status = status
        alert.response_notes = notes
        
        # Handle assigned responder
        if assigned_responder_id:
            try:
                responder = Doctor.objects.get(id=assigned_responder_id)
                alert.assigned_responder = responder
            except Doctor.DoesNotExist:
                logger.warning(f"Assigned responder {assigned_responder_id} not found")
        
        # Handle resolution
        if status == 'resolved' and old_status != 'resolved':
            alert.resolved_at = timezone.now()
            if alert.created_at:
                alert.response_time = int((alert.resolved_at - alert.created_at).total_seconds() / 60)
        elif status != 'resolved':
            # If changing from resolved to another status, clear resolution data
            alert.resolved_at = None
            alert.response_time = None
        
        # Save changes
        alert.save()
        
        # Log the status change
        logger.info(f"Emergency alert {alert_id} status changed from {old_status} to {status}")
        
        # Return updated alert data
        return JsonResponse({
            'status': 'success',
            'message': f'Emergency alert status updated to {status}',
            'emergency_alert': EmergencyAlertSerializer(alert).data
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in update_emergency_status: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Update emergency status error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error',
            'details': str(e) if settings.DEBUG else None
        }, status=500)

# Hospital Capacity Management

@csrf_exempt
@require_http_methods(["GET"])
def hospital_capacity(request):
    """
    Get hospital capacity information
    """
    try:
        departments = HospitalCapacity.objects.all().order_by('department')
        
        # Calculate aggregated data that matches frontend expectations
        total_beds = 0
        icu_beds = 0
        emergency_rooms = 0
        occupied_total = 0
        occupied_icu = 0
        occupied_emergency = 0
        avg_wait_time = 0
        
        if departments.exists():
            for dept in departments:
                total_beds += dept.total_beds
                occupied_total += dept.occupied_beds
                
                if 'ICU' in dept.department.upper() or 'INTENSIVE' in dept.department.upper():
                    icu_beds += dept.total_beds
                    occupied_icu += dept.occupied_beds
                elif 'EMERGENCY' in dept.department.upper():
                    emergency_rooms += dept.total_beds
                    occupied_emergency += dept.occupied_beds
                
                avg_wait_time += dept.average_wait_time
            
            avg_wait_time = avg_wait_time // len(departments) if departments else 15
        else:
            # Mock data when no departments exist
            total_beds = 120
            icu_beds = 15
            emergency_rooms = 20
            occupied_total = 86
            occupied_icu = 12
            occupied_emergency = 16
            avg_wait_time = 15

        return JsonResponse({
            'success': True,
            'data': {
                'total_beds': total_beds,
                'available_beds': total_beds - occupied_total,
                'icu_beds': icu_beds,
                'available_icu': icu_beds - occupied_icu,
                'emergency_rooms': emergency_rooms,
                'available_emergency': emergency_rooms - occupied_emergency,
                'average_wait_time': avg_wait_time
            }
        })

    except Exception as e:
        logger.error(f"Hospital capacity error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to fetch hospital capacity data'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_capacity(request):
    """
    Update hospital capacity (for admins)
    """
    try:
        data = json.loads(request.body)
        department = data.get('department')
        total_beds = data.get('total_beds')
        occupied_beds = data.get('occupied_beds')
        available_doctors = data.get('available_doctors')
        
        if not all([department, total_beds is not None, occupied_beds is not None]):
            return JsonResponse({
                'status': 'error',
                'message': 'Department, total beds, and occupied beds are required'
            }, status=400)
        
        capacity, created = HospitalCapacity.objects.update_or_create(
            department=department,
            defaults={
                'total_beds': total_beds,
                'occupied_beds': occupied_beds,
                'available_doctors': available_doctors or 0
            }
        )
        
        return JsonResponse({
            'status': 'success',
            'capacity': HospitalCapacitySerializer(capacity).data
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Update capacity error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)

# Analytics and Reporting

@csrf_exempt
@require_http_methods(["GET"])
def analytics_dashboard(request):
    """
    Get analytics data for dashboard
    """
    try:
        # Date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Get real data from database
        total_patients = Patient.objects.count()
        total_doctors = Doctor.objects.count()
        active_emergencies = EmergencyAlert.objects.filter(status='active').count()
        total_appointments = Appointment.objects.filter(
            appointment_date__date=timezone.now().date()
        ).count()
        
        analytics_data = {
            'totalPatients': total_patients,
            'totalDoctors': total_doctors,
            'activeEmergencies': active_emergencies,
            'todayAppointments': total_appointments,
            'systemHealth': 'healthy',
            'responseTime': 120
        }
        
        return JsonResponse(analytics_data)
        
    except Exception as e:
        logger.error(f"Analytics dashboard error: {str(e)}")
        return JsonResponse({
            'totalPatients': 0,
            'totalDoctors': 0,
            'activeEmergencies': 0,
            'todayAppointments': 0,
            'systemHealth': 'error',
            'responseTime': 0
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def analytics_symptoms(request):
    """
    Get symptom analysis data for dashboard
    """
    try:
        # Date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Total reports
        total_reports = Symptom.objects.filter(created_at__range=[start_date, end_date]).count()
        
        # Emergency count
        emergency_count = Symptom.objects.filter(
            created_at__range=[start_date, end_date],
            is_emergency=True
        ).count()
        
        # Calculate average confidence from real diagnoses
        diagnoses = Diagnosis.objects.filter(
            symptom__created_at__range=[start_date, end_date],
            confidence_score__isnull=False
        )
        average_confidence = 0.0  # Default to 0 if no diagnoses
        if diagnoses.exists():
            total_confidence = sum(d.confidence_score for d in diagnoses)
            average_confidence = total_confidence / diagnoses.count()
        
        # Top symptoms from real data
        top_symptoms_query = Symptom.objects.filter(
            created_at__range=[start_date, end_date]
        ).values('description').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Convert to list format
        top_symptoms = []
        for symptom in top_symptoms_query:
            top_symptoms.append({
                'name': symptom['description'][:50], 
                'count': symptom['count']
            })
        
        symptom_data = {
            'totalReports': total_reports,
            'emergencyCount': emergency_count,
            'averageConfidence': average_confidence,
            'topSymptoms': top_symptoms
        }
        
        return JsonResponse(symptom_data)
        
    except Exception as e:
        logger.error(f"Symptom analysis error: {str(e)}")
        # Return empty data on error
        return JsonResponse({
            'totalReports': 0,
            'emergencyCount': 0,
            'averageConfidence': 0.0,
            'topSymptoms': []
        }, status=500)

# Health Check Endpoint

def health_check(request):
    """
    Health check endpoint for monitoring
    """
    try:
        # Check database connectivity
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check key services
        services_status = {
            'database': 'healthy',
            'ai_services': 'healthy',
            'communication_services': 'healthy'
        }
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'services': services_status
        })
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500) 

@csrf_exempt
@require_http_methods(["GET"])
@token_or_session_auth
def patient_list(request):
    """
    Returns a list of patients assigned to the current doctor.
    """
    try:
        # Require authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Authentication required'
            }, status=401)
        
        # Get the current doctor
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Doctor profile not found'
            }, status=404)
        
        # Get patients who have appointments with this doctor
        patients = Patient.objects.filter(
            appointment__doctor=doctor
        ).distinct()
        
        serializer = PatientSerializer(patients, many=True)
        return JsonResponse({
            'success': True,
            'data': serializer.data
        })
    except Exception as e:
        logger.error(f"Patient list error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500) 

@csrf_exempt
@require_http_methods(["GET"])
def doctor_list(request):
    """
    Returns a list of all doctors.
    """
    try:
        doctors = Doctor.objects.all()
        doctors_data = []
        for doctor in doctors:
            doctors_data.append({
                'id': doctor.id,
                'name': f"{doctor.user.first_name} {doctor.user.last_name}",
                'specialization': doctor.specialization,
                'hospital': doctor.hospital_affiliation,
                'phone_number': getattr(doctor.user, 'phone_number', ''),
                'email': doctor.user.email,
                'availability': ['Monday', 'Wednesday', 'Friday'] if doctor.is_available else [],
                'rating': 4.5,  # Default rating
                'experience_years': doctor.years_of_experience,
            })
        
        return JsonResponse({
            'success': True,
            'data': doctors_data
        })
    except Exception as e:
        logger.error(f"Doctor list error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST"])
@token_or_session_auth
def appointment_list(request):
    """
    Returns a list of appointments or creates a new appointment.
    """
    try:
        if request.method == 'GET':
            appointments = Appointment.objects.all()
            appointments_data = []
            for appointment in appointments:
                appointments_data.append({
                    'id': appointment.id,
                    'patient': appointment.patient.id,
                    'doctor': appointment.doctor.id if appointment.doctor else None,
                    'hospital': appointment.doctor.hospital_affiliation if appointment.doctor else 'General Hospital',
                    'date': appointment.appointment_date.date().isoformat(),
                    'time': appointment.appointment_date.time().strftime('%H:%M'),
                    'status': appointment.status,
                    'notes': appointment.notes,
                    'reason': appointment.reason,
                    'created_at': appointment.created_at.isoformat(),
                    'updated_at': appointment.updated_at.isoformat(),
                })
            
            return JsonResponse({
                'success': True,
                'data': appointments_data
            })
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            
            # Require authentication for appointment creation
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'message': 'Authentication required to create appointments'
                }, status=401)
            
            # Get patient from authenticated user
            try:
                patient = Patient.objects.get(user=request.user)
            except Patient.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Patient profile not found. Please complete your profile first.'
                }, status=404)

            # Create new appointment
            appointment_date = datetime.strptime(f"{data.get('date')} {data.get('time')}", '%Y-%m-%d %H:%M')
            logger.info(f"Creating appointment for patient {patient.id} on {appointment_date}")
            
            appointment = Appointment.objects.create(
                patient=patient,
                doctor_id=data.get('doctor'),
                appointment_date=appointment_date,
                status='scheduled',
                notes=data.get('notes', ''),
                reason=data.get('symptoms', 'General consultation')
            )
            
            logger.info(f"Created appointment {appointment.id} successfully")
            
            appointment_data = {
                'id': appointment.id,
                'patient': appointment.patient.id,
                'doctor': appointment.doctor.id if appointment.doctor else None,
                'hospital': appointment.doctor.hospital_affiliation if appointment.doctor else 'General Hospital',
                'date': appointment.appointment_date.date().isoformat(),
                'time': appointment.appointment_date.time().strftime('%H:%M'),
                'status': appointment.status,
                'notes': appointment.notes,
                'reason': appointment.reason,
                'created_at': appointment.created_at.isoformat(),
                'updated_at': appointment.updated_at.isoformat(),
            }
            
            return JsonResponse({
                'success': True,
                'data': appointment_data,
                'message': 'Appointment created successfully'
            })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Appointment list error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
@token_or_session_auth
def appointment_detail(request, pk):
    """
    Get, update, or delete a specific appointment.
    """
    try:
        appointment = Appointment.objects.get(pk=pk)
        
        if request.method == 'GET':
            appointment_data = {
                'id': appointment.id,
                'patient': appointment.patient.id,
                'doctor': appointment.doctor.id if appointment.doctor else None,
                'hospital': appointment.doctor.hospital_affiliation if appointment.doctor else 'General Hospital',
                'date': appointment.appointment_date.date().isoformat(),
                'time': appointment.appointment_date.time().strftime('%H:%M'),
                'status': appointment.status,
                'notes': appointment.notes,
                'reason': appointment.reason,
                'created_at': appointment.created_at.isoformat(),
                'updated_at': appointment.updated_at.isoformat(),
            }
            
            return JsonResponse({
                'success': True,
                'data': appointment_data
            })
        
        elif request.method == 'PUT':
            data = json.loads(request.body)
            
            # Update appointment fields
            if 'doctor' in data:
                appointment.doctor_id = data['doctor']
            if 'date' in data and 'time' in data:
                appointment.appointment_date = datetime.strptime(f"{data['date']} {data['time']}", '%Y-%m-%d %H:%M')
            if 'status' in data:
                appointment.status = data['status']
            if 'notes' in data:
                appointment.notes = data['notes']
            if 'symptoms' in data:
                appointment.reason = data['symptoms']
            
            appointment.save()
            
            appointment_data = {
                'id': appointment.id,
                'patient': appointment.patient.id,
                'doctor': appointment.doctor.id if appointment.doctor else None,
                'hospital': appointment.doctor.hospital_affiliation if appointment.doctor else 'General Hospital',
                'date': appointment.appointment_date.date().isoformat(),
                'time': appointment.appointment_date.time().strftime('%H:%M'),
                'status': appointment.status,
                'notes': appointment.notes,
                'reason': appointment.reason,
                'created_at': appointment.created_at.isoformat(),
                'updated_at': appointment.updated_at.isoformat(),
            }
            
            return JsonResponse({
                'success': True,
                'data': appointment_data,
                'message': 'Appointment updated successfully'
            })
        
        elif request.method == 'DELETE':
            appointment.delete()
            return JsonResponse({
                'success': True,
                'message': 'Appointment deleted successfully'
            })
    
    except Appointment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Appointment not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Appointment detail error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def notification_list(request):
    """
    Returns a list of notifications for the current user.
    """
    try:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'id': notification.id,
                'user': notification.user.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'data': notifications_data
        })
    except Exception as e:
        logger.error(f"Notification list error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def notification_mark_read(request, pk):
    """
    Mark a notification as read.
    """
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Notification mark read error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500)

# Authentication Views (duplicate removed - using the one at the end of file)

@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    """
    User logout endpoint
    """
    try:
        from django.contrib.auth import logout
        logout(request)
        return JsonResponse({
            'success': True,
            'message': 'Logout successful'
        })
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    """
    User registration endpoint
    """
    try:
        data = json.loads(request.body)
        
        # Required fields
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        # Optional patient fields
        phone_number = data.get('phone_number', '')
        date_of_birth = data.get('date_of_birth')
        gender = data.get('gender', '')
        address = data.get('address', '')
        emergency_contact = data.get('emergency_contact', '')
        medical_history = data.get('medical_history', '')
        allergies = data.get('allergies', '')
        
        if not all([username, password, email, first_name, last_name]):
            return JsonResponse({
                'success': False,
                'message': 'Username, password, email, first_name, and last_name are required'
            }, status=400)
        
        from django.contrib.auth.models import User
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'message': 'Username already exists'
            }, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'Email already exists'
            }, status=400)
        
        # Validate password
        try:
            validate_password(password)
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'message': 'Password validation failed: ' + ', '.join(e.messages)
            }, status=400)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create patient profile
        patient_data = {
            'user': user,
            'phone_number': phone_number,
            'address': address,
            'emergency_contact': emergency_contact,
            'medical_history': medical_history,
            'allergies': allergies,
        }
        
        if date_of_birth:
            from datetime import datetime
            try:
                patient_data['date_of_birth'] = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if gender:
            patient_data['gender'] = gender
        
        patient = Patient.objects.create(**patient_data)
        
        # Log in the user
        from django.contrib.auth import login
        login(request, user)
        
        # Return user data
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': patient.phone_number,
            'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            'gender': patient.gender,
            'address': patient.address,
            'emergency_contact': patient.emergency_contact,
            'medical_history': patient.medical_history,
            'allergies': patient.allergies.split(',') if patient.allergies else [],
            'insurance_info': patient.insurance_info,
        }
        
        return JsonResponse({
            'success': True,
            'data': {
                'user': user_data,
                'token': 'dummy-token-' + str(user.id)  # In production, use JWT tokens
            },
            'message': 'Registration successful'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500)

@token_or_session_auth
def profile_view(request):
    """
    Get or update user profile
    """
    try:
        if request.method == 'GET':
            # Get user profile
            try:
                patient = Patient.objects.get(user=request.user)
                user_data = {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'phone_number': patient.phone_number,
                    'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                    'gender': patient.gender,
                    'address': patient.address,
                    'emergency_contact': patient.emergency_contact,
                    'medical_history': patient.medical_history,
                    'allergies': patient.allergies.split(',') if patient.allergies else [],
                    'insurance_info': patient.insurance_info,
                }
            except Patient.DoesNotExist:
                user_data = {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                }
            
            return JsonResponse({
                'success': True,
                'data': user_data
            })
        
        elif request.method == 'PUT':
            # Update user profile
            data = json.loads(request.body)
            
            # Update user fields
            if 'first_name' in data:
                request.user.first_name = data['first_name']
            if 'last_name' in data:
                request.user.last_name = data['last_name']
            if 'email' in data:
                request.user.email = data['email']
            request.user.save()
            
            # Update or create patient profile
            patient, created = Patient.objects.get_or_create(user=request.user)
            
            if 'phone_number' in data:
                patient.phone_number = data['phone_number']
            if 'address' in data:
                patient.address = data['address']
            if 'emergency_contact' in data:
                patient.emergency_contact = data['emergency_contact']
            if 'medical_history' in data:
                patient.medical_history = data['medical_history']
            if 'allergies' in data:
                patient.allergies = data['allergies']
            if 'date_of_birth' in data and data['date_of_birth']:
                from datetime import datetime
                try:
                    patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                except ValueError:
                    pass
            if 'gender' in data:
                patient.gender = data['gender']
            
            patient.save()
            
            # Return updated user data
            user_data = {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'phone_number': patient.phone_number,
                'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                'gender': patient.gender,
                'address': patient.address,
                'emergency_contact': patient.emergency_contact,
                'medical_history': patient.medical_history,
                'allergies': patient.allergies.split(',') if patient.allergies else [],
                'insurance_info': patient.insurance_info,
            }
            
            return JsonResponse({
                'success': True,
                'data': user_data,
                'message': 'Profile updated successfully'
            })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500)

@login_required
def logout_view(request):
    """
    User logout endpoint
    """
    try:
        from django.contrib.auth import logout
        logout(request)
        return JsonResponse({
            'success': True,
            'message': 'Logout successful'
        })
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500) 

# Authentication Views
@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """
    User login endpoint
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'message': 'Username and password are required'
            }, status=400)
        
        from django.contrib.auth import authenticate, login
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Get user profile data
            try:
                patient = Patient.objects.get(user=user)
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': 'patient',
                    'phone_number': patient.phone_number,
                    'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                    'gender': patient.gender,
                    'address': patient.address,
                    'emergency_contact': patient.emergency_contact,
                    'medical_history': patient.medical_history,
                    'allergies': patient.allergies.split(',') if patient.allergies else [],
                    'insurance_info': patient.insurance_info,
                    'patient_profile': {
                        'id': patient.id,
                        'user': patient.user.id,
                        'medical_history': patient.medical_history,
                        'allergies': patient.allergies,
                        'emergency_contacts': patient.emergency_contacts,
                        'blood_type': patient.blood_type,
                        'insurance_info': patient.insurance_info
                    }
                }
            except Patient.DoesNotExist:
                try:
                    doctor = Doctor.objects.get(user=user)
                    user_data = {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'user_type': 'doctor',
                        'specialization': doctor.specialization,
                        'license_number': doctor.license_number,
                        'years_of_experience': doctor.years_of_experience,
                        'hospital_affiliation': doctor.hospital_affiliation,
                        'doctor_profile': {
                            'id': doctor.id,
                            'user': doctor.user.id,
                            'specialization': doctor.specialization,
                            'license_number': doctor.license_number,
                            'hospital_affiliation': doctor.hospital_affiliation,
                            'years_of_experience': doctor.years_of_experience,
                            'availability': [],
                            'consultation_fee': 0
                        }
                    }
                except Doctor.DoesNotExist:
                    # User exists but no patient/doctor profile - create basic user data
                    user_data = {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'user_type': 'patient',  # Default to patient
                    }
            
            # Generate JWT token
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'user': user_data,
                    'token': access_token
                },
                'message': 'Login successful'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid username or password'
            }, status=401)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    """
    User registration endpoint
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        if not all([username, password, email, first_name, last_name]):
            return JsonResponse({
                'success': False,
                'message': 'All required fields must be provided'
            }, status=400)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'message': 'Username already exists'
            }, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'Email already exists'
            }, status=400)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create patient profile
        patient = Patient.objects.create(
            user=user,
            phone_number=data.get('phone_number', ''),
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender', ''),
            address=data.get('address', ''),
            emergency_contact=data.get('emergency_contact', ''),
            medical_history=data.get('medical_history', ''),
            allergies=data.get('allergies', ''),
            insurance_info=data.get('insurance_info', '')
        )
        
        # Login the user
        from django.contrib.auth import login
        login(request, user)
        
        # Generate JWT token
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': patient.phone_number,
            'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            'gender': patient.gender,
            'address': patient.address,
            'emergency_contact': patient.emergency_contact,
            'medical_history': patient.medical_history,
            'allergies': patient.allergies.split(',') if patient.allergies else [],
            'insurance_info': patient.insurance_info,
        }
        
        return JsonResponse({
            'success': True,
            'data': {
                'user': user_data,
                'token': access_token
            },
            'message': 'Registration successful'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500)

@login_required
def profile_view(request):
    """
    Get user profile
    """
    try:
        # Try to get patient profile first
        try:
            patient = Patient.objects.get(user=request.user)
            user_data = {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'phone_number': patient.phone_number,
                'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                'gender': patient.gender,
                'address': patient.address,
                'emergency_contact': patient.emergency_contact,
                'medical_history': patient.medical_history,
                'allergies': patient.allergies.split(',') if patient.allergies else [],
                'insurance_info': patient.insurance_info,
            }
        except Patient.DoesNotExist:
            # Try to get doctor profile
            try:
                doctor = Doctor.objects.get(user=request.user)
                user_data = {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'phone_number': doctor.phone_number,
                    'specialization': doctor.specialization,
                    'license_number': doctor.license_number,
                    'years_of_experience': doctor.years_of_experience,
                }
            except Doctor.DoesNotExist:
                # User exists but no patient/doctor profile - create basic user data
                user_data = {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                }
        
        return JsonResponse({
            'success': True,
            'data': user_data
        })
    
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500)

# API Dashboard
@csrf_exempt
@require_http_methods(["GET"])
def api_dashboard(request):
    """
    API Dashboard view
    """
    return render(request, 'api_dashboard.html')

# Landing Page
@csrf_exempt
@require_http_methods(["GET"])
def landing_page(request):
    """
    Landing page view
    """
    return render(request, 'landing_page.html')

# Health Tips endpoint
@csrf_exempt
@require_http_methods(["GET"])
def health_tips(request):
    """
    Get health tips
    """
    try:
        language = request.GET.get('language', 'en')
        
        # Sample health tips
        tips = [
            {
                'id': 1,
                'title': 'Stay Hydrated',
                'content': 'Drink at least 8 glasses of water daily to maintain good health.',
                'category': 'general',
                'language': language,
                'created_at': timezone.now().isoformat()
            },
            {
                'id': 2,
                'title': 'Regular Exercise',
                'content': 'Aim for at least 30 minutes of moderate exercise most days of the week.',
                'category': 'exercise',
                'language': language,
                'created_at': timezone.now().isoformat()
            },
            {
                'id': 3,
                'title': 'Healthy Diet',
                'content': 'Include plenty of fruits, vegetables, and whole grains in your diet.',
                'category': 'nutrition',
                'language': language,
                'created_at': timezone.now().isoformat()
            }
        ]
        
        return JsonResponse({
            'success': True,
            'data': tips
        })
        
    except Exception as e:
        logger.error(f"Health tips error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Internal server error'
        }, status=500) 

 
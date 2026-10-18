from typing import Dict, Optional, List
from django.conf import settings
from django.utils import timezone
from .models import Patient, Notification, Appointment, Symptom, Diagnosis, EmergencyAlert
from .ai_services import SymptomAnalyzer, EmergencyResponseSystem, DoctorMatcher, HealthRiskAssessor

class SMSService:
    def __init__(self):
        self.symptom_analyzer = SymptomAnalyzer();
        self.emergency_system = EmergencyResponseSystem();
        self.doctor_matcher = DoctorMatcher();
        self.risk_assessor = HealthRiskAssessor();
        
        # SMS command patterns
        self.command_patterns = {
            'symptom_report': r'^(symptom|feeling|pain|ache|fever|headache|cough|nausea|vomiting|diarrhea|fatigue|chest|breathing|abdominal|tummy|tumbo|kichwa|homa|kikohozi)',
            'appointment_cancel': r'^(cancel|stop|end|finish)',
            'appointment_reschedule': r'^(reschedule|change|move|postpone)',
            'appointment_confirm': r'^(confirm|yes|ok|accept)',
            'help': r'^(help|aid|assist|support|msaada)',
            'emergency': r'^(emergency|urgent|critical|help|msaada|dharura)'
        }
        
        # Multi-language responses
        self.responses = {
            'english': {
                'welcome': 'Welcome to AI Healthcare Platform. Describe your symptoms or type HELP for assistance.',
                'symptom_received': 'Thank you for your symptom report. Our AI is analyzing your symptoms...',
                'emergency_alert': 'EMERGENCY ALERT: {action}. Emergency services have been notified.',
                'appointment_confirmed': 'Your appointment has been confirmed for {date} at {time}.',
                'appointment_cancelled': 'Your appointment has been cancelled. Call us to reschedule.',
                'help_message': 'Available commands: Describe symptoms, CANCEL appointment, RESCHEDULE appointment, HELP for assistance.',
                'error_message': 'Sorry, I didn\'t understand. Please describe your symptoms or type HELP.',
                'registration_required': 'Please register through our mobile app or call our helpline.'
            },
            'swahili': {
                'welcome': 'Karibu kwenye Jukwaa la Afya la AI. Elezea dalili zako au andika MSAADA kwa usaidizi.',
                'symptom_received': 'Asante kwa ripoti ya dalili. AI yetu inachambua dalili zako...',
                'emergency_alert': 'TAHADHARI YA DHARURA: {action}. Huduma za dharura zimetangazwa.',
                'appointment_confirmed': 'Mkutano wako umethibitishwa kwa {date} saa {time}.',
                'appointment_cancelled': 'Mkutano wako umefutwa. Tuite kwa kupanga tena.',
                'help_message': 'Amri zinazopatikana: Elezea dalili, FUTA mkutano, BADILISHA mkutano, MSAADA kwa usaidizi.',
                'error_message': 'Samahani, sikuelewa. Tafadhali elezea dalili zako au andika MSAADA.',
                'registration_required': 'Tafadhali jisajili kupitia programu ya simu au tuite.'
            }
        }

    def process_incoming_sms(self, phone_number: str, message: str) -> Dict:
        """
        Enhanced SMS processing with multi-language support and intelligent routing
        """
        try:
            # Detect language
            language = self._detect_language(message);
            
            # Try to find patient
            try:
                patient = Patient.objects.get(phone_number=phone_number);
            except Patient.DoesNotExist:
                return self._get_response('registration_required', language);
            
            # Process message based on content
            if self._is_emergency(message):
                return self._handle_emergency(patient, message, language);
            elif self._is_symptom_report(message):
                return self._handle_symptom_report(patient, message, language);
            elif self._is_appointment_action(message):
                return self._handle_appointment_action(patient, message, language);
            elif self._is_help_request(message):
                return self._handle_help_request(patient, language);
            else:
                return self._handle_unknown_message(patient, message, language);
                
        except Exception as e:
            return {
                'status': 'error',
                'message': 'System error. Please try again or call our helpline.',
                'language': 'english'
            };

    def _detect_language(self, message: str) -> str:
        """
        Detect language of the message
        """
        swahili_words = ['homa', 'kikohozi', 'kichwa', 'tumbo', 'kutapika', 'kuhara', 'uchovu', 'msaada', 'dharura'];
        if any(word in message.lower() for word in swahili_words):
            return 'swahili';
        return 'english';

    def _is_emergency(self, message: str) -> bool:
        """
        Check if message indicates emergency
        """
        emergency_keywords = ['emergency', 'urgent', 'critical', 'help', 'msaada', 'dharura', 'unconscious', 'seizure'];
        return any(keyword in message.lower() for keyword in emergency_keywords);

    def _is_symptom_report(self, message: str) -> bool:
        """
        Enhanced symptom report detection
        """
        symptom_keywords = [
            'pain', 'ache', 'fever', 'headache', 'cough', 'nausea', 'vomiting', 
            'diarrhea', 'fatigue', 'chest', 'breathing', 'abdominal', 'tummy',
            'tumbo', 'kichwa', 'homa', 'kikohozi', 'kutapika', 'kuhara', 'uchovu'
        ];
        return any(keyword in message.lower() for keyword in symptom_keywords);

    def _is_appointment_action(self, message: str) -> bool:
        """
        Check if message is appointment-related
        """
        action_keywords = ['cancel', 'reschedule', 'confirm', 'appointment', 'mkutano', 'futa', 'badilisha'];
        return any(keyword in message.lower() for keyword in action_keywords);

    def _is_help_request(self, message: str) -> bool:
        """
        Check if message is a help request
        """
        help_keywords = ['help', 'aid', 'assist', 'support', 'msaada'];
        return any(keyword in message.lower() for keyword in help_keywords);

    def _handle_emergency(self, patient: Patient, message: str, language: str) -> Dict:
        """
        Handle emergency messages
        """
        # Create emergency symptom record
        symptom = patient.symptom_set.create(
            description=message,
            severity='critical',
            input_method='sms',
            is_emergency=True
        );
        
        # Get emergency response plan
        emergency_plan = self.emergency_system.get_emergency_response_plan(symptom);
        
        # Create emergency alert
        EmergencyAlert.objects.create(
            patient=patient,
            symptom=symptom,
            status='active',
            location=patient.location or 'Unknown',
            emergency_type=emergency_plan.get('emergency_type', 'general_emergency'),
            severity_level='critical'
        );
        
        # Find appropriate doctor
        doctor = self.doctor_matcher.find_appropriate_doctor(symptom, patient);
        if doctor:
            emergency_plan['assigned_responder'] = doctor;
        
        return {
            'status': 'emergency',
            'message': self._get_response('emergency_alert', language).format(
                action=emergency_plan['immediate_action']
            ),
            'emergency_plan': emergency_plan,
            'language': language
        };

    def _handle_symptom_report(self, patient: Patient, message: str, language: str) -> Dict:
        """
        Enhanced symptom report handling
        """
        # Analyze symptom with AI
        severity, confidence, is_emergency, disease_predictions = self.symptom_analyzer.analyze_symptom(message);
        
        # Create symptom record
        symptom = patient.symptom_set.create(
            description=message,
            severity=severity,
            input_method='sms',
            is_emergency=is_emergency
        );
        
        # Assess health risk
        risk_assessment = self.risk_assessor.assess_health_risk(patient, symptom);
        
        # Generate preliminary diagnosis
        diagnosis_text = self.symptom_analyzer.generate_preliminary_diagnosis(symptom);
        
        # Create diagnosis record
        diagnosis = Diagnosis.objects.create(
            symptom=symptom,
            preliminary_diagnosis=diagnosis_text,
            confidence_score=confidence,
            is_ai_generated=True
        );
        
        # Find appropriate doctor
        doctor = self.doctor_matcher.find_appropriate_doctor(symptom, patient);
        
        # Prepare response
        response_data = {
            'status': 'success',
            'message': self._get_response('symptom_received', language),
            'diagnosis': diagnosis_text,
            'severity': severity,
            'confidence': confidence,
            'risk_level': risk_assessment['risk_level'],
            'recommendations': risk_assessment['recommendations'],
            'language': language
        };
        
        # Add doctor recommendation if available
        if doctor:
            response_data['recommended_doctor'] = f"Dr. {doctor.user.get_full_name()} - {doctor.specialization}";
            response_data['doctor_contact'] = doctor.user.email;
        
        # Check if emergency
        if is_emergency:
            emergency_plan = self.emergency_system.get_emergency_response_plan(symptom);
            response_data['emergency_alert'] = emergency_plan['immediate_action'];
        
        return response_data;

    def _handle_appointment_action(self, patient: Patient, message: str, language: str) -> Dict:
        """
        Handle appointment-related actions
        """
        message_lower = message.lower();
        
        # Get patient's upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            patient=patient,
            status='scheduled',
            appointment_date__gte=timezone.now()
        ).order_by('appointment_date');
        
        if not upcoming_appointments.exists():
            return {
                'status': 'error',
                'message': 'No upcoming appointments found.',
                'language': language
            };
        
        appointment = upcoming_appointments.first();
        
        if 'cancel' in message_lower or 'futa' in message_lower:
            appointment.status = 'cancelled';
            appointment.cancellation_reason = 'Cancelled via SMS';
            appointment.save();
            
            return {
                'status': 'success',
                'message': self._get_response('appointment_cancelled', language),
                'language': language
            };
        
        elif 'reschedule' in message_lower or 'badilisha' in message_lower:
            # For rescheduling, we need more information
            return {
                'status': 'info',
                'message': 'To reschedule, please call our helpline or use the mobile app.',
                'language': language
            };
        
        elif 'confirm' in message_lower:
            return {
                'status': 'success',
                'message': self._get_response('appointment_confirmed', language).format(
                    date=appointment.appointment_date.strftime('%Y-%m-%d'),
                    time=appointment.appointment_date.strftime('%H:%M')
                ),
                'language': language
            };
        
        return {
            'status': 'error',
            'message': self._get_response('error_message', language),
            'language': language
        };

    def _handle_help_request(self, patient: Patient, language: str) -> Dict:
        """
        Handle help requests
        """
        return {
            'status': 'info',
            'message': self._get_response('help_message', language),
            'language': language
        };

    def _handle_unknown_message(self, patient: Patient, message: str, language: str) -> Dict:
        """
        Handle unrecognized messages
        """
        return {
            'status': 'error',
            'message': self._get_response('error_message', language),
            'language': language
        };

    def _get_response(self, key: str, language: str) -> str:
        """
        Get localized response message
        """
        return self.responses.get(language, self.responses['english']).get(key, 'Message not found');

class VoiceCallService:
    def __init__(self):
        self.symptom_analyzer = SymptomAnalyzer();
        self.emergency_system = EmergencyResponseSystem();
        self.doctor_matcher = DoctorMatcher();
        self.risk_assessor = HealthRiskAssessor();
        
        # Voice-specific patterns
        self.voice_patterns = {
            'greeting': ['hello', 'hi', 'start', 'begin', 'karibu', 'hodi'],
            'symptom_description': ['pain', 'ache', 'fever', 'headache', 'cough', 'nausea'],
            'emergency': ['emergency', 'urgent', 'help', 'dharura', 'msaada'],
            'goodbye': ['goodbye', 'bye', 'end', 'stop', 'kwaheri', 'end']
        };

    def process_voice_input(self, phone_number: str, transcript: str, language: str = 'english') -> Dict:
        """
        Process voice call input with enhanced NLP
        """
        try:
            # Find patient
            try:
                patient = Patient.objects.get(phone_number=phone_number);
            except Patient.DoesNotExist:
                return {
                    'status': 'error',
                    'message': 'Please register through our mobile app or call our helpline.',
                    'voice_response': 'Please register through our mobile app or call our helpline.'
                };
            
            # Process transcript
            transcript_lower = transcript.lower();
            
            # Check for emergency
            if self._is_emergency_voice(transcript_lower):
                return self._handle_voice_emergency(patient, transcript, language);
            
            # Check for symptom description
            elif self._is_symptom_description(transcript_lower):
                return self._handle_voice_symptom(patient, transcript, language);
            
            # Check for greeting
            elif self._is_greeting(transcript_lower):
                return self._handle_voice_greeting(patient, language);
            
            # Default response
            else:
                return self._handle_voice_unknown(patient, transcript, language);
                
        except Exception as e:
            return {
                'status': 'error',
                'message': 'System error. Please try again.',
                'voice_response': 'System error. Please try again.'
            };

    def _is_emergency_voice(self, transcript: str) -> bool:
        """
        Check if voice input indicates emergency
        """
        emergency_words = ['emergency', 'urgent', 'help', 'critical', 'dharura', 'msaada', 'unconscious'];
        return any(word in transcript for word in emergency_words);

    def _is_symptom_description(self, transcript: str) -> bool:
        """
        Check if voice input describes symptoms
        """
        symptom_words = ['pain', 'ache', 'fever', 'headache', 'cough', 'nausea', 'vomiting', 'diarrhea'];
        return any(word in transcript for word in symptom_words);

    def _is_greeting(self, transcript: str) -> bool:
        """
        Check if voice input is a greeting
        """
        greeting_words = ['hello', 'hi', 'start', 'begin', 'karibu', 'hodi'];
        return any(word in transcript for word in greeting_words);

    def _handle_voice_emergency(self, patient: Patient, transcript: str, language: str) -> Dict:
        """
        Handle emergency voice calls
        """
        # Create emergency symptom record
        symptom = patient.symptom_set.create(
            description=transcript,
            severity='critical',
            input_method='voice',
            is_emergency=True
        );
        
        # Get emergency response plan
        emergency_plan = self.emergency_system.get_emergency_response_plan(symptom);
        
        # Create emergency alert
        EmergencyAlert.objects.create(
            patient=patient,
            symptom=symptom,
            status='active',
            location=patient.location or 'Unknown',
            emergency_type=emergency_plan.get('emergency_type', 'general_emergency'),
            severity_level='critical'
        );
        
        voice_response = f"EMERGENCY ALERT: {emergency_plan['immediate_action']}. Emergency services have been notified.";
        
        return {
            'status': 'emergency',
            'message': voice_response,
            'voice_response': voice_response,
            'emergency_plan': emergency_plan
        };

    def _handle_voice_symptom(self, patient: Patient, transcript: str, language: str) -> Dict:
        """
        Handle symptom description in voice calls
        """
        # Analyze symptom
        severity, confidence, is_emergency, disease_predictions = self.symptom_analyzer.analyze_symptom(transcript);
        
        # Create symptom record
        symptom = patient.symptom_set.create(
            description=transcript,
            severity=severity,
            input_method='voice',
            is_emergency=is_emergency
        );
        
        # Generate diagnosis
        diagnosis_text = self.symptom_analyzer.generate_preliminary_diagnosis(symptom);
        
        # Create diagnosis record
        diagnosis = Diagnosis.objects.create(
            symptom=symptom,
            preliminary_diagnosis=diagnosis_text,
            confidence_score=confidence,
            is_ai_generated=True
        );
        
        # Find doctor
        doctor = self.doctor_matcher.find_appropriate_doctor(symptom, patient);
        
        # Prepare voice response
        voice_response = f"Thank you for describing your symptoms. {diagnosis_text}";
        
        if doctor:
            voice_response += f" I recommend consulting Dr. {doctor.user.get_full_name()}, a {doctor.specialization}.";
        
        if is_emergency:
            voice_response += " This appears to be an emergency. Please seek immediate medical attention.";
        
        return {
            'status': 'success',
            'message': voice_response,
            'voice_response': voice_response,
            'diagnosis': diagnosis_text,
            'severity': severity,
            'confidence': confidence
        };

    def _handle_voice_greeting(self, patient: Patient, language: str) -> Dict:
        """
        Handle greeting in voice calls
        """
        greeting_response = "Welcome to AI Healthcare Platform. Please describe your symptoms or say 'emergency' if this is urgent.";
        
        if language == 'swahili':
            greeting_response = "Karibu kwenye Jukwaa la Afya la AI. Tafadhali elezea dalili zako au sema 'dharura' ikiwa hii ni ya haraka.";
        
        return {
            'status': 'info',
            'message': greeting_response,
            'voice_response': greeting_response
        };

    def _handle_voice_unknown(self, patient: Patient, transcript: str, language: str) -> Dict:
        """
        Handle unrecognized voice input
        """
        unknown_response = "I didn't understand that. Please describe your symptoms clearly or say 'emergency' if this is urgent.";
        
        if language == 'swahili':
            unknown_response = "Sikuelewa hiyo. Tafadhali elezea dalili zako kwa uwazi au sema 'dharura' ikiwa hii ni ya haraka.";
        
        return {
            'status': 'error',
            'message': unknown_response,
            'voice_response': unknown_response
        };

class NotificationService:
    @staticmethod
    def create_test_result_notification(test_result):
        """
        Create notification for test results
        """
        title = f"Test Result: {test_result.test_name}";
        message = f"Your {test_result.test_name} results are ready. Please check your medical records.";
        
        if test_result.is_abnormal:
            title = f"URGENT: Abnormal Test Result - {test_result.test_name}";
            message = f"Your {test_result.test_name} results show abnormal values. Please contact your doctor immediately.";
        
        Notification.objects.create(
            user=test_result.patient.user,
            notification_type='result',
            title=title,
            message=message,
            delivery_method='all',
            priority='high' if test_result.is_abnormal else 'medium',
            action_required=test_result.is_abnormal
        );

    @staticmethod
    def create_follow_up_notification(instance):
        """
        Create follow-up notifications
        """
        if hasattr(instance, 'follow_up_required') and instance.follow_up_required:
            if hasattr(instance, 'follow_up_date') and instance.follow_up_date:
                # Create reminder notification
                Notification.objects.create(
                    user=instance.patient.user,
                    notification_type='follow_up',
                    title="Follow-up Appointment Reminder",
                    message=f"You have a follow-up appointment scheduled for {instance.follow_up_date.strftime('%Y-%m-%d %H:%M')}.",
                    delivery_method='all',
                    priority='medium',
                    action_required=True
                );

    @staticmethod
    def create_system_notification(user, title, message, priority='medium', action_required=False, action_url=''):
        """
        Create system notifications
        """
        Notification.objects.create(
            user=user,
            notification_type='system',
            title=title,
            message=message,
            delivery_method='all',
            priority=priority,
            action_required=action_required,
            action_url=action_url
        );

    @staticmethod
    def create_emergency_notification(emergency_alert):
        """
        Create emergency notifications
        """
        # Notify patient
        Notification.objects.create(
            user=emergency_alert.patient.user,
            notification_type='emergency',
            title="Emergency Alert",
            message=f"Emergency services have been notified. {emergency_alert.symptom.description}",
            delivery_method='all',
            priority='urgent',
            action_required=True
        );
        
        # Notify assigned doctor if available
        if emergency_alert.assigned_responder:
            Notification.objects.create(
                user=emergency_alert.assigned_responder.user,
                notification_type='emergency',
                title="Emergency Case Assigned",
                message=f"Emergency case assigned: {emergency_alert.symptom.description}",
                delivery_method='all',
                priority='urgent',
                action_required=True
            );

    @staticmethod
    def create_appointment_notification(appointment):
        """
        Create appointment notifications
        """
        if appointment.status == 'scheduled':
            # Reminder notification
            Notification.objects.create(
                user=appointment.patient.user,
                notification_type='appointment',
                title="Appointment Reminder",
                message=f"Reminder: You have an appointment with Dr. {appointment.doctor.user.get_full_name()} on {appointment.appointment_date.strftime('%Y-%m-%d %H:%M')}.",
                delivery_method='all',
                priority='medium',
                action_required=False
            );
        elif appointment.status == 'cancelled':
            # Cancellation notification
            Notification.objects.create(
                user=appointment.patient.user,
                notification_type='appointment',
                title="Appointment Cancelled",
                message=f"Your appointment with Dr. {appointment.doctor.user.get_full_name()} has been cancelled.",
                delivery_method='all',
                priority='medium',
                action_required=False
            ); 
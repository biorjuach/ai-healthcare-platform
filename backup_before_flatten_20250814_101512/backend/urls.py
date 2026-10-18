from django.urls import path, include
from django.contrib import admin
from . import views

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Multi-channel Communication Endpoints
    path('api/sms/webhook/', views.sms_webhook, name='sms_webhook'),
    path('api/voice/webhook/', views.voice_webhook, name='voice_webhook'),
    
    # Symptom Analysis Endpoints
    path('api/symptoms/analyze/', views.analyze_symptoms, name='analyze_symptoms'),
    path('api/symptoms/submit/', views.submit_symptom_report, name='submit_symptom_report'),
    
    # Patient Management Endpoints
    path('api/patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('api/patient/symptoms/', views.patient_symptoms, name='patient_symptoms'),
    path('api/patient/appointments/', views.patient_appointments, name='patient_appointments'),
    
    # Doctor Management Endpoints
    path('api/doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    
    # Emergency Management Endpoints
    path('api/emergency/alerts/', views.emergency_alerts, name='emergency_alerts'),
    path('api/emergency/update-status/', views.update_emergency_status, name='update_emergency_status'),
    
    # Hospital Capacity Management
    path('api/hospital/capacity/', views.hospital_capacity, name='hospital_capacity'),
    path('api/hospital/capacity/update/', views.update_capacity, name='update_capacity'),
    
    # Analytics and Reporting
    path('api/analytics/dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('api/analytics/symptoms/', views.analytics_symptoms, name='analytics_symptoms'),
    
    # Health Check
    path('api/health/', views.health_check, name='health_check'),
    
    # Health Tips
    path('api/health-tips/', views.health_tips, name='health_tips'),
    
    # API Dashboard
    path('dashboard/', views.api_dashboard, name='api_dashboard'),
    
    # REST API endpoints for CRUD operations
    path('api/patients/', views.patient_list, name='patient_list'),
    # path('api/patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    # path('api/doctors/', views.doctor_list, name='doctor_list'),
    # path('api/doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    # path('api/symptoms/', views.symptom_list, name='symptom_list'),
    # path('api/symptoms/<int:pk>/', views.symptom_detail, name='symptom_detail'),
    # path('api/diagnoses/', views.diagnosis_list, name='diagnosis_list'),
    # path('api/diagnoses/<int:pk>/', views.diagnosis_detail, name='diagnosis_detail'),
    # path('api/appointments/', views.appointment_list, name='appointment_list'),
    # path('api/appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    # path('api/medical-records/', views.medical_record_list, name='medical_record_list'),
    # path('api/medical-records/<int:pk>/', views.medical_record_detail, name='medical_record_detail'),
    # path('api/notifications/', views.notification_list, name='notification_list'),
    # path('api/notifications/<int:pk>/', views.notification_detail, name='notification_detail'),
    # path('api/test-results/', views.test_result_list, name='test_result_list'),
    # path('api/test-results/<int:pk>/', views.test_result_detail, name='test_result_detail'),
    # path('api/emergency-alerts/', views.emergency_alert_list, name='emergency_alert_list'),
    # path('api/emergency-alerts/<int:pk>/', views.emergency_alert_detail, name='emergency_alert_detail'),
    # path('api/hospital-capacity/', views.hospital_capacity_list, name='hospital_capacity_list'),
    # path('api/hospital-capacity/<int:pk>/', views.hospital_capacity_detail, name='hospital_capacity_detail'),
    
    # Authentication endpoints
    path('api/auth/login/', views.login_view, name='login'),
    path('api/auth/logout/', views.logout_view, name='logout'),
    path('api/auth/register/', views.register_view, name='register'),
    path('api/auth/profile/', views.profile_view, name='profile'),
    
    # Search and filtering endpoints
    # path('api/search/patients/', views.search_patients, name='search_patients'),
    # path('api/search/doctors/', views.search_doctors, name='search_doctors'),
    # path('api/search/symptoms/', views.search_symptoms, name='search_symptoms'),
    
    # Reporting endpoints
    # path('api/reports/patient-summary/<int:patient_id>/', views.patient_summary_report, name='patient_summary_report'),
    # path('api/reports/doctor-summary/<int:doctor_id>/', views.doctor_summary_report, name='doctor_summary_report'),
    # path('api/reports/emergency-summary/', views.emergency_summary_report, name='emergency_summary_report'),
    # path('api/reports/hospital-summary/', views.hospital_summary_report, name='hospital_summary_report'),
    
    # Integration endpoints
    # path('api/integration/hmis/', views.hmis_integration, name='hmis_integration'),
    # path('api/integration/sms-gateway/', views.sms_gateway_integration, name='sms_gateway_integration'),
    # path('api/integration/voice-gateway/', views.voice_gateway_integration, name='voice_gateway_integration'),
    
    # Mobile app specific endpoints
    # path('api/mobile/sync/', views.mobile_sync, name='mobile_sync'),
    # path('api/mobile/offline-data/', views.mobile_offline_data, name='mobile_offline_data'),
    # path('api/mobile/push-notification/', views.mobile_push_notification, name='mobile_push_notification'),
    
    # Admin dashboard endpoints
    # path('api/admin/system-status/', views.admin_system_status, name='admin_system_status'),
    # path('api/admin/user-management/', views.admin_user_management, name='admin_user_management'),
    # path('api/admin/data-export/', views.admin_data_export, name='admin_data_export'),
    # path('api/admin/backup-restore/', views.admin_backup_restore, name='admin_backup_restore'),
    
    # Community Health Worker endpoints
    # path('api/chw/patients/', views.chw_patient_list, name='chw_patient_list'),
    # path('api/chw/assignments/', views.chw_assignments, name='chw_assignments'),
    # path('api/chw/reports/', views.chw_reports, name='chw_reports'),
    
    # Telemedicine endpoints
    # path('api/telemedicine/session/', views.telemedicine_session, name='telemedicine_session'),
    # path('api/telemedicine/consultation/', views.telemedicine_consultation, name='telemedicine_consultation'),
    # path('api/telemedicine/prescription/', views.telemedicine_prescription, name='telemedicine_prescription'),
    
    # Laboratory integration
    # path('api/lab/orders/', views.lab_orders, name='lab_orders'),
    # path('api/lab/results/', views.lab_results, name='lab_results'),
    # path('api/lab/tests/', views.lab_tests, name='lab_tests'),
    
    # Pharmacy integration
    # path('api/pharmacy/prescriptions/', views.pharmacy_prescriptions, name='pharmacy_prescriptions'),
    # path('api/pharmacy/medications/', views.pharmacy_medications, name='pharmacy_medications'),
    # path('api/pharmacy/inventory/', views.pharmacy_inventory, name='pharmacy_inventory'),
    
    # Insurance integration
    # path('api/insurance/verification/', views.insurance_verification, name='insurance_verification'),
    # path('api/insurance/claims/', views.insurance_claims, name='insurance_claims'),
    # path('api/insurance/coverage/', views.insurance_coverage, name='insurance_coverage'),
    
    # Payment processing
    # path('api/payments/process/', views.payment_process, name='payment_process'),
    # path('api/payments/history/', views.payment_history, name='payment_history'),
    # path('api/payments/refund/', views.payment_refund, name='payment_refund'),
    
    # Data analytics and ML
    # path('api/ml/predict/', views.ml_predict, name='ml_predict'),
    # path('api/ml/train/', views.ml_train, name='ml_train'),
    # path('api/ml/models/', views.ml_models, name='ml_models'),
    # path('api/analytics/trends/', views.analytics_trends, name='analytics_trends'),
    # path('api/analytics/predictions/', views.analytics_predictions, name='analytics_predictions'),
    
    # System monitoring and maintenance
    # path('api/system/logs/', views.system_logs, name='system_logs'),
    # path('api/system/performance/', views.system_performance, name='system_performance'),
    # path('api/system/backup/', views.system_backup, name='system_backup'),
    # path('api/system/restore/', views.system_restore, name='system_restore'),
    
    # API documentation
    # path('api/docs/', views.api_documentation, name='api_documentation'),
    # path('api/schema/', views.api_schema, name='api_schema'),
    
    # Webhook endpoints for external integrations
    # path('api/webhooks/twilio/', views.twilio_webhook, name='twilio_webhook'),
    # path('api/webhooks/africas-talking/', views.africas_talking_webhook, name='africas_talking_webhook'),
    # path('api/webhooks/firebase/', views.firebase_webhook, name='firebase_webhook'),
    # path('api/webhooks/aws/', views.aws_webhook, name='aws_webhook'),
    
    # File upload and management
    # path('api/files/upload/', views.file_upload, name='file_upload'),
    # path('api/files/download/<str:file_id>/', views.file_download, name='file_download'),
    # path('api/files/delete/<str:file_id>/', views.file_delete, name='file_delete'),
    
    # Notification management
    # path('api/notifications/send/', views.send_notification, name='send_notification'),
    # path('api/notifications/bulk/', views.bulk_notification, name='bulk_notification'),
    # path('api/notifications/templates/', views.notification_templates, name='notification_templates'),
    
    # Appointment scheduling
    # path('api/appointments/schedule/', views.schedule_appointment, name='schedule_appointment'),
    # path('api/appointments/available-slots/', views.available_slots, name='available_slots'),
    # path('api/appointments/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    # path('api/appointments/cancel/', views.cancel_appointment, name='cancel_appointment'),
    
    # Patient education and resources
    # path('api/education/articles/', views.education_articles, name='education_articles'),
    # path('api/education/videos/', views.education_videos, name='education_videos'),
    # path('api/education/faqs/', views.education_faqs, name='education_faqs'),
    
    # Support and feedback
    # path('api/support/tickets/', views.support_tickets, name='support_tickets'),
    # path('api/support/chat/', views.support_chat, name='support_chat'),
    # path('api/feedback/submit/', views.feedback_submit, name='feedback_submit'),
    
    # Settings and preferences
    # path('api/settings/user/', views.user_settings, name='user_settings'),
    # path('api/settings/system/', views.system_settings, name='system_settings'),
    # path('api/settings/notifications/', views.notification_settings, name='notification_settings'),
    
    # Data import/export
    # path('api/data/import/', views.data_import, name='data_import'),
    # path('api/data/export/', views.data_export, name='data_export'),
    # path('api/data/migrate/', views.data_migrate, name='data_migrate'),
    
    # Security and audit
    # path('api/security/audit-logs/', views.audit_logs, name='audit_logs'),
    # path('api/security/permissions/', views.security_permissions, name='security_permissions'),
    # path('api/security/encryption/', views.security_encryption, name='security_encryption'),
    
    # Default landing page
    path('', views.landing_page, name='landing_page'),
] 
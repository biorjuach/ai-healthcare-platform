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
    path('api/appointments/', views.appointment_list, name='appointment_list'),
    path('api/appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('api/doctors/', views.doctor_list, name='doctor_list'),
    path('api/notifications/', views.notification_list, name='notification_list'),
    path('api/notifications/<int:pk>/read/', views.notification_mark_read, name='notification_mark_read'),
    

    
    # Authentication endpoints
    path('api/auth/login/', views.login_view, name='login'),
    path('api/auth/logout/', views.logout_view, name='logout'),
    path('api/auth/register/', views.register_view, name='register'),
    path('api/auth/profile/', views.profile_view, name='profile'),
    
    # Default landing page
    path('', views.landing_page, name='landing_page'),
] 
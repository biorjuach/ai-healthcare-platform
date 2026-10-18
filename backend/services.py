from django.utils import timezone
from .models import Notification, Appointment, TestResult

class NotificationService:
    @staticmethod
    def create_appointment_notification(appointment, notification_type='appointment'):
        """Create a notification for appointment-related events"""
        if notification_type == 'appointment':
            title = 'New Appointment Scheduled'
            message = f'Your appointment with Dr. {appointment.doctor.user.get_full_name()} has been scheduled for {appointment.appointment_date}'
        elif notification_type == 'reminder':
            title = 'Appointment Reminder'
            message = f'Reminder: You have an appointment with Dr. {appointment.doctor.user.get_full_name()} tomorrow at {appointment.appointment_date}'
        elif notification_type == 'cancellation':
            title = 'Appointment Cancelled'
            message = f'Your appointment with Dr. {appointment.doctor.user.get_full_name()} has been cancelled'
        
        return Notification.objects.create(
            user=appointment.patient.user,
            notification_type=notification_type,
            title=title,
            message=message
        )

    @staticmethod
    def create_test_result_notification(test_result):
        """Create a notification for new test results"""
        return Notification.objects.create(
            user=test_result.patient.user,
            notification_type='result',
            title='New Test Result Available',
            message=f'Your {test_result.test_name} results are now available'
        )

    @staticmethod
    def create_system_notification(user, title, message):
        """Create a system notification"""
        return Notification.objects.create(
            user=user,
            notification_type='system',
            title=title,
            message=message
        )

    @staticmethod
    def send_appointment_reminders():
        """Send reminders for appointments scheduled for tomorrow"""
        tomorrow = timezone.now() + timezone.timedelta(days=1)
        appointments = Appointment.objects.filter(
            appointment_date__date=tomorrow.date(),
            status='scheduled'
        )
        
        for appointment in appointments:
            NotificationService.create_appointment_notification(
                appointment,
                notification_type='reminder'
            ) 
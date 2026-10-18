from django.core.management.base import BaseCommand
from backend.services import NotificationService

class Command(BaseCommand):
    help = 'Sends reminders for appointments scheduled for tomorrow'

    def handle(self, *args, **options):
        try:
            NotificationService.send_appointment_reminders()
            self.stdout.write(
                self.style.SUCCESS('Successfully sent appointment reminders')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error sending appointment reminders: {str(e)}')
            ) 
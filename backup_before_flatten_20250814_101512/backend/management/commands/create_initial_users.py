from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from backend.models import Doctor

class Command(BaseCommand):
    help = 'Create initial superuser and doctor for Makueni County Referral Hospital'

    def handle(self, *args, **options):
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@makuenihospital.com',
                password='admin123',
                first_name='Hospital',
                last_name='Admin'
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully created superuser')
            )

        # Create initial doctor
        if not Doctor.objects.filter(user__username='dr.smith').exists():
            user = User.objects.create_user(
                username='dr.smith',
                email='dr.smith@makuenihospital.com',
                password='doctor123',
                first_name='John',
                last_name='Smith'
            )
            Doctor.objects.create(
                user=user,
                specialization='general',
                license_number='MD123456',
                years_of_experience=10,
                hospital_affiliation='Makueni County Referral Hospital',
                is_available=True
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully created initial doctor')
            ) 
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from backend.models import UserProfile

class Command(BaseCommand):
    help = 'Create profiles for all users and update patient names'

    def handle(self, *args, **options):
        # Create profiles for all users
        for user in User.objects.all():
            UserProfile.objects.get_or_create(user=user)
            self.stdout.write(f'Created profile for {user.username}')

        # Update patient names
        patient_updates = {
            'patient1': {
                'first_name': 'Alice',
                'last_name': 'Smith',
                'kenyan_first_name': 'Alice',
                'kenyan_last_name': 'Wanjiru'
            },
            'patient2': {
                'first_name': 'Bob',
                'last_name': 'Johnson',
                'kenyan_first_name': 'Bob',
                'kenyan_last_name': 'Ochieng'
            },
            'patient3': {
                'first_name': 'Carol',
                'last_name': 'Williams',
                'kenyan_first_name': 'Abdi',
                'kenyan_last_name': 'Mohamed'
            }
        }

        # Update each patient
        for username, names in patient_updates.items():
            try:
                user = User.objects.get(username=username)
                user.first_name = names['first_name']
                user.last_name = names['last_name']
                user.save()
                
                profile = user.profile
                profile.kenyan_first_name = names['kenyan_first_name']
                profile.kenyan_last_name = names['kenyan_last_name']
                profile.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated {username}: {names["first_name"]} {names["last_name"]} '
                        f'({names["kenyan_first_name"]} {names["kenyan_last_name"]})'
                    )
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User {username} not found')
                ) 
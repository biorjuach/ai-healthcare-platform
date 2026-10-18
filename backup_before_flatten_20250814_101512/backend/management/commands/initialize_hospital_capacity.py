from django.core.management.base import BaseCommand
from backend.models import HospitalCapacity

class Command(BaseCommand):
    help = 'Initialize hospital capacity data for Makueni County Referral Hospital'

    def handle(self, *args, **options):
        departments = [
            {
                'department': 'Emergency',
                'total_beds': 20,
                'occupied_beds': 0,
                'available_doctors': 5
            },
            {
                'department': 'General Medicine',
                'total_beds': 50,
                'occupied_beds': 0,
                'available_doctors': 8
            },
            {
                'department': 'Pediatrics',
                'total_beds': 30,
                'occupied_beds': 0,
                'available_doctors': 4
            },
            {
                'department': 'Surgery',
                'total_beds': 40,
                'occupied_beds': 0,
                'available_doctors': 6
            },
            {
                'department': 'Maternity',
                'total_beds': 35,
                'occupied_beds': 0,
                'available_doctors': 5
            },
            {
                'department': 'ICU',
                'total_beds': 15,
                'occupied_beds': 0,
                'available_doctors': 3
            }
        ]

        for dept_data in departments:
            HospitalCapacity.objects.get_or_create(
                department=dept_data['department'],
                defaults={
                    'total_beds': dept_data['total_beds'],
                    'occupied_beds': dept_data['occupied_beds'],
                    'available_doctors': dept_data['available_doctors']
                }
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully initialized hospital capacity data')
        ) 
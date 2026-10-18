from django.core.management.base import BaseCommand
from django.test import Client
import json

class Command(BaseCommand):
    help = 'Test all fixed API endpoints'

    def handle(self, *args, **options):
        client = Client()
        
        tests = [
            {
                'method': 'GET',
                'url': '/api/doctor/dashboard/',
                'name': 'Doctor Dashboard'
            },
            {
                'method': 'POST',
                'url': '/api/emergency/update-status/',
                'data': {'alert_id': 1, 'status': 'in_progress'},
                'name': 'Emergency Status Update'
            },
            {
                'method': 'POST',
                'url': '/api/hospital/capacity/update/',
                'data': {
                    'department': 'Test Ward',
                    'total_beds': 30,
                    'occupied_beds': 20,
                    'available_doctors': 5
                },
                'name': 'Hospital Capacity Update'
            },
            {
                'method': 'POST',
                'url': '/api/symptoms/analyze/',
                'data': {
                    'symptoms': 'fever and headache',
                    'language': 'english'
                },
                'name': 'Symptom Analysis'
            },
            {
                'method': 'POST',
                'url': '/api/sms/webhook/',
                'data': {
                    'from': '+1234567890',
                    'text': 'I have fever'
                },
                'name': 'SMS Webhook'
            },
            {
                'method': 'POST',
                'url': '/api/voice/webhook/',
                'data': {
                    'from': '+1234567890',
                    'transcript': 'I feel sick',
                    'language': 'english'
                },
                'name': 'Voice Webhook'
            }
        ]
        
        passed = 0
        total = len(tests)
        
        self.stdout.write("Testing API Endpoints...")
        self.stdout.write("=" * 50)
        
        for test in tests:
            try:
                if test['method'] == 'GET':
                    response = client.get(test['url'])
                else:
                    response = client.post(
                        test['url'],
                        data=json.dumps(test.get('data', {})),
                        content_type='application/json'
                    )
                
                if response.status_code in [200, 201]:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ {test['name']} - Status: {response.status_code}")
                    )
                    passed += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ {test['name']} - Status: {response.status_code}")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ {test['name']} - Error: {str(e)}")
                )
        
        self.stdout.write("=" * 50)
        self.stdout.write(f"Results: {passed}/{total} APIs working")
        
        if passed == total:
            self.stdout.write(
                self.style.SUCCESS("🎉 All APIs are working correctly!")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"⚠️ {total - passed} APIs need attention")
            )

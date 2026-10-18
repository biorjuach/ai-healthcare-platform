#!/usr/bin/env python3
"""
Enhanced API Testing Script for AI Healthcare Platform
This script tests all available API endpoints with proper authentication handling.
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your server URL
TIMEOUT = 10  # Request timeout in seconds

# Test credentials (from add_test_data.py)
TEST_CREDENTIALS = {
    "patient": {
        "username": "patient1",
        "password": "testpass123"
    },
    "doctor": {
        "username": "testdoctor", 
        "password": "testpass123"
    }
}

# Test data for POST requests
TEST_DATA = {
    "sms_webhook": {
        "from": "+254712345678",
        "text": "I have a headache and fever"
    },
    "voice_webhook": {
        "from": "+254712345678",
        "transcript": "I am experiencing chest pain and shortness of breath",
        "language": "english"
    },
    "analyze_symptoms": {
        "symptoms": ["headache", "fever", "fatigue"],
        "patient_id": 1,
        "severity": "moderate"
    },
    "submit_symptom_report": {
        "patient_id": 1,
        "symptoms": ["cough", "fever", "body aches"],
        "severity": "mild",
        "duration": "3 days",
        "additional_notes": "Started after exposure to sick family member"
    },
    "update_emergency_status": {
        "alert_id": 1,
        "status": "resolved",
        "notes": "Patient stabilized and transferred to ward"
    },
    "update_capacity": {
        "ward": "emergency",
        "available_beds": 5,
        "total_beds": 20,
        "status": "normal"
    }
}

class AuthenticatedAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.results = []
        self.patient_session = requests.Session()
        self.doctor_session = requests.Session()
        self.anonymous_session = requests.Session()
        
    def login_user(self, session, username, password):
        """Login a user and get session cookies"""
        try:
            # First, get the login page to get CSRF token
            login_page = session.get(f"{self.base_url}/admin/login/", timeout=TIMEOUT)
            
            # For Django admin login
            login_data = {
                'username': username,
                'password': password,
                'next': '/admin/'
            }
            
            response = session.post(
                f"{self.base_url}/admin/login/",
                data=login_data,
                timeout=TIMEOUT
            )
            
            # Check if login was successful
            if response.status_code == 200 and 'error' not in response.text.lower():
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False
    
    def test_endpoint(self, method, endpoint, data=None, expected_status=200, session_type="anonymous"):
        """Test a single endpoint with appropriate session"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        # Choose the appropriate session
        if session_type == "patient":
            session = self.patient_session
        elif session_type == "doctor":
            session = self.doctor_session
        else:
            session = self.anonymous_session
        
        try:
            if method.upper() == "GET":
                response = session.get(url, timeout=TIMEOUT)
            elif method.upper() == "POST":
                headers = {'Content-Type': 'application/json'}
                response = session.post(url, json=data, headers=headers, timeout=TIMEOUT)
            else:
                return {
                    'endpoint': endpoint,
                    'method': method,
                    'status': 'ERROR',
                    'message': f'Unsupported method: {method}',
                    'response_time': 0,
                    'session_type': session_type
                }
            
            response_time = time.time() - start_time
            
            # Check if response is JSON
            try:
                response_data = response.json()
                response_text = json.dumps(response_data, indent=2)
            except:
                response_text = response.text[:500]  # Limit text response
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'status': 'SUCCESS' if response.status_code == expected_status else 'FAILED',
                'status_code': response.status_code,
                'expected_status': expected_status,
                'response_time': round(response_time, 3),
                'response': response_text[:1000],  # Limit response size
                'url': url,
                'session_type': session_type
            }
            
        except requests.exceptions.ConnectionError:
            result = {
                'endpoint': endpoint,
                'method': method,
                'status': 'ERROR',
                'message': 'Connection refused - Is the server running?',
                'response_time': 0,
                'url': url,
                'session_type': session_type
            }
        except requests.exceptions.Timeout:
            result = {
                'endpoint': endpoint,
                'method': method,
                'status': 'ERROR',
                'message': 'Request timeout',
                'response_time': 0,
                'url': url,
                'session_type': session_type
            }
        except Exception as e:
            result = {
                'endpoint': endpoint,
                'method': method,
                'status': 'ERROR',
                'message': str(e),
                'response_time': 0,
                'url': url,
                'session_type': session_type
            }
        
        self.results.append(result)
        return result
    
    def setup_authentication(self):
        """Setup authentication for patient and doctor sessions"""
        print("🔐 Setting up authentication...")
        
        # Login as patient
        patient_login = self.login_user(
            self.patient_session, 
            TEST_CREDENTIALS["patient"]["username"],
            TEST_CREDENTIALS["patient"]["password"]
        )
        
        # Login as doctor
        doctor_login = self.login_user(
            self.doctor_session,
            TEST_CREDENTIALS["doctor"]["username"], 
            TEST_CREDENTIALS["doctor"]["password"]
        )
        
        if patient_login:
            print("✅ Patient authentication successful")
        else:
            print("❌ Patient authentication failed")
            
        if doctor_login:
            print("✅ Doctor authentication successful")
        else:
            print("❌ Doctor authentication failed")
            
        return patient_login, doctor_login
    
    def run_all_tests(self):
        """Run tests for all endpoints"""
        print("🚀 Starting Enhanced API Tests...")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Setup authentication first
        patient_auth, doctor_auth = self.setup_authentication()
        
        # Define all endpoints to test with their authentication requirements
        endpoints = [
            # Communication APIs (no auth required)
            ("POST", "/api/sms/webhook/", TEST_DATA["sms_webhook"], "anonymous"),
            ("POST", "/api/voice/webhook/", TEST_DATA["voice_webhook"], "anonymous"),
            
            # Symptom Analysis APIs (no auth required)
            ("POST", "/api/symptoms/analyze/", TEST_DATA["analyze_symptoms"], "anonymous"),
            ("POST", "/api/symptoms/submit/", TEST_DATA["submit_symptom_report"], "anonymous"),
            
            # Patient Management APIs (require patient auth)
            ("GET", "/api/patient/dashboard/", None, "patient"),
            ("GET", "/api/patient/symptoms/", None, "patient"),
            ("GET", "/api/patient/appointments/", None, "patient"),
            
            # Doctor Management APIs (require doctor auth)
            ("GET", "/api/doctor/dashboard/", None, "doctor"),
            
            # Emergency Management APIs (no auth required)
            ("GET", "/api/emergency/alerts/", None, "anonymous"),
            ("POST", "/api/emergency/update-status/", TEST_DATA["update_emergency_status"], "anonymous"),
            
            # Hospital Management APIs (no auth required)
            ("GET", "/api/hospital/capacity/", None, "anonymous"),
            ("POST", "/api/hospital/capacity/update/", TEST_DATA["update_capacity"], "anonymous"),
            
            # Analytics APIs (no auth required)
            ("GET", "/api/analytics/dashboard/", None, "anonymous"),
            ("GET", "/api/analytics/symptoms/", None, "anonymous"),
            
            # System APIs (no auth required)
            ("GET", "/api/health/", None, "anonymous"),
            ("GET", "/admin/", None, "anonymous"),
            ("GET", "/dashboard/", None, "anonymous"),
            
            # Patient list (no auth required)
            ("GET", "/api/patients/", None, "anonymous"),
        ]
        
        # Test each endpoint
        for i, (method, endpoint, data, session_type) in enumerate(endpoints, 1):
            print(f"Testing {i}/{len(endpoints)}: {method} {endpoint} ({session_type})")
            
            # Skip auth-required tests if authentication failed
            if session_type == "patient" and not patient_auth:
                print(f"  ⚠️  SKIPPED - Patient authentication failed")
                continue
            elif session_type == "doctor" and not doctor_auth:
                print(f"  ⚠️  SKIPPED - Doctor authentication failed")
                continue
            
            result = self.test_endpoint(method, endpoint, data, session_type=session_type)
            
            # Print immediate result
            if result['status'] == 'SUCCESS':
                print(f"  ✅ {result['status']} ({result['status_code']}) - {result['response_time']}s")
            elif result['status'] == 'FAILED':
                print(f"  ❌ {result['status']} ({result['status_code']}) - Expected {result['expected_status']}")
            else:
                print(f"  ⚠️  {result['status']}: {result.get('message', 'Unknown error')}")
        
        print("\n" + "=" * 60)
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.results)
        successful = len([r for r in self.results if r['status'] == 'SUCCESS'])
        failed = len([r for r in self.results if r['status'] == 'FAILED'])
        errors = len([r for r in self.results if r['status'] == 'ERROR'])
        
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Endpoints Tested: {total}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Errors: {errors}")
        if total > 0:
            print(f"Success Rate: {(successful/total)*100:.1f}%")
        
        # Show failed tests
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAILED':
                    print(f"  {result['method']} {result['endpoint']} ({result['session_type']}) - Got {result['status_code']}, Expected {result['expected_status']}")
        
        # Show errors
        if errors > 0:
            print("\n⚠️  ERRORS:")
            for result in self.results:
                if result['status'] == 'ERROR':
                    print(f"  {result['method']} {result['endpoint']} ({result['session_type']}) - {result.get('message', 'Unknown error')}")
        
        # Show successful tests
        if successful > 0:
            print(f"\n✅ WORKING APIs ({successful}):")
            for result in self.results:
                if result['status'] == 'SUCCESS':
                    print(f"  {result['method']} {result['endpoint']} ({result['session_type']}) - {result['response_time']}s")
    
    def save_results(self, filename=None):
        """Save test results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'base_url': self.base_url,
                'results': self.results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main function"""
    print("🏥 AI Healthcare Platform - Enhanced API Testing Tool")
    print("=" * 60)
    
    # Check if server URL is provided as argument
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL
        print(f"Using default URL: {base_url}")
        print("To use a different URL: python test_apis_with_auth.py <your-server-url>")
    
    # Create tester and run tests
    tester = AuthenticatedAPITester(base_url)
    tester.run_all_tests()
    
    # Save results
    tester.save_results()
    
    print("\n🎯 Next Steps:")
    print("1. Check the detailed results in the saved JSON file")
    print("2. For failed tests, check server logs for more details")
    print("3. Ensure test data exists: cd backend && python manage.py add_test_data")
    print("4. For auth issues, verify test users exist in the database")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Comprehensive API Testing Script for AI Healthcare Platform
This script tests all available API endpoints and provides detailed status reports.
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your server URL
TIMEOUT = 10  # Request timeout in seconds

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

class APITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.results = []
        self.session = requests.Session()
        
    def test_endpoint(self, method, endpoint, data=None, expected_status=200):
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, timeout=TIMEOUT)
            elif method.upper() == "POST":
                headers = {'Content-Type': 'application/json'}
                response = self.session.post(url, json=data, headers=headers, timeout=TIMEOUT)
            else:
                return {
                    'endpoint': endpoint,
                    'method': method,
                    'status': 'ERROR',
                    'message': f'Unsupported method: {method}',
                    'response_time': 0
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
                'url': url
            }
            
        except requests.exceptions.ConnectionError:
            result = {
                'endpoint': endpoint,
                'method': method,
                'status': 'ERROR',
                'message': 'Connection refused - Is the server running?',
                'response_time': 0,
                'url': url
            }
        except requests.exceptions.Timeout:
            result = {
                'endpoint': endpoint,
                'method': method,
                'status': 'ERROR',
                'message': 'Request timeout',
                'response_time': 0,
                'url': url
            }
        except Exception as e:
            result = {
                'endpoint': endpoint,
                'method': method,
                'status': 'ERROR',
                'message': str(e),
                'response_time': 0,
                'url': url
            }
        
        self.results.append(result)
        return result
    
    def run_all_tests(self):
        """Run tests for all endpoints"""
        print("🚀 Starting API Tests...")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Define all endpoints to test
        endpoints = [
            # Communication APIs
            ("POST", "/api/sms/webhook/", TEST_DATA["sms_webhook"]),
            ("POST", "/api/voice/webhook/", TEST_DATA["voice_webhook"]),
            
            # Symptom Analysis APIs
            ("POST", "/api/symptoms/analyze/", TEST_DATA["analyze_symptoms"]),
            ("POST", "/api/symptoms/submit/", TEST_DATA["submit_symptom_report"]),
            
            # Patient Management APIs (GET requests)
            ("GET", "/api/patient/dashboard/"),
            ("GET", "/api/patient/symptoms/"),
            ("GET", "/api/patient/appointments/"),
            ("GET", "/api/patients/"),
            
            # Doctor Management APIs
            ("GET", "/api/doctor/dashboard/"),
            
            # Emergency Management APIs
            ("GET", "/api/emergency/alerts/"),
            ("POST", "/api/emergency/update-status/", TEST_DATA["update_emergency_status"]),
            
            # Hospital Management APIs
            ("GET", "/api/hospital/capacity/"),
            ("POST", "/api/hospital/capacity/update/", TEST_DATA["update_capacity"]),
            
            # Analytics APIs
            ("GET", "/api/analytics/dashboard/"),
            ("GET", "/api/analytics/symptoms/"),
            
            # System APIs
            ("GET", "/api/health/"),
            ("GET", "/admin/"),
            ("GET", "/dashboard/"),
        ]
        
        # Test each endpoint
        for i, (method, endpoint, *args) in enumerate(endpoints, 1):
            data = args[0] if args else None
            print(f"Testing {i}/{len(endpoints)}: {method} {endpoint}")
            
            result = self.test_endpoint(method, endpoint, data)
            
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
        print(f"Success Rate: {(successful/total)*100:.1f}%")
        
        # Show failed tests
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAILED':
                    print(f"  {result['method']} {result['endpoint']} - Got {result['status_code']}, Expected {result['expected_status']}")
        
        # Show errors
        if errors > 0:
            print("\n⚠️  ERRORS:")
            for result in self.results:
                if result['status'] == 'ERROR':
                    print(f"  {result['method']} {result['endpoint']} - {result.get('message', 'Unknown error')}")
        
        # Show successful tests
        if successful > 0:
            print(f"\n✅ WORKING APIs ({successful}):")
            for result in self.results:
                if result['status'] == 'SUCCESS':
                    print(f"  {result['method']} {result['endpoint']} ({result['response_time']}s)")
    
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
    print("🏥 AI Healthcare Platform - API Testing Tool")
    print("=" * 60)
    
    # Check if server URL is provided as argument
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL
        print(f"Using default URL: {base_url}")
        print("To use a different URL: python test_apis.py <your-server-url>")
    
    # Create tester and run tests
    tester = APITester(base_url)
    tester.run_all_tests()
    
    # Save results
    tester.save_results()
    
    print("\n🎯 Next Steps:")
    print("1. Check the detailed results in the saved JSON file")
    print("2. For failed tests, check server logs for more details")
    print("3. Ensure test data exists in the database")
    print("4. Verify authentication requirements for protected endpoints")

if __name__ == "__main__":
    main()

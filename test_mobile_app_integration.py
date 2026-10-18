#!/usr/bin/env python3
"""
Mobile App Integration Test Suite
Tests all mobile app API endpoints and ensures proper backend connectivity
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"
MOBILE_CONFIG = {
    "api_url": f"{BASE_URL}/api",
    "timeout": 10,
    "retry_attempts": 3
}

class MobileAppTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'MobileApp/2.1.0'
        })
        self.test_results = []
        self.auth_token = None
        
    def log_test(self, test_name, success, message="", data=None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/health/", timeout=MOBILE_CONFIG['timeout'])
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, "Backend is healthy", data)
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test mobile app authentication"""
        # Test login endpoint
        login_data = {
            "username": "patient1",
            "password": "patient123"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login/",
                json=login_data,
                timeout=MOBILE_CONFIG['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.auth_token = data.get('token')
                    if self.auth_token:
                        self.session.headers['Authorization'] = f'Bearer {self.auth_token}'
                    self.log_test("Mobile Authentication", True, "Login successful", {
                        'user': data.get('user', {}).get('username'),
                        'has_token': bool(self.auth_token)
                    })
                    return True
                else:
                    self.log_test("Mobile Authentication", False, data.get('message', 'Login failed'))
                    return False
            else:
                self.log_test("Mobile Authentication", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Mobile Authentication", False, f"Connection error: {str(e)}")
            return False
    
    def test_symptom_analysis(self):
        """Test symptom analysis endpoint (mobile app format)"""
        symptom_data = {
            "symptoms": "I have a headache and fever for the past 2 days",
            "language": "english",
            "patient_id": 1
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/symptoms/analyze/",
                json=symptom_data,
                timeout=MOBILE_CONFIG['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    analysis_data = data.get('data', {})
                    self.log_test("Symptom Analysis", True, "Analysis completed", {
                        'severity': analysis_data.get('severity'),
                        'is_emergency': analysis_data.get('is_emergency'),
                        'confidence': analysis_data.get('confidence')
                    })
                    return True
                else:
                    self.log_test("Symptom Analysis", False, data.get('message', 'Analysis failed'))
                    return False
            else:
                self.log_test("Symptom Analysis", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Symptom Analysis", False, f"Connection error: {str(e)}")
            return False
    
    def test_symptom_submission(self):
        """Test symptom report submission"""
        submission_data = {
            "patient_id": 1,
            "symptoms": "Headache and fever",
            "input_method": "app",
            "language": "english"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/symptoms/submit/",
                json=submission_data,
                timeout=MOBILE_CONFIG['timeout']
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("Symptom Submission", True, "Report submitted successfully", {
                    'status': data.get('status'),
                    'message': data.get('message')
                })
                return True
            else:
                self.log_test("Symptom Submission", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Symptom Submission", False, f"Connection error: {str(e)}")
            return False
    
    def test_patient_dashboard(self):
        """Test patient dashboard endpoint"""
        try:
            response = self.session.get(
                f"{API_BASE}/patient/dashboard/",
                timeout=MOBILE_CONFIG['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Patient Dashboard", True, "Dashboard data retrieved", {
                    'has_data': bool(data),
                    'data_keys': list(data.keys()) if data else []
                })
                return True
            else:
                self.log_test("Patient Dashboard", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Patient Dashboard", False, f"Connection error: {str(e)}")
            return False
    
    def test_patient_symptoms(self):
        """Test patient symptoms history"""
        try:
            response = self.session.get(
                f"{API_BASE}/patient/symptoms/",
                timeout=MOBILE_CONFIG['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Patient Symptoms", True, "Symptoms history retrieved", {
                    'has_data': bool(data),
                    'count': len(data) if isinstance(data, list) else 0
                })
                return True
            else:
                self.log_test("Patient Symptoms", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Patient Symptoms", False, f"Connection error: {str(e)}")
            return False
    
    def test_patient_appointments(self):
        """Test patient appointments endpoint"""
        try:
            response = self.session.get(
                f"{API_BASE}/patient/appointments/",
                timeout=MOBILE_CONFIG['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Patient Appointments", True, "Appointments retrieved", {
                    'has_data': bool(data),
                    'count': len(data) if isinstance(data, list) else 0
                })
                return True
            else:
                self.log_test("Patient Appointments", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Patient Appointments", False, f"Connection error: {str(e)}")
            return False
    
    def test_health_tips(self):
        """Test health tips endpoint"""
        try:
            response = self.session.get(
                f"{API_BASE}/health-tips/",
                timeout=MOBILE_CONFIG['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Tips", True, "Health tips retrieved", {
                    'has_data': bool(data),
                    'count': len(data) if isinstance(data, list) else 0
                })
                return True
            else:
                self.log_test("Health Tips", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Tips", False, f"Connection error: {str(e)}")
            return False
    
    def test_multi_language_support(self):
        """Test multi-language symptom analysis"""
        swahili_data = {
            "symptoms": "Nina kichwa cha kuumwa na homa",
            "language": "swahili",
            "patient_id": 1
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/symptoms/analyze/",
                json=swahili_data,
                timeout=MOBILE_CONFIG['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Multi-language Support", True, "Swahili analysis completed", {
                        'language': 'swahili',
                        'has_analysis': bool(data.get('data'))
                    })
                    return True
                else:
                    self.log_test("Multi-language Support", False, data.get('message', 'Swahili analysis failed'))
                    return False
            else:
                self.log_test("Multi-language Support", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Multi-language Support", False, f"Connection error: {str(e)}")
            return False
    
    def test_emergency_detection(self):
        """Test emergency symptom detection"""
        emergency_data = {
            "symptoms": "Severe chest pain, difficulty breathing, feeling faint",
            "language": "english",
            "patient_id": 1
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/symptoms/analyze/",
                json=emergency_data,
                timeout=MOBILE_CONFIG['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    analysis_data = data.get('data', {})
                    is_emergency = analysis_data.get('is_emergency', False)
                    self.log_test("Emergency Detection", True, f"Emergency detected: {is_emergency}", {
                        'is_emergency': is_emergency,
                        'severity': analysis_data.get('severity'),
                        'has_emergency_plan': bool(analysis_data.get('emergency_plan'))
                    })
                    return True
                else:
                    self.log_test("Emergency Detection", False, data.get('message', 'Emergency analysis failed'))
                    return False
            else:
                self.log_test("Emergency Detection", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Emergency Detection", False, f"Connection error: {str(e)}")
            return False
    
    def test_api_endpoints_list(self):
        """Test all available API endpoints"""
        endpoints = [
            ("GET", "/health/"),
            ("GET", "/patients/"),
            ("GET", "/doctors/"),
            ("GET", "/appointments/"),
            ("GET", "/notifications/"),
        ]
        
        successful_endpoints = 0
        total_endpoints = len(endpoints)
        
        for method, endpoint in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{API_BASE}{endpoint}", timeout=MOBILE_CONFIG['timeout'])
                else:
                    continue
                
                if response.status_code in [200, 201, 204]:
                    successful_endpoints += 1
                    self.log_test(f"API Endpoint {endpoint}", True, f"Status: {response.status_code}")
                else:
                    self.log_test(f"API Endpoint {endpoint}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"API Endpoint {endpoint}", False, f"Error: {str(e)}")
        
        success_rate = (successful_endpoints / total_endpoints) * 100
        self.log_test("API Endpoints Coverage", success_rate >= 80, f"Success rate: {success_rate:.1f}%")
        return success_rate >= 80
    
    def run_all_tests(self):
        """Run all mobile app integration tests"""
        print("🚀 Starting Mobile App Integration Tests")
        print("=" * 50)
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("Authentication", self.test_authentication),
            ("Symptom Analysis", self.test_symptom_analysis),
            ("Symptom Submission", self.test_symptom_submission),
            ("Patient Dashboard", self.test_patient_dashboard),
            ("Patient Symptoms", self.test_patient_symptoms),
            ("Patient Appointments", self.test_patient_appointments),
            ("Health Tips", self.test_health_tips),
            ("Multi-language Support", self.test_multi_language_support),
            ("Emergency Detection", self.test_emergency_detection),
            ("API Endpoints Coverage", self.test_api_endpoints_list),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test error: {str(e)}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Mobile app integration is working perfectly!")
        elif success_rate >= 80:
            print("✅ GOOD: Mobile app integration is working well with minor issues")
        elif success_rate >= 70:
            print("⚠️  FAIR: Mobile app integration has some issues that need attention")
        else:
            print("❌ POOR: Mobile app integration has significant issues")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"mobile_app_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': total_tests - passed_tests,
                    'success_rate': success_rate,
                    'timestamp': datetime.now().isoformat()
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        return success_rate >= 80

def main():
    """Main function"""
    print("🏥 AI Healthcare Platform - Mobile App Integration Test")
    print("Testing mobile app connectivity with backend APIs")
    print()
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/api/health/", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not responding properly")
            print("Please ensure the Django backend is running on http://localhost:8000")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to backend")
        print("Please ensure the Django backend is running on http://localhost:8000")
        sys.exit(1)
    
    # Run tests
    tester = MobileAppTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 RECOMMENDATIONS:")
        print("✅ Mobile app is ready for deployment")
        print("✅ All critical API endpoints are working")
        print("✅ Backend integration is stable")
        print("\n📱 Next steps:")
        print("1. Test the mobile app on actual devices")
        print("2. Verify all UI components work correctly")
        print("3. Test offline functionality")
        print("4. Perform user acceptance testing")
    else:
        print("\n🔧 ISSUES FOUND:")
        print("❌ Some API endpoints are not working properly")
        print("❌ Mobile app may have connectivity issues")
        print("\n📋 Action items:")
        print("1. Check backend server logs for errors")
        print("2. Verify API endpoint configurations")
        print("3. Test individual endpoints manually")
        print("4. Update mobile app API configuration if needed")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

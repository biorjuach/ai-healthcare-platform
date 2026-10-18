#!/usr/bin/env python3
"""
Test all API endpoints to check for 405 Method Not Allowed errors
"""
import requests
import json
import time

def test_all_endpoints():
    base_url = 'http://localhost:8000'
    
    # Define all endpoints with their expected methods
    endpoints = [
        # Communication
        {'url': '/api/sms/webhook/', 'method': 'POST', 'data': {'from': '+254712345678', 'text': 'test'}, 'category': 'Communication'},
        {'url': '/api/voice/webhook/', 'method': 'POST', 'data': {'from': '+254712345678', 'text': 'test'}, 'category': 'Communication'},
        
        # Symptom Analysis
        {'url': '/api/symptoms/analyze/', 'method': 'POST', 'data': {'symptoms': 'headache', 'language': 'en'}, 'category': 'Symptom Analysis'},
        {'url': '/api/symptoms/submit/', 'method': 'POST', 'data': {'symptoms': 'headache', 'language': 'en'}, 'category': 'Symptom Analysis'},
        
        # Patient Management
        {'url': '/api/patient/dashboard/', 'method': 'GET', 'category': 'Patient'},
        {'url': '/api/patient/symptoms/', 'method': 'GET', 'category': 'Patient'},
        {'url': '/api/patient/appointments/', 'method': 'GET', 'category': 'Patient'},
        {'url': '/api/patients/', 'method': 'GET', 'category': 'Patient'},
        
        # Doctor Management
        {'url': '/api/doctor/dashboard/', 'method': 'GET', 'category': 'Doctor'},
        {'url': '/api/doctors/', 'method': 'GET', 'category': 'Doctor'},
        
        # Emergency
        {'url': '/api/emergency/alerts/', 'method': 'GET', 'category': 'Emergency'},
        {'url': '/api/emergency/update-status/', 'method': 'POST', 'data': {'alert_id': 1, 'status': 'resolved'}, 'category': 'Emergency'},
        
        # Hospital
        {'url': '/api/hospital/capacity/', 'method': 'GET', 'category': 'Hospital'},
        {'url': '/api/hospital/capacity/update/', 'method': 'POST', 'data': {'total_beds': 100}, 'category': 'Hospital'},
        
        # Analytics
        {'url': '/api/analytics/dashboard/', 'method': 'GET', 'category': 'Analytics'},
        {'url': '/api/analytics/symptoms/', 'method': 'GET', 'category': 'Analytics'},
        
        # System
        {'url': '/api/health/', 'method': 'GET', 'category': 'System'},
        {'url': '/api/health-tips/', 'method': 'GET', 'category': 'System'},
        
        # Authentication
        {'url': '/api/auth/login/', 'method': 'POST', 'data': {'username': 'test', 'password': 'test'}, 'category': 'Auth'},
        {'url': '/api/auth/register/', 'method': 'POST', 'data': {'username': 'test', 'password': 'test'}, 'category': 'Auth'},
        {'url': '/api/auth/profile/', 'method': 'GET', 'category': 'Auth'},
        {'url': '/api/auth/logout/', 'method': 'POST', 'category': 'Auth'},
        
        # Notifications
        {'url': '/api/notifications/', 'method': 'GET', 'category': 'Notifications'},
        
        # Appointments
        {'url': '/api/appointments/', 'method': 'GET', 'category': 'Appointments'},
    ]
    
    print("🧪 Testing All API Endpoints")
    print("=" * 80)
    
    results = {'working': [], 'method_errors': [], 'other_errors': []}
    
    for endpoint in endpoints:
        url = base_url + endpoint['url']
        method = endpoint['method']
        data = endpoint.get('data', {})
        category = endpoint['category']
        
        try:
            print(f"\n📊 Testing: {method} {endpoint['url']} [{category}]")
            
            if method == 'GET':
                response = requests.get(url, timeout=5)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=5)
            elif method == 'PUT':
                response = requests.put(url, json=data, timeout=5)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=5)
            
            status = response.status_code
            
            if status == 405:
                print(f"   ❌ 405 METHOD NOT ALLOWED")
                results['method_errors'].append({
                    'url': endpoint['url'],
                    'method': method,
                    'category': category,
                    'error': '405 Method Not Allowed'
                })
            elif status in [200, 201, 302, 400, 401, 403, 404]:  # Expected responses
                print(f"   ✅ {status} - Endpoint accessible")
                results['working'].append({
                    'url': endpoint['url'],
                    'method': method,
                    'category': category,
                    'status': status
                })
            else:
                print(f"   ⚠️ {status} - Unexpected status")
                results['other_errors'].append({
                    'url': endpoint['url'],
                    'method': method,
                    'category': category,
                    'status': status
                })
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ CONNECTION FAILED - Server not running?")
            results['other_errors'].append({
                'url': endpoint['url'],
                'method': method,
                'category': category,
                'error': 'Connection Failed'
            })
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results['other_errors'].append({
                'url': endpoint['url'],
                'method': method,
                'category': category,
                'error': str(e)
            })
        
        time.sleep(0.1)  # Small delay to avoid overwhelming server
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY RESULTS")
    print("=" * 80)
    
    print(f"\n✅ WORKING ENDPOINTS ({len(results['working'])})")
    for item in results['working']:
        print(f"   {item['method']} {item['url']} - {item['status']} [{item['category']}]")
    
    if results['method_errors']:
        print(f"\n❌ 405 METHOD NOT ALLOWED ({len(results['method_errors'])})")
        for item in results['method_errors']:
            print(f"   {item['method']} {item['url']} - {item['error']} [{item['category']}]")
    
    if results['other_errors']:
        print(f"\n⚠️ OTHER ISSUES ({len(results['other_errors'])})")
        for item in results['other_errors']:
            error = item.get('error', f"Status {item.get('status', 'Unknown')}")
            print(f"   {item['method']} {item['url']} - {error} [{item['category']}]")
    
    print(f"\n🎯 TOTAL TESTED: {len(endpoints)} endpoints")
    print(f"✅ Working: {len(results['working'])}")
    print(f"❌ Method Errors: {len(results['method_errors'])}")
    print(f"⚠️ Other Issues: {len(results['other_errors'])}")

if __name__ == '__main__':
    test_all_endpoints()

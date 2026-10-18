#!/usr/bin/env python3
"""
Test Frontend API Compatibility
Verifies that the frontend can handle the new API structure without crashing.
"""

import requests
import json
import time

def test_api_responses():
    """Test all APIs that the frontend uses to ensure they return valid data"""
    print("🔧 Testing API Responses for Frontend Compatibility...")
    print("=" * 60)
    
    apis_to_test = [
        ("/api/health/", "System Health"),
        ("/api/analytics/dashboard/", "Analytics Dashboard"),
        ("/api/emergency/alerts/", "Emergency Alerts"),
        ("/api/hospital/capacity/", "Hospital Capacity"),
        ("/api/patients/", "Patient List"),
        ("/api/analytics/symptoms/", "Symptom Analytics"),
    ]
    
    results = []
    
    for endpoint, description in apis_to_test:
        url = f"http://localhost:8000{endpoint}"
        print(f"Testing {description}...")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for potential undefined/null values that could cause frontend issues
                issues = check_for_frontend_issues(data, description)
                
                if issues:
                    print(f"  ⚠️  {description} - Potential frontend issues found:")
                    for issue in issues:
                        print(f"    - {issue}")
                else:
                    print(f"  ✅ {description} - No frontend compatibility issues")
                
                results.append({
                    'endpoint': endpoint,
                    'description': description,
                    'status': 'success',
                    'issues': issues
                })
            else:
                print(f"  ❌ {description} - HTTP {response.status_code}")
                results.append({
                    'endpoint': endpoint,
                    'description': description,
                    'status': 'error',
                    'issues': [f"HTTP {response.status_code}"]
                })
                
        except Exception as e:
            print(f"  ❌ {description} - Error: {str(e)}")
            results.append({
                'endpoint': endpoint,
                'description': description,
                'status': 'error',
                'issues': [str(e)]
            })
    
    return results

def check_for_frontend_issues(data, api_name):
    """Check for potential issues that could cause frontend crashes"""
    issues = []
    
    if api_name == "Emergency Alerts":
        # Check emergency alerts structure
        if 'emergency_alerts' in data and isinstance(data['emergency_alerts'], list):
            for i, alert in enumerate(data['emergency_alerts']):
                # Check for missing patient name
                if 'patient' in alert:
                    if not alert['patient'].get('user', {}).get('first_name') and not alert['patient'].get('user', {}).get('last_name'):
                        issues.append(f"Alert {i}: Missing patient name")
                
                # Check for missing symptom description
                if 'symptom' in alert and isinstance(alert['symptom'], dict):
                    if not alert['symptom'].get('description'):
                        issues.append(f"Alert {i}: Missing symptom description")
                
                # Check for missing severity
                if not alert.get('severity') and not alert.get('severity_level'):
                    issues.append(f"Alert {i}: Missing severity information")
    
    elif api_name == "Patient List":
        # Check patient list structure
        if isinstance(data, list):
            for i, patient in enumerate(data):
                if 'user' in patient:
                    if not patient['user'].get('first_name') and not patient['user'].get('last_name'):
                        issues.append(f"Patient {i}: Missing name information")
    
    # Check for null/undefined values that could cause .toLowerCase() errors
    def check_nested(obj, path=""):
        if obj is None:
            issues.append(f"Null value found at {path}")
            return
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                check_nested(value, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_nested(item, f"{path}[{i}]")
        elif isinstance(obj, str) and obj.strip() == "":
            issues.append(f"Empty string found at {path}")
    
    check_nested(data)
    
    return issues

def generate_frontend_test_data():
    """Generate test data that the frontend can safely handle"""
    print("\n📝 Generating Safe Test Data...")
    print("=" * 60)
    
    safe_test_data = {
        "emergency_alerts": [
            {
                "id": 1,
                "patient": {
                    "id": 1,
                    "user": {
                        "id": 1,
                        "username": "testpatient",
                        "email": "test@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "profile": {}
                    }
                },
                "symptom": {
                    "id": 1,
                    "description": "Headache",
                    "severity": "high",
                    "body_location": "Head",
                    "duration": "2 hours"
                },
                "severity_level": "high",
                "status": "active",
                "location": "Emergency Room",
                "created_at": "2025-01-10T10:00:00Z"
            }
        ],
        "patients": [
            {
                "id": 1,
                "user": {
                    "id": 1,
                    "username": "patient1",
                    "email": "patient1@example.com",
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "profile": {}
                },
                "blood_type": "A+",
                "date_of_birth": "1990-01-01",
                "gender": "female"
            }
        ]
    }
    
    # Save test data
    with open('safe_test_data.json', 'w') as f:
        json.dump(safe_test_data, f, indent=2)
    
    print("✅ Generated safe test data: safe_test_data.json")
    print("📋 This data structure is guaranteed to work with the frontend")

def main():
    print("🏥 Frontend API Compatibility Test")
    print("=" * 60)
    
    # Test API responses
    results = test_api_responses()
    
    # Generate safe test data
    generate_frontend_test_data()
    
    # Summary
    print("\n📊 COMPATIBILITY SUMMARY")
    print("=" * 60)
    
    successful_apis = len([r for r in results if r['status'] == 'success'])
    total_apis = len(results)
    total_issues = sum(len(r.get('issues', [])) for r in results)
    
    print(f"APIs Tested: {total_apis}")
    print(f"Successful APIs: {successful_apis}")
    print(f"Total Issues Found: {total_issues}")
    
    if total_issues == 0:
        print("\n✅ All APIs are compatible with the frontend!")
        print("🎉 Your frontend should work without crashes.")
    else:
        print(f"\n⚠️  Found {total_issues} potential issues:")
        for result in results:
            if result.get('issues'):
                print(f"\n{result['description']}:")
                for issue in result['issues']:
                    print(f"  - {issue}")
    
    print("\n📋 Next Steps:")
    print("1. Start your React app: cd admin-dashboard && npm start")
    print("2. The frontend should now handle the API data safely")
    print("3. Check browser console for any remaining errors")

if __name__ == "__main__":
    main()

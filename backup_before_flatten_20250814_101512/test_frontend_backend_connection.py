#!/usr/bin/env python3
"""
Frontend-Backend Connection Test
Tests if the frontend can properly connect to and receive data from the backend APIs.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"  # React default port
TIMEOUT = 10

def test_backend_apis():
    """Test all backend APIs that the frontend might use"""
    print("🔧 Testing Backend APIs...")
    print("=" * 50)
    
    # APIs that the frontend typically uses
    apis_to_test = [
        ("GET", "/api/health/", "System Health"),
        ("GET", "/api/analytics/dashboard/", "Analytics Dashboard"),
        ("GET", "/api/emergency/alerts/", "Emergency Alerts"),
        ("GET", "/api/hospital/capacity/", "Hospital Capacity"),
        ("GET", "/api/patients/", "Patient List"),
        ("GET", "/api/analytics/symptoms/", "Symptom Analytics"),
    ]
    
    results = []
    
    for method, endpoint, description in apis_to_test:
        url = f"{BACKEND_URL}{endpoint}"
        print(f"Testing {description}...")
        
        try:
            start_time = time.time()
            response = requests.request(method, url, timeout=TIMEOUT)
            response_time = time.time() - start_time
            
            # Try to parse JSON response
            try:
                data = response.json()
                data_size = len(json.dumps(data))
                has_data = len(data) > 0 if isinstance(data, (dict, list)) else True
            except:
                data = response.text
                data_size = len(data)
                has_data = len(data) > 0
            
            result = {
                'endpoint': endpoint,
                'description': description,
                'status_code': response.status_code,
                'response_time': round(response_time, 3),
                'data_size': data_size,
                'has_data': has_data,
                'success': response.status_code == 200,
                'url': url
            }
            
            if result['success']:
                print(f"  ✅ {description} - {response.status_code} ({response_time:.3f}s) - Data: {data_size} chars")
            else:
                print(f"  ❌ {description} - {response.status_code} ({response_time:.3f}s)")
            
            results.append(result)
            
        except Exception as e:
            print(f"  ❌ {description} - Error: {str(e)}")
            results.append({
                'endpoint': endpoint,
                'description': description,
                'status_code': 0,
                'response_time': 0,
                'data_size': 0,
                'has_data': False,
                'success': False,
                'error': str(e),
                'url': url
            })
    
    return results

def test_frontend_connection():
    """Test if frontend is accessible"""
    print("\n🌐 Testing Frontend Connection...")
    print("=" * 50)
    
    try:
        response = requests.get(FRONTEND_URL, timeout=TIMEOUT)
        if response.status_code == 200:
            print(f"✅ Frontend is accessible at {FRONTEND_URL}")
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend is not accessible: {str(e)}")
        return False

def test_cors_configuration():
    """Test CORS configuration"""
    print("\n🔒 Testing CORS Configuration...")
    print("=" * 50)
    
    # Test a simple API call from frontend perspective
    headers = {
        'Origin': FRONTEND_URL,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/health/", headers=headers, timeout=TIMEOUT)
        
        # Check for CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        print("CORS Headers found:")
        for header, value in cors_headers.items():
            if value:
                print(f"  ✅ {header}: {value}")
            else:
                print(f"  ⚠️  {header}: Not set")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ CORS test failed: {str(e)}")
        return False

def generate_frontend_test_code(backend_results):
    """Generate test code for frontend to verify API calls"""
    print("\n📝 Generating Frontend Test Code...")
    print("=" * 50)
    
    working_apis = [r for r in backend_results if r['success']]
    
    if not working_apis:
        print("❌ No working APIs found for frontend testing")
        return
    
    print("✅ Working APIs for frontend:")
    for api in working_apis:
        print(f"  - {api['description']}: {api['endpoint']}")
    
    # Generate React test component
    test_code = f"""
// Frontend API Test Component
import React, {{ useState, useEffect }} from 'react';
import axios from 'axios';

const ApiTestComponent = () => {{
  const [results, setResults] = useState({{}});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const testApis = async () => {{
    setLoading(true);
    setError(null);
    const apiResults = {{}};

    const apis = [
      {{ name: 'Health Check', url: '/api/health/' }},
      {{ name: 'Analytics Dashboard', url: '/api/analytics/dashboard/' }},
      {{ name: 'Emergency Alerts', url: '/api/emergency/alerts/' }},
      {{ name: 'Hospital Capacity', url: '/api/hospital/capacity/' }},
      {{ name: 'Patient List', url: '/api/patients/' }},
    ];

    for (const api of apis) {{
      try {{
        const startTime = Date.now();
        const response = await axios.get(api.url);
        const responseTime = Date.now() - startTime;
        
        apiResults[api.name] = {{
          success: true,
          status: response.status,
          responseTime,
          dataSize: JSON.stringify(response.data).length,
          data: response.data
        }};
      }} catch (err) {{
        apiResults[api.name] = {{
          success: false,
          error: err.message,
          status: err.response?.status
        }};
      }}
    }}

    setResults(apiResults);
    setLoading(false);
  }};

  return (
    <div style={{ padding: '20px' }}>
      <h2>API Connection Test</h2>
      <button onClick={{testApis}} disabled={{loading}}>
        {{loading ? 'Testing...' : 'Test APIs'}}
      </button>
      
      {{Object.entries(results).map(([name, result]) => (
        <div key={{name}} style={{ margin: '10px 0', padding: '10px', border: '1px solid #ccc' }}>
          <h3>{{name}}</h3>
          {{result.success ? (
            <div style={{ color: 'green' }}>
              ✅ Success ({{result.status}}) - {{result.responseTime}}ms - {{result.dataSize}} chars
            </div>
          ) : (
            <div style={{ color: 'red' }}>
              ❌ Failed: {{result.error}} ({{result.status}})
            </div>
          )}}
        </div>
      )}}
    </div>
  );
}};

export default ApiTestComponent;
"""
    
    # Save the test component
    with open('frontend_api_test_component.jsx', 'w') as f:
        f.write(test_code)
    
    print("✅ Generated frontend test component: frontend_api_test_component.jsx")
    print("📋 Instructions:")
    print("1. Copy the component to your React app")
    print("2. Import and use it to test API connections")
    print("3. Check the browser console for detailed results")

def main():
    print("🏥 Frontend-Backend Connection Test")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print("=" * 60)
    
    # Test backend APIs
    backend_results = test_backend_apis()
    
    # Test frontend connection
    frontend_accessible = test_frontend_connection()
    
    # Test CORS
    cors_working = test_cors_configuration()
    
    # Generate frontend test code
    generate_frontend_test_code(backend_results)
    
    # Summary
    print("\n📊 CONNECTION SUMMARY")
    print("=" * 60)
    
    working_apis = len([r for r in backend_results if r['success']])
    total_apis = len(backend_results)
    
    print(f"Backend APIs: {working_apis}/{total_apis} working ({working_apis/total_apis*100:.1f}%)")
    print(f"Frontend Accessible: {'✅ Yes' if frontend_accessible else '❌ No'}")
    print(f"CORS Configured: {'✅ Yes' if cors_working else '❌ No'}")
    
    if working_apis > 0:
        print("\n✅ Your backend is ready for frontend integration!")
        print("📋 Next Steps:")
        print("1. Start your React app: cd admin-dashboard && npm start")
        print("2. Use the generated test component to verify API calls")
        print("3. Check browser network tab for API requests")
    else:
        print("\n❌ Backend APIs are not responding")
        print("📋 Troubleshooting:")
        print("1. Ensure Django server is running on port 8000")
        print("2. Check Django server logs for errors")
        print("3. Verify API endpoints are properly configured")

if __name__ == "__main__":
    main()

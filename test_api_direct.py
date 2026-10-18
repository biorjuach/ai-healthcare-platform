#!/usr/bin/env python3
"""
Test the symptom analysis API directly
"""
import requests
import json

def test_symptom_analysis():
    url = 'http://localhost:8000/api/symptoms/analyze/'
    
    test_data = {
        'symptoms': 'chest pain and difficulty breathing',
        'body_location': 'chest',
        'duration': '2 hours',
        'severity': 'high',
        'description': 'I have been experiencing chest pain and difficulty breathing for 2 hours',
        'language': 'en'
    }
    
    print(f"🧪 Testing API endpoint: {url}")
    print(f"📊 Test data: {test_data}")
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        
        print(f"\n📈 Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            
            if data.get('success') and 'data' in data:
                analysis = data['data']
                print(f"\n✅ Analysis Results:")
                print(f"   Severity: {analysis.get('severity')}")
                print(f"   Confidence: {analysis.get('confidence', 0)*100:.1f}%")
                print(f"   Emergency: {analysis.get('is_emergency')}")
                print(f"   Diagnosis: {analysis.get('diagnosis')}")
                print(f"   Disease Predictions: {analysis.get('disease_predictions')}")
            else:
                print(f"❌ API returned error: {data.get('message')}")
                print(f"   Full response: {data}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the Django server running?")
        print("   Start it with: python manage.py runserver")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_symptom_analysis()

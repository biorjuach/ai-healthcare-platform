#!/usr/bin/env python3
"""
Test login functionality for patients 1, 2, and 3
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def test_patient_login():
    """Test login for patients 1, 2, and 3"""
    
    print("🔍 Testing login for patients 1, 2, and 3...")
    print("=" * 50)
    
    # Test credentials - common passwords
    test_passwords = [
        'patient123',
        'password123', 
        '123456',
        'password',
        'test123',
        'demo123'
    ]
    
    for patient_num in [1, 2, 3]:
        username = f'patient{patient_num}'
        print(f"\n👤 Testing login for {username}:")
        
        # Check if user exists
        try:
            user = User.objects.get(username=username)
            print(f"   ✅ User exists: {user.username}")
            print(f"   📧 Email: {user.email}")
            print(f"   ✅ Active: {user.is_active}")
            
            # Test authentication with different passwords
            authenticated = False
            working_password = None
            
            for password in test_passwords:
                auth_user = authenticate(username=username, password=password)
                if auth_user is not None:
                    authenticated = True
                    working_password = password
                    break
            
            if authenticated:
                print(f"   ✅ Login successful with password: {working_password}")
            else:
                print(f"   ❌ Login failed with all test passwords")
                print(f"   🔍 Trying to check password hash...")
                
                # Check if password is set
                if user.password.startswith('pbkdf2_sha256$'):
                    print(f"   ✅ Password hash is set")
                else:
                    print(f"   ❌ No password hash found")
                    
        except User.DoesNotExist:
            print(f"   ❌ User {username} does not exist")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 RECOMMENDATIONS:")
    print("1. If passwords are not working, run: python set_user_passwords.py")
    print("2. Check if backend server is running on http://localhost:8000")
    print("3. Check frontend API configuration in web-app/src/services/api.ts")

if __name__ == "__main__":
    test_patient_login()

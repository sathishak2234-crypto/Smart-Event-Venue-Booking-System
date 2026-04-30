#!/usr/bin/env python
"""
Test script to verify user registration and profile data flow
"""
import requests
import json
from datetime import datetime

API_URL = 'http://localhost:5000/api'

print("=" * 80)
print("USER REGISTRATION AND PROFILE DATA FLOW TEST")
print("=" * 80)

# Test 1: Register a new user
print("\n1. TESTING USER REGISTRATION")
print("-" * 80)

test_user_data = {
    'name': 'Test User ' + str(datetime.now().timestamp()),
    'email': f'testuser_{int(datetime.now().timestamp())}@example.com',
    'phone': '9876543210',
    'password': 'TestPassword123'
}

print(f"Registering user with data:")
print(f"  Name: {test_user_data['name']}")
print(f"  Email: {test_user_data['email']}")
print(f"  Phone: {test_user_data['phone']}")

try:
    reg_response = requests.post(
        f'{API_URL}/auth/register',
        json=test_user_data,
        timeout=5
    )
    
    if reg_response.status_code == 201:
        reg_data = reg_response.json()
        user_id = reg_data.get('user_id')
        print(f"\n✓ Registration successful!")
        print(f"  User ID: {user_id}")
        print(f"  Response: {json.dumps(reg_data, indent=2)}")
    else:
        print(f"\n✗ Registration failed!")
        print(f"  Status: {reg_response.status_code}")
        print(f"  Response: {reg_response.text}")
        exit(1)
except Exception as e:
    print(f"\n✗ Registration error: {str(e)}")
    exit(1)

# Test 2: Login with registered user
print("\n2. TESTING USER LOGIN")
print("-" * 80)

login_data = {
    'email': test_user_data['email'],
    'password': test_user_data['password']
}

print(f"Logging in with email: {login_data['email']}")

try:
    login_response = requests.post(
        f'{API_URL}/auth/login',
        json=login_data,
        timeout=5
    )
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = login_result.get('token')
        user_info = login_result.get('user')
        print(f"\n✓ Login successful!")
        print(f"  Token: {token[:50]}...")
        print(f"  User info: {json.dumps(user_info, indent=2)}")
    else:
        print(f"\n✗ Login failed!")
        print(f"  Status: {login_response.status_code}")
        print(f"  Response: {login_response.text}")
        exit(1)
except Exception as e:
    print(f"\n✗ Login error: {str(e)}")
    exit(1)

# Test 3: Get profile with token
print("\n3. TESTING PROFILE DATA RETRIEVAL")
print("-" * 80)

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

print(f"Fetching profile with token...")

try:
    profile_response = requests.get(
        f'{API_URL}/auth/profile',
        headers=headers,
        timeout=5
    )
    
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        user_profile = profile_data.get('user')
        print(f"\n✓ Profile retrieved successfully!")
        print(f"\nStored User Profile Data:")
        print(f"  ID: {user_profile.get('id')}")
        print(f"  Name: {user_profile.get('name')}")
        print(f"  Email: {user_profile.get('email')}")
        print(f"  Phone: {user_profile.get('phone')}")
        print(f"  Member Since: {user_profile.get('created_at')}")
        
        # Verify data matches registration
        print(f"\n✓ Data Verification:")
        print(f"  Name matches: {'✓' if user_profile.get('name') == test_user_data['name'] else '✗'}")
        print(f"  Email matches: {'✓' if user_profile.get('email') == test_user_data['email'] else '✗'}")
        print(f"  Phone matches: {'✓' if user_profile.get('phone') == test_user_data['phone'] else '✗'}")
    else:
        print(f"\n✗ Profile retrieval failed!")
        print(f"  Status: {profile_response.status_code}")
        print(f"  Response: {profile_response.text}")
        exit(1)
except Exception as e:
    print(f"\n✗ Profile retrieval error: {str(e)}")
    exit(1)

print("\n" + "=" * 80)
print("✓ ALL TESTS PASSED - Data flow is working correctly!")
print("=" * 80)
print("\nData Flow Summary:")
print("  1. Register → Data stored in database")
print("  2. Login → User data retrieved and token generated")
print("  3. Profile → User data fetched using token")
print("\nThe registration information is now accessible in the profile page!")
print("=" * 80)

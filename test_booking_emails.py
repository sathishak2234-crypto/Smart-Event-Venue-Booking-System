import requests
import json
import time

BASE_URL = 'http://localhost:5000/api'

def test_booking_emails():
    print("Testing booking email notifications...")

    # Step 1: Register a test user
    register_data = {
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'testpass123',
        'phone': '9876543210'
    }

    try:
        response = requests.post(f'{BASE_URL}/auth/register', json=register_data)
        if response.status_code == 201:
            print("✓ User registered successfully")
        else:
            print(f"✗ Registration failed: {response.text}")
            return
    except Exception as e:
        print(f"✗ Registration error: {str(e)}")
        return

    # Step 2: Login to get token
    login_data = {
        'email': 'testuser@example.com',
        'password': 'testpass123'
    }

    try:
        response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        if response.status_code == 200:
            token = response.json().get('token')
            print("✓ User logged in successfully")
        else:
            print(f"✗ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"✗ Login error: {str(e)}")
        return

    # Step 3: Get a venue ID
    try:
        response = requests.get(f'{BASE_URL}/venues')
        if response.status_code == 200:
            venues = response.json().get('venues', [])
            if venues:
                venue_id = venues[0]['id']
                print(f"✓ Using venue ID: {venue_id}")
            else:
                print("✗ No venues found")
                return
        else:
            print(f"✗ Failed to get venues: {response.text}")
            return
    except Exception as e:
        print(f"✗ Venues fetch error: {str(e)}")
        return

    # Step 4: Make a booking
    booking_data = {
        'venue_id': venue_id,
        'start_date': '2026-05-01',
        'end_date': '2026-05-01',
        'start_time': '10:00',
        'end_time': '18:00'
    }

    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.post(f'{BASE_URL}/bookings', json=booking_data, headers=headers)
        if response.status_code == 201:
            booking_result = response.json()
            booking_id = booking_result.get('booking_id')
            print(f"✓ Booking created successfully. Booking ID: {booking_id}")
            print("✓ Check email logs for user confirmation and vendor notification")
        else:
            print(f"✗ Booking failed: {response.text}")
    except Exception as e:
        print(f"✗ Booking error: {str(e)}")

if __name__ == '__main__':
    test_booking_emails()
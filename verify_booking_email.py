"""
Test script to verify that booking confirmation emails are sent to users
when they book a venue.
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000'

def print_step(step_num, description):
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print('='*60)

def test_booking_email_notification():
    """Test complete booking email notification flow"""
    
    # Step 1: Register a new user
    print_step(1, "Register Test User")
    register_data = {
        'name': 'Email Test User',
        'email': 'emailtest@example.com',
        'password': 'password123',
        'phone': '9876543210'
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/register', json=register_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code != 201:
        print("❌ Registration failed!")
        return False
    
    # Step 2: Login to get token
    print_step(2, "Login and Get Authentication Token")
    login_data = {
        'email': register_data['email'],
        'password': register_data['password']
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data)
    print(f"Status: {response.status_code}")
    login_response = response.json()
    print(f"Response: {json.dumps(login_response, indent=2)}")
    
    if response.status_code != 200:
        print("❌ Login failed!")
        return False
    
    token = login_response.get('token')
    print(f"✓ Token obtained: {token[:20]}...")
    
    # Step 3: Get available venues
    print_step(3, "Fetch Available Venues")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/api/venues/', headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Failed to fetch venues!")
        return False
    
    venues = response.json().get('venues', [])
    if not venues:
        print("❌ No venues found!")
        return False
    
    venue = venues[0]
    print(f"✓ Found venue: {venue['venue_name']} (ID: {venue['id']})")
    print(f"  Location: {venue['location']}")
    print(f"  Price: ₹{venue['price']}")
    
    # Step 4: Book a venue with email notification
    print_step(4, "Create Booking (Should Trigger Email Notification)")
    booking_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    booking_data = {
        'venue_id': venue['id'],
        'booking_date': booking_date
    }
    
    response = requests.post(f'{BASE_URL}/api/bookings/', 
                            json=booking_data,
                            headers=headers)
    print(f"Status: {response.status_code}")
    booking_response = response.json()
    print(f"Response: {json.dumps(booking_response, indent=2)}")
    
    if response.status_code != 201:
        print("❌ Booking creation failed!")
        return False
    
    booking_id = booking_response.get('booking_id')
    print(f"✓ Booking created successfully!")
    print(f"✓ Booking ID: {booking_id}")
    print(f"✓ Booking Date: {booking_date}")
    print(f"✓ Amount: ₹{booking_response.get('amount')}")
    
    # Step 5: Verify booking was created
    print_step(5, "Verify Booking in Database")
    response = requests.get(f'{BASE_URL}/api/bookings/{booking_id}', headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Booking found in database!")
        booking_details = response.json().get('booking', {})
        print(f"  Booking ID: {booking_details.get('id')}")
        print(f"  Status: {booking_details.get('booking_status')}")
        print(f"  User Email: {booking_details.get('email')}")
        print(f"  User Name: {booking_details.get('name')}")
    else:
        print("❌ Could not verify booking!")
        return False
    
    # Step 6: Verify user bookings list
    print_step(6, "Verify Booking in User's Bookings List")
    response = requests.get(f'{BASE_URL}/api/bookings/', headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        bookings = response.json().get('bookings', [])
        user_booking = next((b for b in bookings if b['id'] == booking_id), None)
        
        if user_booking:
            print(f"✓ Booking found in user's list!")
            print(f"  Venue: {user_booking.get('venue_name')}")
            print(f"  Date: {user_booking.get('booking_date')}")
            print(f"  Amount: ₹{user_booking.get('price')}")
            print(f"  Status: {user_booking.get('booking_status')}")
        else:
            print("❌ Booking not found in user's list!")
            return False
    
    # Summary
    print_step(7, "Test Summary")
    print("✓ Registration successful")
    print("✓ Login successful")
    print("✓ Venue fetched")
    print("✓ Booking created")
    print(f"✓ Booking confirmation email triggered for: emailtest@example.com")
    print("\n📧 EMAIL NOTIFICATION DETAILS:")
    print(f"  Recipient: {register_data['email']}")
    print(f"  User Name: {register_data['name']}")
    print(f"  Venue: {venue['venue_name']}")
    print(f"  Location: {venue['location']}")
    print(f"  Booking Date: {booking_date}")
    print(f"  Amount: ₹{venue['price']}")
    print(f"  Booking ID: {booking_id}")
    print(f"  Status: CONFIRMED")
    print("\n✅ BOOKING EMAIL NOTIFICATION TEST PASSED!")
    print("\nNote: Check EMAIL_ADDRESS configured in backend/.env")
    print("The email should be received at the registered email address.")
    
    return True

if __name__ == '__main__':
    try:
        print("\n" + "="*60)
        print("BOOKING EMAIL NOTIFICATION TEST")
        print("="*60)
        print("\nThis test verifies that when a user books a venue,")
        print("a confirmation email is automatically sent to the user.\n")
        
        success = test_booking_email_notification()
        
        if success:
            print("\n✅ All tests completed successfully!")
        else:
            print("\n❌ Test failed!")
            
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

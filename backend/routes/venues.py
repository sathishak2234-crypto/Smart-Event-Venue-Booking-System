from flask import Blueprint, request, jsonify
from db import execute_query, execute_fetch_one, execute_fetch_all
import logging
from datetime import datetime, timedelta
from mailer import send_new_venue_admin_notification

venues_bp = Blueprint('venues', __name__, url_prefix='/api/venues')
logger = logging.getLogger(__name__)

@venues_bp.route('/', methods=['GET'])
def get_all_venues():
    """Get all venues with optional price filter"""
    try:
        min_price = request.args.get('min_price', type=int)
        max_price = request.args.get('max_price', type=int)
        location = request.args.get('location', type=str)
        
        query = """
            SELECT id, venue_name, location, capacity, price, isAC, rating, facilities,
                   image_url, thumbnail_url, latitude, longitude, gmaps_url,
                   seating_capacity, dining_capacity, dining_type, buffet_available,
                   kitchen_specialty, kitchen_food_support, kitchen_fuel_type, gas_cylinder_count,
                   restrooms_count, bathrooms_count, water_taps_count,
                   two_wheeler_parking_capacity, car_parking_available, max_car_parking_capacity,
                   groom_rooms_count, bride_rooms_count, owner_mobile,
                   advance_amount, advance_details, timing_type,
                   disability_ramp_available, address
            FROM venues
            WHERE 1=1
        """
        params = []
        
        if min_price is not None:
            query += " AND price >= ?"
            params.append(min_price)
        
        if max_price is not None:
            query += " AND price <= ?"
            params.append(max_price)
        
        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
        
        venues = execute_fetch_all(query, tuple(params)) if params else execute_fetch_all(query)
        
        venue_list = []
        if venues:
            for venue in venues:
                venue_list.append({
                    'id': venue['id'],
                    'venue_name': venue['venue_name'],
                    'location': venue['location'],
                    'capacity': venue['capacity'],
                    'price': venue['price'],
                    'isAC': venue['isAC'],
                    'rating': venue['rating'],
                    'facilities': venue['facilities'],
                    'image_url': venue['image_url'],
                    'thumbnail_url': venue['thumbnail_url'],
                    'latitude': venue['latitude'],
                    'longitude': venue['longitude'],
                    'gmaps_url': venue['gmaps_url'],
                    'seating_capacity': venue['seating_capacity'],
                    'dining_capacity': venue['dining_capacity'],
                    'dining_type': venue['dining_type'],
                    'buffet_available': venue['buffet_available'],
                    'kitchen_specialty': venue['kitchen_specialty'],
                    'kitchen_food_support': venue['kitchen_food_support'],
                    'kitchen_fuel_type': venue['kitchen_fuel_type'],
                    'gas_cylinder_count': venue['gas_cylinder_count'],
                    'restrooms_count': venue['restrooms_count'],
                    'bathrooms_count': venue['bathrooms_count'],
                    'water_taps_count': venue['water_taps_count'],
                    'two_wheeler_parking_capacity': venue['two_wheeler_parking_capacity'],
                    'car_parking_available': venue['car_parking_available'],
                    'max_car_parking_capacity': venue['max_car_parking_capacity'],
                    'groom_rooms_count': venue['groom_rooms_count'],
                    'bride_rooms_count': venue['bride_rooms_count'],
                    'owner_mobile': venue['owner_mobile'],
                    'advance_amount': venue['advance_amount'],
                    'advance_details': venue['advance_details'],
                    'timing_type': venue['timing_type'],
                    'disability_ramp_available': venue['disability_ramp_available'],
                    'address': venue['address']
                })
        
        return jsonify({'venues': venue_list}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@venues_bp.route('/<int:venue_id>', methods=['GET'])
def get_venue_details(venue_id):
    """Get details of a specific venue"""
    try:
        venue = execute_fetch_one(
            """
            SELECT id, venue_name, location, capacity, price, isAC, rating, facilities,
                   image_url, thumbnail_url, latitude, longitude, gmaps_url,
                   seating_capacity, dining_capacity, dining_type, buffet_available,
                   kitchen_specialty, kitchen_food_support, kitchen_fuel_type, gas_cylinder_count,
                   restrooms_count, bathrooms_count, water_taps_count,
                   two_wheeler_parking_capacity, car_parking_available, max_car_parking_capacity,
                   groom_rooms_count, bride_rooms_count, owner_mobile,
                   advance_amount, advance_details, timing_type,
                   disability_ramp_available, address
            FROM venues
            WHERE id = ?
            """,
            (venue_id,)
        )
        
        if not venue:
            return jsonify({'message': 'Venue not found'}), 404
        
        # Get booked dates for this venue
        booked_ranges = execute_fetch_all(
            "SELECT booking_date, start_date, end_date FROM bookings WHERE venue_id = ? AND booking_status = 'CONFIRMED'",
            (venue_id,)
        )

        booked_dates_list = []
        for booking in (booked_ranges or []):
            start_date = booking.get('start_date') or booking.get('booking_date')
            end_date = booking.get('end_date') or start_date
            if not start_date or not end_date:
                continue
            current = datetime.strptime(str(start_date), '%Y-%m-%d').date()
            last = datetime.strptime(str(end_date), '%Y-%m-%d').date()
            while current <= last:
                booked_dates_list.append(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)
        
        venue_dict = {
            'id': venue['id'],
            'venue_name': venue['venue_name'],
            'location': venue['location'],
            'capacity': venue['capacity'],
            'price': venue['price'],
            'isAC': venue['isAC'],
            'rating': venue['rating'],
            'facilities': venue['facilities'],
            'image_url': venue['image_url'],
            'thumbnail_url': venue['thumbnail_url'],
            'latitude': venue['latitude'],
            'longitude': venue['longitude'],
            'gmaps_url': venue['gmaps_url'],
            'seating_capacity': venue['seating_capacity'],
            'dining_capacity': venue['dining_capacity'],
            'dining_type': venue['dining_type'],
            'buffet_available': venue['buffet_available'],
            'kitchen_specialty': venue['kitchen_specialty'],
            'kitchen_food_support': venue['kitchen_food_support'],
            'kitchen_fuel_type': venue['kitchen_fuel_type'],
            'gas_cylinder_count': venue['gas_cylinder_count'],
            'restrooms_count': venue['restrooms_count'],
            'bathrooms_count': venue['bathrooms_count'],
            'water_taps_count': venue['water_taps_count'],
            'two_wheeler_parking_capacity': venue['two_wheeler_parking_capacity'],
            'car_parking_available': venue['car_parking_available'],
            'max_car_parking_capacity': venue['max_car_parking_capacity'],
            'groom_rooms_count': venue['groom_rooms_count'],
            'bride_rooms_count': venue['bride_rooms_count'],
            'owner_mobile': venue['owner_mobile'],
            'advance_amount': venue['advance_amount'],
            'advance_details': venue['advance_details'],
            'timing_type': venue['timing_type'],
            'disability_ramp_available': venue['disability_ramp_available'],
            'address': venue['address'],
            'booked_dates': booked_dates_list
        }
        
        return jsonify({'venue': venue_dict}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@venues_bp.route('/availability/<int:venue_id>', methods=['GET'])
def check_availability(venue_id):
    """Check availability for a specific venue and date/range"""
    try:
        start_date = request.args.get('start_date', type=str) or request.args.get('date', type=str)
        end_date = request.args.get('end_date', type=str) or start_date

        if not start_date or not end_date:
            return jsonify({'message': 'start_date and end_date parameters are required'}), 400

        # Check if date range overlaps with existing confirmed booking.
        existing_booking = execute_fetch_one(
            """
            SELECT *
            FROM bookings
            WHERE venue_id = %s
              AND booking_status = 'CONFIRMED'
              AND COALESCE(start_date, booking_date) <= %s
              AND COALESCE(end_date, booking_date) >= %s
            """,
            (venue_id, end_date, start_date)
        )
        
        if existing_booking:
            return jsonify({'available': False, 'message': 'Venue is booked on this date'}), 200
        
        return jsonify({'available': True, 'message': 'Venue is available'}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@venues_bp.route('/', methods=['POST'])
def create_venue():
    """Create a new venue (Admin only)"""
    try:
        data = request.get_json()
        
        required_fields = ['venue_name', 'location', 'capacity', 'price']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400

        capacity_value = int(data['capacity'])
        
        result = execute_query(
            """
            INSERT INTO venues (
                venue_name, location, capacity, price, facilities, image_url, description,
                seating_capacity, dining_capacity, dining_type, buffet_available,
                kitchen_specialty, kitchen_food_support, kitchen_fuel_type, gas_cylinder_count,
                restrooms_count, bathrooms_count, water_taps_count,
                two_wheeler_parking_capacity, car_parking_available, max_car_parking_capacity,
                groom_rooms_count, bride_rooms_count, owner_mobile, owner_email,
                advance_amount, advance_details, timing_type,
                disability_ramp_available, address
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s
            )
            """,
            (
                data['venue_name'], data['location'], capacity_value, data['price'],
                data.get('facilities', ''), data.get('image_url', ''), data.get('description', ''),
                data.get('seating_capacity', capacity_value),
                data.get('dining_capacity', int(capacity_value * 0.6)),
                data.get('dining_type', 'veg'),
                data.get('buffet_available', 0),
                data.get('kitchen_specialty', 'Classic'),
                data.get('kitchen_food_support', 'Both'),
                data.get('kitchen_fuel_type', 'Gas Cylinder'),
                data.get('gas_cylinder_count', 0),
                data.get('restrooms_count', 0),
                data.get('bathrooms_count', 0),
                data.get('water_taps_count', 0),
                data.get('two_wheeler_parking_capacity', 0),
                data.get('car_parking_available', 0),
                data.get('max_car_parking_capacity', 0),
                data.get('groom_rooms_count', 0),
                data.get('bride_rooms_count', 0),
                data.get('owner_mobile', ''),
                data.get('owner_email', ''),
                data.get('advance_amount', 0),
                data.get('advance_details', ''),
                data.get('timing_type', '12hrs'),
                data.get('disability_ramp_available', 0),
                data.get('address', data['location'])
            )
        )
        
        if result:
            # Notify admin email for every new venue registration.
            try:
                email_result = send_new_venue_admin_notification({
                    'venue_name': data['venue_name'],
                    'location': data['location'],
                    'capacity': data['capacity'],
                    'price': data['price'],
                    'rating': data.get('rating', 'N/A')
                })
                if email_result['success']:
                    logger.info(f"Admin notified for new venue: {data['venue_name']}")
                else:
                    logger.warning(
                        f"Admin notification failed for venue {data['venue_name']}: {email_result.get('error')}"
                    )
            except Exception as email_error:
                logger.error(f"Error sending admin venue notification: {str(email_error)}")

            return jsonify({'message': 'Venue created successfully', 'venue_id': result}), 201
        else:
            return jsonify({'message': 'Failed to create venue'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@venues_bp.route('/<int:venue_id>', methods=['PUT'])
def update_venue(venue_id):
    """Update venue details (Admin only)"""
    try:
        data = request.get_json()
        
        # Build dynamic update query
        update_fields = []
        params = []
        
        for field in [
            'venue_name', 'location', 'capacity', 'price', 'facilities', 'image_url', 'description',
            'seating_capacity', 'dining_capacity', 'dining_type', 'buffet_available',
            'kitchen_specialty', 'kitchen_food_support', 'kitchen_fuel_type', 'gas_cylinder_count',
            'restrooms_count', 'bathrooms_count', 'water_taps_count',
            'two_wheeler_parking_capacity', 'car_parking_available', 'max_car_parking_capacity',
            'groom_rooms_count', 'bride_rooms_count', 'owner_mobile', 'owner_email',
            'advance_amount', 'advance_details', 'timing_type',
            'disability_ramp_available', 'address', 'gmaps_url', 'thumbnail_url'
        ]:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({'message': 'No fields to update'}), 400
        
        params.append(venue_id)
        query = f"UPDATE venues SET {', '.join(update_fields)} WHERE id = %s"
        
        execute_query(query, params)
        
        return jsonify({'message': 'Venue updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

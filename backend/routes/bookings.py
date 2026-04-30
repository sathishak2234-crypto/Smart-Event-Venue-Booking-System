from flask import Blueprint, request, jsonify
from db import execute_query, execute_fetch_one, execute_fetch_all
import jwt
from config import SECRET_KEY, VENDOR_NOTIFICATION_FALLBACK_EMAIL
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor
from mailer import send_booking_confirmation_with_status, send_vendor_booking_notification_with_status

logger = logging.getLogger(__name__)

bookings_bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')

def get_user_from_token(token):
    """Extract user_id from JWT token"""
    try:
        if not token:
            return None
        token = token.split(' ')[1] if ' ' in token else token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded['user_id']
    except:
        return None


def normalize_booking_window(data):
    """Normalize booking range inputs while preserving legacy booking_date support."""
    legacy_date = data.get('booking_date')
    start_date = data.get('start_date') or legacy_date
    end_date = data.get('end_date') or start_date
    start_time = (data.get('start_time') or '09:00').strip()
    end_time = (data.get('end_time') or '21:00').strip()

    if not start_date or not end_date:
        return None

    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        datetime.strptime(start_time, '%H:%M')
        datetime.strptime(end_time, '%H:%M')
    except ValueError:
        return None

    if end_dt < start_dt:
        return None

    if start_dt == end_dt and end_time <= start_time:
        return None

    return {
        'booking_date': start_date,
        'start_date': start_date,
        'end_date': end_date,
        'start_time': start_time,
        'end_time': end_time,
        'start_dt': start_dt,
        'end_dt': end_dt,
    }

@bookings_bp.route('/', methods=['POST'])
def create_booking():
    """Create a new booking"""
    try:
        data = request.get_json()
        token = request.headers.get('Authorization')
        user_id = get_user_from_token(token)

        if not user_id:
            return jsonify({'message': 'Authentication required'}), 401

        venue_id = data.get('venue_id')
        booking_window = normalize_booking_window(data)

        if not venue_id or not booking_window:
            return jsonify({'message': 'Venue ID, valid start/end date, and time range are required'}), 400

        # Check if venue exists
        venue = execute_fetch_one("SELECT * FROM venues WHERE id = %s", (venue_id,))
        if not venue:
            return jsonify({'message': 'Venue not found'}), 404

        booking_days = (booking_window['end_dt'] - booking_window['start_dt']).days + 1
        total_amount = int(venue['price']) * booking_days

        # Check if date range overlaps an existing confirmed/pending booking.
        existing_booking = execute_fetch_one(
            """
            SELECT * FROM bookings
            WHERE venue_id = %s
              AND booking_status IN ('CONFIRMED', 'PENDING')
              AND COALESCE(start_date, booking_date) <= %s
              AND COALESCE(end_date, booking_date) >= %s
            """,
            (venue_id, booking_window['end_date'], booking_window['start_date'])
        )

        if existing_booking:
            return jsonify({'message': 'Venue is already booked for the selected date range', 'error': 'already_booked'}), 409

        # Create booking with CONFIRMED status directly
        booking_id = execute_query(
            """
            INSERT INTO bookings (user_id, venue_id, booking_date, start_date, end_date, start_time, end_time, payment_status, booking_status, amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                venue_id,
                booking_window['booking_date'],
                booking_window['start_date'],
                booking_window['end_date'],
                booking_window['start_time'],
                booking_window['end_time'],
                'COMPLETED',
                'CONFIRMED',
                total_amount
            )
        )

        if booking_id:
            logger.info(f"Booking created successfully. Booking ID: {booking_id}")

            # Send booking confirmation and vendor notification emails in parallel.
            try:
                # Get user details for email
                user = execute_fetch_one(
                    "SELECT name, email, phone FROM users WHERE id = %s",
                    (user_id,)
                )

                if user:
                    date_label = f"{booking_window['start_date']} to {booking_window['end_date']}"
                    time_label = f"{booking_window['start_time']} - {booking_window['end_time']}"

                    user_email_payload = {
                        'name': user['name'],
                        'email': user['email'],
                        'venue_name': venue['venue_name'],
                        'location': venue['location'],
                        'booking_date': f"{date_label} ({time_label})",
                        'amount': total_amount,
                        'payment_status': 'COMPLETED'
                    }

                    raw_vendor_email = (venue.get('owner_email') or '').strip() if venue else ''
                    vendor_email = raw_vendor_email or (VENDOR_NOTIFICATION_FALLBACK_EMAIL or '').strip()

                    vendor_email_result = {
                        'success': False,
                        'error': 'Vendor email is missing for this venue.',
                        'delivery_status': 'FAILED'
                    }

                    with ThreadPoolExecutor(max_workers=2) as executor:
                        user_future = executor.submit(send_booking_confirmation_with_status, user_email_payload)

                        vendor_future = None
                        if vendor_email:
                            vendor_payload = {
                                'vendor_email': vendor_email,
                                'user_name': user['name'],
                                'user_email': user['email'],
                                'user_phone': (user.get('phone') or 'Not provided'),
                                'venue_name': venue['venue_name'],
                                'location': venue['location'],
                                'booking_date': date_label,
                                'booking_time': time_label,
                                'amount': total_amount,
                            }
                            vendor_future = executor.submit(send_vendor_booking_notification_with_status, vendor_payload)

                        email_result = user_future.result()
                        if vendor_future:
                            vendor_email_result = vendor_future.result()

                    if email_result['success']:
                        logger.info(f"Booking {booking_id}: Confirmation email sent to {user['email']}")
                        execute_query(
                            "UPDATE bookings SET email_sent = 1, email_status = 'SENT', email_sent_at = CURRENT_TIMESTAMP WHERE id = ?",
                            (booking_id,)
                        )
                    else:
                        logger.warning(
                            f"Booking {booking_id}: Failed to send confirmation email to {user['email']}. "
                            f"Error: {email_result.get('error')}"
                        )
                        execute_query(
                            "UPDATE bookings SET email_sent = 0, email_status = 'FAILED', email_sent_at = NULL WHERE id = ?",
                            (booking_id,)
                        )

                    if vendor_email_result['success']:
                        logger.info(
                            f"Booking {booking_id}: Vendor notification sent to {vendor_email}"
                        )
                    else:
                        logger.warning(
                            f"Booking {booking_id}: Vendor notification failed. "
                            f"Vendor email: {vendor_email or 'MISSING'}. "
                            f"Error: {vendor_email_result.get('error')}"
                        )
                else:
                    logger.warning(f"Booking {booking_id}: User record not found for email notifications")

            except Exception as e:
                logger.error(f"Error processing booking email: {str(e)}")

            return jsonify({
                'message': 'Booking created successfully',
                'booking_id': booking_id,
                'amount': total_amount,
                'venue_name': venue['venue_name'],
                'start_date': booking_window['start_date'],
                'end_date': booking_window['end_date'],
                'start_time': booking_window['start_time'],
                'end_time': booking_window['end_time']
            }), 201
        else:
            return jsonify({'message': 'Failed to create booking'}), 500

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bookings_bp.route('/', methods=['GET'])
def get_user_bookings():
    """Get all bookings for logged-in user"""
    try:
        token = request.headers.get('Authorization')
        user_id = get_user_from_token(token)
        
        if not user_id:
            return jsonify({'message': 'Authentication required'}), 401
        
        bookings = execute_fetch_all(
            """SELECT b.*, v.venue_name, v.location, v.price 
               FROM bookings b 
               JOIN venues v ON b.venue_id = v.id 
               WHERE b.user_id = %s 
               ORDER BY COALESCE(b.start_date, b.booking_date) DESC""",
            (user_id,)
        )
        
        return jsonify({'bookings': bookings}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bookings_bp.route('/<int:booking_id>', methods=['GET'])
def get_booking_details(booking_id):
    """Get details of a specific booking"""
    try:
        booking = execute_fetch_one(
            """SELECT b.*, v.venue_name, v.location, v.price, v.facilities, u.name, u.email 
               FROM bookings b 
               JOIN venues v ON b.venue_id = v.id 
               JOIN users u ON b.user_id = u.id 
               WHERE b.id = %s""",
            (booking_id,)
        )
        
        if not booking:
            return jsonify({'message': 'Booking not found'}), 404
        
        return jsonify({'booking': booking}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a booking"""
    try:
        token = request.headers.get('Authorization')
        user_id = get_user_from_token(token)
        
        if not user_id:
            return jsonify({'message': 'Authentication required'}), 401
        
        booking = execute_fetch_one(
            "SELECT * FROM bookings WHERE id = %s AND user_id = %s",
            (booking_id, user_id)
        )
        
        if not booking:
            return jsonify({'message': 'Booking not found'}), 404
        
        # Check if booking is already cancelled
        if booking['booking_status'] == 'CANCELLED':
            return jsonify({'message': 'Booking is already cancelled'}), 400
        
        # Check if booking date has passed
        booking_date = datetime.strptime(str(booking.get('start_date') or booking['booking_date']), '%Y-%m-%d').date()
        if booking_date < datetime.now().date():
            return jsonify({'message': 'Cannot cancel past bookings'}), 400
        
        # Cancel the booking
        execute_query(
            "UPDATE bookings SET booking_status = %s WHERE id = %s",
            ('CANCELLED', booking_id)
        )
        
        logger.info(f"Booking {booking_id} cancelled by user {user_id}")
        
        return jsonify({
            'message': 'Booking cancelled successfully',
            'booking_id': booking_id
        }), 200
            
    except Exception as e:
        logger.error(f"Error cancelling booking: {str(e)}")
        return jsonify({'message': str(e)}), 500

@bookings_bp.route('/calendar/<int:venue_id>', methods=['GET'])
def get_booked_dates(venue_id):
    """Get all booked dates for calendar view"""
    try:
        bookings = execute_fetch_all(
            """
            SELECT booking_date, start_date, end_date, booking_status
            FROM bookings
            WHERE venue_id = %s
            """,
            (venue_id,)
        )

        booked_dates = []
        for booking in bookings:
            if booking['booking_status'] != 'CONFIRMED':
                continue
            start_date = booking.get('start_date') or booking.get('booking_date')
            end_date = booking.get('end_date') or start_date
            if not start_date or not end_date:
                continue
            current = datetime.strptime(str(start_date), '%Y-%m-%d').date()
            last = datetime.strptime(str(end_date), '%Y-%m-%d').date()
            while current <= last:
                booked_dates.append(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)
        
        return jsonify({'booked_dates': booked_dates}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@bookings_bp.route('/<int:booking_id>/send-confirmation', methods=['POST'])
def send_booking_confirmation_email(booking_id):
    """Send booking confirmation email to user"""
    try:
        token = request.headers.get('Authorization')
        user_id = get_user_from_token(token)
        
        if not user_id:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        
        # Get booking details
        booking = execute_fetch_one(
            """SELECT b.*, v.venue_name, v.location, v.price, u.name, u.email
               FROM bookings b
               JOIN venues v ON b.venue_id = v.id
               JOIN users u ON b.user_id = u.id
               WHERE b.id = %s AND b.user_id = %s""",
            (booking_id, user_id)
        )
        
        if not booking:
            return jsonify({'success': False, 'message': 'Booking not found'}), 404
        
        # Send confirmation email
        try:
            email_result = send_booking_confirmation_with_status({
                'name': booking['name'],
                'email': booking['email'],
                'venue_name': booking['venue_name'],
                'location': booking['location'],
                'booking_date': str(booking['booking_date']),
                'amount': booking['price'],
                'payment_status': booking['payment_status']
            })

            if email_result['success']:
                execute_query(
                    "UPDATE bookings SET email_sent = 1, email_status = 'SENT', email_sent_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (booking_id,)
                )
                logger.info(f"Booking {booking_id}: Confirmation email resent to {booking['email']}")

                return jsonify({
                    'success': True,
                    'message': 'Confirmation email sent successfully',
                    'booking_id': booking_id
                }), 200

            logger.warning(
                f"Booking {booking_id}: Confirmation email resend failed for {booking['email']}. "
                f"Error: {email_result.get('error')}"
            )
            execute_query(
                "UPDATE bookings SET email_sent = 0, email_status = 'FAILED', email_sent_at = NULL WHERE id = ?",
                (booking_id,)
            )
            return jsonify({
                'success': False,
                'message': 'Email delivery failed. Please verify email configuration.',
                'booking_id': booking_id
            }), 500
        except Exception as e:
            logger.error(f"Error sending confirmation email: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error sending email: {str(e)}',
                'booking_id': booking_id
            }), 500
        
    except Exception as e:
        print(f"Error in send confirmation endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'booking_id': booking_id
        }), 500

@bookings_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        token = request.headers.get('Authorization')
        user_id = get_user_from_token(token)
        
        if not user_id:
            return jsonify({'message': 'Authentication required'}), 401
        
        # Total bookings
        total_bookings = execute_fetch_one(
            "SELECT COUNT(*) as count FROM bookings WHERE user_id = %s",
            (user_id,)
        )
        
        # Confirmed bookings
        confirmed_bookings = execute_fetch_one(
            "SELECT COUNT(*) as count FROM bookings WHERE user_id = %s AND booking_status = 'CONFIRMED'",
            (user_id,)
        )
        
        # Total spent
        total_spent = execute_fetch_one(
            "SELECT SUM(amount) as total FROM bookings WHERE user_id = %s AND payment_status = 'PAID'",
            (user_id,)
        )
        
        stats = {
            'total_bookings': total_bookings['count'] if total_bookings else 0,
            'confirmed_bookings': confirmed_bookings['count'] if confirmed_bookings else 0,
            'total_spent': total_spent['total'] if total_spent and total_spent['total'] else 0
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

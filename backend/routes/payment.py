from flask import Blueprint, request, jsonify
from db import execute_query, execute_fetch_one, execute_fetch_all
import jwt
from config import SECRET_KEY, RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, PAYMENT_CURRENCY
from mailer import send_booking_confirmation

# Lazy import razorpay
try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False
    print("Warning: Razorpay not available")

payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')

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

# Initialize Razorpay only if available
if RAZORPAY_AVAILABLE:
    try:
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    except:
        client = None
else:
    client = None

@payment_bp.route('/create-order', methods=['POST'])
def create_order():
    """Create a Razorpay order"""
    try:
        if not RAZORPAY_AVAILABLE or not client:
            return jsonify({'message': 'Payment gateway not available'}), 503
            
        data = request.get_json()
        booking_id = data.get('booking_id')
        
        if not booking_id:
            return jsonify({'message': 'Booking ID is required'}), 400
        
        # Get booking details
        booking = execute_fetch_one(
            "SELECT b.*, v.price FROM bookings b JOIN venues v ON b.venue_id = v.id WHERE b.id = %s",
            (booking_id,)
        )
        
        if not booking:
            return jsonify({'message': 'Booking not found'}), 404
        
        # Create Razorpay order
        order_data = {
            'amount': booking['price'] * 100,  # Convert to paise
            'currency': PAYMENT_CURRENCY,
            'receipt': f'booking_{booking_id}',
            'notes': {
                'booking_id': booking_id
            }
        }
        
        order = client.order.create(data=order_data)
        
        return jsonify({
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'booking_id': booking_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@payment_bp.route('/verify-payment', methods=['POST'])
def verify_payment():
    """Verify Razorpay payment"""
    try:
        data = request.get_json()
        
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')
        booking_id = data.get('booking_id')
        
        if not all([payment_id, order_id, signature, booking_id]):
            return jsonify({'message': 'Missing payment details'}), 400
        
        # Verify signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        try:
            client.utility.verify_payment_signature(params_dict)
            
            # Get booking amount first
            booking_info = execute_fetch_one(
                "SELECT amount FROM bookings WHERE id = %s",
                (booking_id,)
            )
            
            if not booking_info:
                return jsonify({'message': 'Booking not found'}), 404
            
            # Update booking status
            execute_query(
                "UPDATE bookings SET payment_status = %s, payment_id = %s WHERE id = %s",
                ('PAID', payment_id, booking_id)
            )
            
            # Store payment record
            execute_query(
                "INSERT INTO payments (booking_id, amount, payment_method, transaction_id) VALUES (%s, %s, %s, %s)",
                (booking_id, booking_info['amount'], 'Razorpay', payment_id)
            )
            
            # Get booking and user details
            booking = execute_fetch_one(
                """SELECT b.*, v.venue_name, v.location, u.email, u.name 
                   FROM bookings b 
                   JOIN venues v ON b.venue_id = v.id 
                   JOIN users u ON b.user_id = u.id 
                   WHERE b.id = %s""",
                (booking_id,)
            )
            
            # Send booking confirmation email
            if booking:
                try:
                    send_booking_confirmation({
                        'name': booking['name'],
                        'email': booking['email'],
                        'venue_name': booking['venue_name'],
                        'location': booking['location'],
                        'booking_date': str(booking['booking_date']),
                        'amount': booking['amount'],
                        'payment_status': booking['payment_status']
                    })
                    
                    # Mark email as sent
                    execute_query(
                        "UPDATE bookings SET email_sent = 1, email_sent_at = NOW() WHERE id = %s",
                        (booking_id,)
                    )
                    print(f"Payment verified and email sent for booking {booking_id}")
                except Exception as e:
                    print(f"Error sending email: {str(e)}")
                    # Still mark as processed
                    try:
                        execute_query(
                            "UPDATE bookings SET email_sent = 1, email_sent_at = NOW() WHERE id = %s",
                            (booking_id,)
                        )
                    except:
                        pass
            
            return jsonify({'message': 'Payment verified successfully'}), 200
            
        except Exception as e:
            if RAZORPAY_AVAILABLE and 'BadRequestsError' in str(type(e).__name__):
                return jsonify({'message': 'Payment verification failed'}), 400
            return jsonify({'message': 'Payment verification error: ' + str(e)}), 400
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@payment_bp.route('/payment-history', methods=['GET'])
def get_payment_history():
    """Get payment history for user"""
    try:
        token = request.headers.get('Authorization')
        user_id = get_user_from_token(token)
        
        if not user_id:
            return jsonify({'message': 'Authentication required'}), 401
        
        payments = execute_fetch_all(
            """SELECT p.*, b.booking_date, v.venue_name, b.amount 
               FROM payments p 
               JOIN bookings b ON p.booking_id = b.id 
               JOIN venues v ON b.venue_id = v.id 
               WHERE b.user_id = %s 
               ORDER BY p.payment_date DESC""",
            (user_id,)
        )
        
        return jsonify({'payments': payments}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@payment_bp.route('/dashboard/revenue', methods=['GET'])
def get_revenue_stats():
    """Get revenue statistics (Admin)"""
    try:
        # Total revenue
        total_revenue = execute_fetch_one(
            "SELECT SUM(amount) as total FROM bookings WHERE payment_status = 'PAID'"
        )
        
        # Monthly revenue
        monthly_revenue = execute_fetch_all(
            """SELECT DATE_FORMAT(created_at, '%Y-%m') as month, SUM(amount) as revenue 
               FROM bookings WHERE payment_status = 'PAID' 
               GROUP BY DATE_FORMAT(created_at, '%Y-%m') 
               ORDER BY month DESC LIMIT 12"""
        )
        
        # Total transactions
        total_transactions = execute_fetch_one(
            "SELECT COUNT(*) as count FROM payments"
        )
        
        stats = {
            'total_revenue': total_revenue['total'] if total_revenue and total_revenue['total'] else 0,
            'monthly_revenue': monthly_revenue or [],
            'total_transactions': total_transactions['count'] if total_transactions else 0
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

from flask import Blueprint, request, jsonify
from db import execute_query, execute_fetch_one, execute_fetch_all
import jwt
from config import SECRET_KEY

feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')

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

@feedback_bp.route('/', methods=['POST'])
def submit_feedback():
    """Submit feedback for a booking"""
    try:
        data = request.get_json()
        token = request.headers.get('Authorization')
        user_id = get_user_from_token(token)
        
        if not user_id:
            return jsonify({'message': 'Authentication required'}), 401
        
        booking_id = data.get('booking_id')
        rating = data.get('rating')
        message = data.get('message')
        
        if not booking_id or not rating:
            return jsonify({'message': 'Booking ID and rating are required'}), 400
        
        if not (1 <= rating <= 5):
            return jsonify({'message': 'Rating must be between 1 and 5'}), 400
        
        # Verify booking exists and belongs to user
        booking = execute_fetch_one(
            "SELECT * FROM bookings WHERE id = %s AND user_id = %s",
            (booking_id, user_id)
        )
        
        if not booking:
            return jsonify({'message': 'Booking not found'}), 404
        
        # Submit feedback
        feedback_id = execute_query(
            "INSERT INTO feedback (user_id, booking_id, rating, message) VALUES (%s, %s, %s, %s)",
            (user_id, booking_id, rating, message or '')
        )
        
        if feedback_id:
            return jsonify({'message': 'Feedback submitted successfully', 'feedback_id': feedback_id}), 201
        else:
            return jsonify({'message': 'Failed to submit feedback'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@feedback_bp.route('/', methods=['GET'])
def get_all_feedback():
    """Get all feedback for a venue or all venues"""
    try:
        venue_id = request.args.get('venue_id', type=int)
        
        if venue_id:
            feedback_list = execute_fetch_all(
                """SELECT f.*, u.name, b.venue_id 
                   FROM feedback f 
                   JOIN users u ON f.user_id = u.id 
                   JOIN bookings b ON f.booking_id = b.id 
                   WHERE b.venue_id = %s 
                   ORDER BY f.created_at DESC""",
                (venue_id,)
            )
        else:
            feedback_list = execute_fetch_all(
                """SELECT f.*, u.name, b.venue_id, v.venue_name 
                   FROM feedback f 
                   JOIN users u ON f.user_id = u.id 
                   JOIN bookings b ON f.booking_id = b.id 
                   JOIN venues v ON b.venue_id = v.id 
                   ORDER BY f.created_at DESC"""
            )
        
        return jsonify({'feedback': feedback_list}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@feedback_bp.route('/<int:venue_id>/rating', methods=['GET'])
def get_venue_rating(venue_id):
    """Get average rating for a venue"""
    try:
        rating_data = execute_fetch_one(
            """SELECT AVG(f.rating) as avg_rating, COUNT(f.id) as total_reviews 
               FROM feedback f 
               JOIN bookings b ON f.booking_id = b.id 
               WHERE b.venue_id = %s""",
            (venue_id,)
        )
        
        avg_rating = rating_data['avg_rating'] if rating_data and rating_data['avg_rating'] else 0
        total_reviews = rating_data['total_reviews'] if rating_data and rating_data['total_reviews'] else 0
        
        return jsonify({
            'venue_id': venue_id,
            'average_rating': round(float(avg_rating), 2) if avg_rating else 0,
            'total_reviews': total_reviews
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@feedback_bp.route('/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    """Delete feedback (user can only delete their own)"""
    try:
        token = request.headers.get('Authorization')
        user_id = get_user_from_token(token)
        
        if not user_id:
            return jsonify({'message': 'Authentication required'}), 401
        
        feedback = execute_fetch_one(
            "SELECT * FROM feedback WHERE id = %s AND user_id = %s",
            (feedback_id, user_id)
        )
        
        if not feedback:
            return jsonify({'message': 'Feedback not found'}), 404
        
        execute_query(
            "DELETE FROM feedback WHERE id = %s",
            (feedback_id,)
        )
        
        return jsonify({'message': 'Feedback deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

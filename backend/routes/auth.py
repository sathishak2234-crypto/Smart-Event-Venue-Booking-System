from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import execute_query, execute_fetch_one
import jwt
from config import SECRET_KEY
from datetime import datetime, timedelta
import logging
from mailer import send_registration_confirmation, send_registration_confirmation_with_status

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Name, email, and password are required'}), 400
        
        # Check if user already exists
        existing_user = execute_fetch_one(
            "SELECT id FROM users WHERE email = ?",
            (data['email'],)
        )
        
        if existing_user:
            return jsonify({'message': 'User already exists'}), 409
        
        # Hash password
        hashed_password = generate_password_hash(data['password'])
        
        # Insert user
        result = execute_query(
            "INSERT INTO users (name, email, password, phone, is_admin) VALUES (?, ?, ?, ?, ?)",
            (data['name'], data['email'], hashed_password, data.get('phone', ''), 0)
        )
        
        if result:
            # Send registration confirmation email (non-blocking)
            try:
                email_result = send_registration_confirmation_with_status({
                    'name': data['name'],
                    'email': data['email']
                })
                if email_result['success']:
                    execute_query(
                        "UPDATE users SET registration_email_sent = 1, registration_email_status = 'SENT', registration_email_sent_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (result,)
                    )
                    logger.info(f"Registration email sent to {data['email']}")
                else:
                    execute_query(
                        "UPDATE users SET registration_email_sent = 0, registration_email_status = 'FAILED', registration_email_sent_at = NULL WHERE id = ?",
                        (result,)
                    )
                    logger.warning(f"Failed to send registration email to {data['email']}")
            except Exception as e:
                try:
                    execute_query(
                        "UPDATE users SET registration_email_sent = 0, registration_email_status = 'FAILED', registration_email_sent_at = NULL WHERE id = ?",
                        (result,)
                    )
                except Exception:
                    pass
                logger.error(f"Error sending registration email: {str(e)}")
            
            logger.info(f"User registered successfully. User ID: {result}, Email: {data['email']}")
            
            return jsonify({
                'message': 'User registered successfully',
                'user_id': result,
                'email': data['email'],
                'name': data['name']
            }), 201
        else:
            return jsonify({'message': 'Registration failed'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        import sqlite3 as sq
        from db import DB_PATH
        
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Find user using direct SQLite connection
        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, password, is_admin FROM users WHERE email = ?", (data['email'],))
        user_row = cursor.fetchone()
        conn.close()
        
        if not user_row or not check_password_hash(user_row['password'], data['password']):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user_row['id'],
            'email': user_row['email'],
            'is_admin': user_row['is_admin'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user_row['id'],
                'name': user_row['name'],
                'email': user_row['email'],
                'is_admin': user_row['is_admin']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # Remove 'Bearer ' from token
        token = token.split(' ')[1] if ' ' in token else token
        
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = decoded['user_id']
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        # Fetch user profile
        user = execute_fetch_one(
            "SELECT id, name, email, phone, is_admin, registration_email_sent, registration_email_status, registration_email_sent_at, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'phone': user['phone'],
                'is_admin': user['is_admin'],
                'registration_email_sent': user['registration_email_sent'],
                'registration_email_status': user['registration_email_status'],
                'registration_email_sent_at': user['registration_email_sent_at'],
                'created_at': user['created_at']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout (client-side token removal)"""
    return jsonify({'message': 'Logout successful'}), 200

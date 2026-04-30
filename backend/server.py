from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import DEBUG, SECRET_KEY
from db import get_db_connection, init_db
import os

# Initialize database on startup
try:
    init_db()
except Exception as e:
    print(f"Database initialization failed: {e}")

# Import blueprints
from routes.auth import auth_bp
from routes.venues import venues_bp
from routes.bookings import bookings_bp
from routes.feedback import feedback_bp
from routes.payment import payment_bp
from routes.admin import admin_bp

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(venues_bp)
app.register_blueprint(bookings_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(admin_bp)

# Serve uploaded images
@app.route('/uploads/<filename>')
def download_file(filename):
    """Serve uploaded images"""
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    return send_from_directory(uploads_dir, filename)


@app.route('/images/<path:filename>')
def serve_venue_image(filename):
    """Serve venue images from project images folder."""
    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
    return send_from_directory(images_dir, filename)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
            connection.close()
            return jsonify({'status': 'healthy', 'database': 'connected'}), 200
        except Exception as e:
            return jsonify({'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}), 503
    else:
        return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 503

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Smart Event Venue Booking System API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'venues': '/api/venues',
            'bookings': '/api/bookings',
            'feedback': '/api/feedback',
            'payment': '/api/payment',
            'admin': '/api/admin'
        }
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'message': 'Bad request'}), 400

if __name__ == '__main__':
    print("Starting Smart Event Venue Booking System API...")
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)

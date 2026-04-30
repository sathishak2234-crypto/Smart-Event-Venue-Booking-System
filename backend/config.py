import os
from dotenv import load_dotenv

load_dotenv()

# Flask Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', True)

# MySQL Configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DB = os.getenv('MYSQL_DB', 'venue_booking')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))

# Email Configuration
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'sathishak2234@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'hbouzmmjqymjxisq')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'sathishak2234@gmail.com')
VENDOR_NOTIFICATION_FALLBACK_EMAIL = os.getenv('VENDOR_NOTIFICATION_FALLBACK_EMAIL', 'skrtamilan7@gmail.com')

# Razorpay Configuration
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', 'your-razorpay-key')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', 'your-razorpay-secret')

# Payment Configuration
PAYMENT_CURRENCY = 'INR'
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')

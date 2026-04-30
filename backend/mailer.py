import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD, ADMIN_EMAIL, FRONTEND_URL
import logging
import os
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_email_to_file(recipient_email, subject, body, email_type="general"):
    """Backup: Log email to file"""
    try:
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'email_logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        log_file = os.path.join(logs_dir, 'email_log.txt')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*70}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Type: {email_type}\n")
            f.write(f"To: {recipient_email}\n")
            f.write(f"Subject: {subject}\n")
            f.write(f"From: {EMAIL_ADDRESS}\n")
            f.write(f"{'='*70}\n")
            f.write(f"{body}\n")
        
        logger.info(f"Email logged to backup file for {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to log email to file: {str(e)}")
        return False

def send_email_with_status(recipient_email, subject, body, is_html=False, email_type="general"):
    """Send email and return structured delivery status."""
    try:
        logger.info(f"=" * 70)
        logger.info(f"📧 SENDING EMAIL")
        logger.info(f"To: {recipient_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"From: {EMAIL_ADDRESS}")
        logger.info(f"Host: {EMAIL_HOST}:{EMAIL_PORT}")
        
        # Build message
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = EMAIL_ADDRESS
        message['To'] = recipient_email
        
        if is_html:
            message.attach(MIMEText(body, 'html'))
        else:
            message.attach(MIMEText(body, 'plain'))
        
        logger.info("Connecting to SMTP server...")
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=5)
        logger.info(f"✓ Connected to {EMAIL_HOST}")
        
        logger.info("Initiating STARTTLS...")
        server.starttls()
        logger.info("✓ STARTTLS successful")
        
        logger.info(f"Authenticating as {EMAIL_ADDRESS}...")
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        logger.info(f"✓ Authentication successful")
        
        logger.info("Sending message...")
        server.send_message(message)
        logger.info(f"✓✓✓ EMAIL SUCCESSFULLY SENT to {recipient_email}")
        
        server.quit()
        logger.info("=" * 70)
        return {
            'success': True,
            'delivery_status': 'SENT',
            'logged_to_file': False,
            'error': None,
        }
        
    except smtplib.SMTPAuthenticationError as e:
        logger.warning(f"⚠️ GMAIL AUTH FAILED - Using local file logging instead")
        logger.warning(f"Error: {str(e)}")
        logger.warning("To fix: Update EMAIL_PASSWORD in .env with valid Gmail app password")
        logger.warning("Visit: https://myaccount.google.com/apppasswords")
        log_result = log_email_to_file(recipient_email, subject, body, email_type)
        logger.info(f"✓ Email logged to backup file for {recipient_email}")
        logger.info("=" * 70)
        return {
            'success': False,
            'delivery_status': 'FAILED',
            'logged_to_file': bool(log_result),
            'error': str(e),
        }
        
    except smtplib.SMTPException as e:
        logger.warning(f"⚠️ SMTP ERROR: {str(e)}")
        log_result = log_email_to_file(recipient_email, subject, body, email_type)
        logger.info(f"✓ Email logged to backup file for {recipient_email}")
        logger.info("=" * 70)
        return {
            'success': False,
            'delivery_status': 'FAILED',
            'logged_to_file': bool(log_result),
            'error': str(e),
        }
        
    except Exception as e:
        logger.warning(f"⚠️ ERROR: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        log_result = log_email_to_file(recipient_email, subject, body, email_type)
        logger.info(f"✓ Email logged to backup file for {recipient_email}")
        logger.info("=" * 70)
        return {
            'success': False,
            'delivery_status': 'FAILED',
            'logged_to_file': bool(log_result),
            'error': str(e),
        }


def send_email(recipient_email, subject, body, is_html=False, email_type="general"):
    """Backwards-compatible wrapper that returns a boolean."""
    result = send_email_with_status(recipient_email, subject, body, is_html=is_html, email_type=email_type)
    return result['success']

def send_registration_confirmation(user):
    """Send registration confirmation email"""
    subject = "Welcome to Smart Event Venue Booking System"
    
    body = f"""
    <html>
        <body>
            <h2>Welcome, {user['name']}!</h2>
            <p>Your account has been successfully created.</p>
            <p><strong>Email:</strong> {user['email']}</p>
            <p>You can now login and start booking venues for your events.</p>
            <br>
            <p>Best regards,<br>Smart Event Venue Booking Team</p>
        </body>
    </html>
    """
    
    return send_email(user['email'], subject, body, is_html=True, email_type="registration")


def send_registration_confirmation_with_status(user):
    """Send registration confirmation and return delivery metadata."""
    subject = "Welcome to Smart Event Venue Booking System"

    body = f"""
    <html>
        <body>
            <h2>Welcome, {user['name']}!</h2>
            <p>Your account has been successfully created.</p>
            <p><strong>Email:</strong> {user['email']}</p>
            <p>You can now login and start booking venues for your events.</p>
            <br>
            <p>Best regards,<br>Smart Event Venue Booking Team</p>
        </body>
    </html>
    """

    return send_email_with_status(user['email'], subject, body, is_html=True, email_type="registration")

def send_booking_confirmation(booking):
    """Send booking confirmation email"""
    subject = f"Booking Confirmed - {booking['venue_name']}"
    
    body = f"""
    <html>
        <body>
            <h2>Booking Confirmation</h2>
            <p>Dear {booking['name']},</p>
            <p>Your booking has been confirmed!</p>
            <br>
            <h3>Booking Details:</h3>
            <table style="border-collapse: collapse; width: 100%;">
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Venue Name:</strong></td>
                    <td style="padding: 8px;">{booking['venue_name']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Location:</strong></td>
                    <td style="padding: 8px;">{booking['location']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Booking Date:</strong></td>
                    <td style="padding: 8px;">{booking['booking_date']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Amount:</strong></td>
                    <td style="padding: 8px;">₹{booking['amount']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Payment Status:</strong></td>
                    <td style="padding: 8px;">{booking['payment_status']}</td>
                </tr>
            </table>
            <br>
            <p>Thank you for booking with us!</p>
            <p>Best regards,<br>Smart Event Venue Booking Team</p>
        </body>
    </html>
    """
    
    return send_email(booking['email'], subject, body, is_html=True, email_type="booking")


def send_booking_confirmation_with_status(booking):
    """Send booking confirmation email with delivery metadata."""
    subject = f"Booking Confirmed - {booking['venue_name']}"

    body = f"""
    <html>
        <body>
            <h2>Booking Confirmation</h2>
            <p>Dear {booking['name']},</p>
            <p>Your booking has been confirmed!</p>
            <br>
            <h3>Booking Details:</h3>
            <table style="border-collapse: collapse; width: 100%;">
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Venue Name:</strong></td>
                    <td style="padding: 8px;">{booking['venue_name']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Location:</strong></td>
                    <td style="padding: 8px;">{booking['location']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Booking Date:</strong></td>
                    <td style="padding: 8px;">{booking['booking_date']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Amount:</strong></td>
                    <td style="padding: 8px;">₹{booking['amount']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Payment Status:</strong></td>
                    <td style="padding: 8px;">{booking['payment_status']}</td>
                </tr>
            </table>
            <br>
            <p>Thank you for booking with us!</p>
            <p>Best regards,<br>Smart Event Venue Booking Team</p>
        </body>
    </html>
    """

    return send_email_with_status(booking['email'], subject, body, is_html=True, email_type="booking")


def send_vendor_booking_notification_with_status(booking):
    """Send booking notification email to venue vendor with customer details."""
    subject = f"New Booking Received - {booking['venue_name']}"

    body = f"""
    <html>
        <body>
            <h2>New Booking Notification</h2>
            <p>Dear Venue Partner,</p>
            <p>You have received a new confirmed booking.</p>
            <br>
            <h3>Booking Details:</h3>
            <table style="border-collapse: collapse; width: 100%;">
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Customer Name:</strong></td>
                    <td style="padding: 8px;">{booking['user_name']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Venue Name:</strong></td>
                    <td style="padding: 8px;">{booking['venue_name']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Location:</strong></td>
                    <td style="padding: 8px;">{booking['location']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Date:</strong></td>
                    <td style="padding: 8px;">{booking['booking_date']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Time:</strong></td>
                    <td style="padding: 8px;">{booking['booking_time']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Customer Email:</strong></td>
                    <td style="padding: 8px;">{booking['user_email']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Customer Phone:</strong></td>
                    <td style="padding: 8px;">{booking['user_phone']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Amount:</strong></td>
                    <td style="padding: 8px;">₹{booking['amount']}</td>
                </tr>
            </table>
            <br>
            <p>Please contact the customer if any additional coordination is needed.</p>
            <p>Best regards,<br>Smart Event Venue Booking Team</p>
        </body>
    </html>
    """

    return send_email_with_status(
        booking['vendor_email'],
        subject,
        body,
        is_html=True,
        email_type="vendor_booking_notification"
    )


def send_new_venue_admin_notification(venue):
    """Notify admin email when a new venue is registered."""
    subject = f"New Venue Registered - {venue['venue_name']}"
    body = f"""
    <html>
        <body>
            <h2>New Venue Registered</h2>
            <p>A new venue has been added to the system.</p>
            <table style="border-collapse: collapse; width: 100%;">
                <tr style="border: 1px solid #ddd;"><td style="padding: 8px;"><strong>Venue Name</strong></td><td style="padding: 8px;">{venue['venue_name']}</td></tr>
                <tr style="border: 1px solid #ddd;"><td style="padding: 8px;"><strong>Location</strong></td><td style="padding: 8px;">{venue['location']}</td></tr>
                <tr style="border: 1px solid #ddd;"><td style="padding: 8px;"><strong>Capacity</strong></td><td style="padding: 8px;">{venue['capacity']}</td></tr>
                <tr style="border: 1px solid #ddd;"><td style="padding: 8px;"><strong>Price</strong></td><td style="padding: 8px;">₹{venue['price']}</td></tr>
                <tr style="border: 1px solid #ddd;"><td style="padding: 8px;"><strong>Rating</strong></td><td style="padding: 8px;">{venue.get('rating', 'N/A')}</td></tr>
            </table>
        </body>
    </html>
    """

    return send_email_with_status(ADMIN_EMAIL, subject, body, is_html=True, email_type="admin_new_venue")

def send_payment_reminder(booking):
    """Send payment reminder email"""
    subject = f"Payment Reminder - {booking['venue_name']}"
    
    body = f"""
    <html>
        <body>
            <h2>Payment Reminder</h2>
            <p>Dear {booking['name']},</p>
            <p>This is a reminder that your booking payment is pending.</p>
            <br>
            <p><strong>Venue:</strong> {booking['venue_name']}</p>
            <p><strong>Date:</strong> {booking['booking_date']}</p>
            <p><strong>Amount Due:</strong> ₹{booking['amount']}</p>
            <br>
            <p>Please complete your payment to confirm your booking.</p>
            <p>Best regards,<br>Smart Event Venue Booking Team</p>
        </body>
    </html>
    """
    
    return send_email(booking['email'], subject, body, is_html=True)

def send_cancellation_confirmation(booking):
    """Send booking cancellation confirmation email"""
    subject = f"Booking Cancelled - {booking['venue_name']}"
    
    body = f"""
    <html>
        <body>
            <h2>Booking Cancelled</h2>
            <p>Dear {booking['name']},</p>
            <p>Your booking has been cancelled.</p>
            <br>
            <p><strong>Venue:</strong> {booking['venue_name']}</p>
            <p><strong>Date:</strong> {booking['booking_date']}</p>
            <br>
            <p>If you have any questions, please contact us.</p>
            <p>Best regards,<br>Smart Event Venue Booking Team</p>
        </body>
    </html>
    """
    
    return send_email(booking['email'], subject, body, is_html=True)


def send_admin_notification_email(recipient, subject, message, audience_label="User"):
    """Send admin notification email to users/vendors and return delivery metadata."""
    recipient_name = recipient.get('name') or recipient.get('email') or audience_label
    body = f"""
    <html>
        <body>
            <h2>New Message From Admin</h2>
            <p>Dear {recipient_name},</p>
            <p>You have received a new notification from Smart Event Venue Booking administration.</p>
            <div style="border: 1px solid #ddd; border-radius: 6px; padding: 12px; margin: 10px 0; background: #fafafa;">
                <p style="margin: 0 0 6px 0;"><strong>Subject:</strong> {subject}</p>
                <p style="margin: 0;"><strong>Message:</strong></p>
                <p style="margin: 6px 0 0 0; white-space: pre-line;">{message}</p>
            </div>
            <p>Best regards,<br>Admin Team<br>Smart Event Venue Booking</p>
        </body>
    </html>
    """

    return send_email_with_status(
        recipient['email'],
        subject,
        body,
        is_html=True,
        email_type=f"admin_notification_{audience_label.lower()}"
    )


def send_feedback_request_email_with_status(feedback_request):
    """Send post-event feedback request email with delivery metadata."""
    feedback_url = f"{FRONTEND_URL.rstrip('/')}/feedback.html?booking_id={feedback_request['booking_id']}"
    subject = f"How was your event at {feedback_request['venue_name']}?"

    body = f"""
    <html>
        <body>
            <h2>We Value Your Feedback</h2>
            <p>Dear {feedback_request['name']},</p>
            <p>Thank you for booking with Smart Event Venue Booking.</p>
            <p>Your event at <strong>{feedback_request['venue_name']}</strong> has been completed. Please share your feedback.</p>

            <table style="border-collapse: collapse; width: 100%; margin: 12px 0;">
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Booking ID</strong></td>
                    <td style="padding: 8px;">{feedback_request['booking_id']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Venue</strong></td>
                    <td style="padding: 8px;">{feedback_request['venue_name']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Event Date</strong></td>
                    <td style="padding: 8px;">{feedback_request['start_date']} to {feedback_request['end_date']}</td>
                </tr>
            </table>

            <p>
                <a href="{feedback_url}" style="display: inline-block; background: #0d6efd; color: #fff; text-decoration: none; padding: 10px 16px; border-radius: 6px;">
                    Submit Feedback
                </a>
            </p>

            <p>If the button does not work, copy this link in your browser:</p>
            <p>{feedback_url}</p>

            <p>Best regards,<br>Smart Event Venue Booking Team</p>
        </body>
    </html>
    """

    return send_email_with_status(
        feedback_request['email'],
        subject,
        body,
        is_html=True,
        email_type='feedback_request'
    )

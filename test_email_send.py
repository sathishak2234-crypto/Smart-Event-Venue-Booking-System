"""
Test script to verify Gmail email sending configuration
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from config import EMAIL_HOST, EMAIL_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD  # type: ignore

print("=" * 60)
print("GMAIL EMAIL CONFIGURATION TEST")
print("=" * 60)

print("\n1. Configuration Check:")
print(f"   Email Host: {EMAIL_HOST}")
print(f"   Email Port: {EMAIL_PORT}")
print(f"   Email Address: {EMAIL_ADDRESS}")
print(f"   Password: {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 'NOT SET'}")

if EMAIL_ADDRESS == 'your-email@gmail.com' or EMAIL_PASSWORD == 'your-app-password':
    print("\n   ❌ ERROR: Email credentials not configured!")
    print("   Please update .env file with:")
    print("   - EMAIL_ADDRESS=your-gmail@gmail.com")
    print("   - EMAIL_PASSWORD=your-16-char-app-password")
    sys.exit(1)

print("\n2. Testing SMTP Connection...")
try:
    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    print("   ✓ SMTP server connected")
    
    print("\n3. Testing STARTTLS...")
    server.starttls()
    print("   ✓ STARTTLS successful")
    
    print("\n4. Testing Gmail Authentication...")
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    print(f"   ✓ Authentication successful as {EMAIL_ADDRESS}")
    
    print("\n5. Sending Test Email...")
    # Create test email
    message = MIMEMultipart('alternative')
    message['Subject'] = "Test Email - Smart Venue Booking System"
    message['From'] = EMAIL_ADDRESS
    message['To'] = EMAIL_ADDRESS
    
    html_body = """
    <html>
        <body>
            <h2>Test Email Success! ✓</h2>
            <p>This is a test email from your Smart Event Venue Booking System.</p>
            <p>If you received this email, your Gmail SMTP configuration is working correctly.</p>
            <br>
            <p><strong>Configuration Details:</strong></p>
            <ul>
                <li>Host: smtp.gmail.com</li>
                <li>Port: 587</li>
                <li>Email: """ + EMAIL_ADDRESS + """</li>
            </ul>
            <br>
            <p>Your booking confirmation emails should now work properly!</p>
            <br>
            <p>Best regards,<br>Smart Venue Booking System</p>
        </body>
    </html>
    """
    
    message.attach(MIMEText(html_body, 'html'))
    
    server.send_message(message)
    print(f"   ✓ Test email sent successfully to {EMAIL_ADDRESS}")
    
    server.quit()
    print("\n6. SMTP Connection Closed")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYour Gmail configuration is working correctly.")
    print("Booking confirmation emails should now be sent successfully.")
    print("\nNext Steps:")
    print("1. Make sure your Flask backend server is running")
    print("2. Test by making a booking")
    print("3. Check your registered email for confirmation")
    print("\nIf you don't receive emails:")
    print("- Check spam/junk folder")
    print("- Verify .env file has correct Gmail credentials")
    print("- Check backend console for any error messages")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n   ❌ Authentication Failed! Error: {str(e)}")
    print("\n   SOLUTIONS:")
    print("   1. Verify email address is correct in .env")
    print("   2. Use App Password (not your Gmail password)")
    print("   3. Enable 2-Factor Authentication in Gmail")
    print("   4. Generate new App Password at:")
    print("      https://myaccount.google.com/apppasswords")
    sys.exit(1)
    
except smtplib.SMTPException as e:
    print(f"\n   ❌ SMTP Error: {str(e)}")
    print("\n   SOLUTIONS:")
    print("   1. Check internet connection")
    print("   2. Verify firewall/antivirus is not blocking port 587")
    print("   3. Try different SMTP port (usually 587 or 465)")
    sys.exit(1)
    
except Exception as e:
    print(f"\n   ❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

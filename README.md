# Smart Event Venue Booking System

A complete full-stack solution for booking event venues online. Built with Flask backend, MySQL database, and vanilla JavaScript frontend.

## Features

✅ **User Management**
- User Registration & Login
- JWT Authentication
- Profile Management

✅ **Venue Management**
- Browse & Filter Venues
- View Detailed Information
- Availability Calendar
- Price Comparison

✅ **Booking System**
- Calendar-based Date Selection
- Real-time Availability Check
- Booking Confirmation

✅ **Payment Integration**
- Razorpay Payment Gateway
- Payment Verification
- Transaction History

✅ **Email Notifications**
- Registration Confirmation
- Booking Confirmation
- Payment Reminders

✅ **Dashboard & Analytics**
- Booking Statistics
- Revenue Charts
- Recent Bookings

✅ **Feedback System**
- Venue Ratings
- User Reviews

## Project Structure

```
smart-event-venue-booking/
├── frontend/
│   ├── login.html              # Authentication page
│   ├── home.html               # Home page with featured venues
│   ├── venues.html             # Venue listing & filtering
│   ├── booking.html            # Booking with calendar
│   ├── dashboard.html          # User dashboard with stats
│   ├── feedback.html           # Feedback & ratings
│   ├── css/
│   │   └── style.css          # Main styling
│   └── js/
│       └── app.js             # Main JavaScript app
│
├── backend/
│   ├── server.py              # Flask main app
│   ├── config.py              # Configuration
│   ├── db.py                  # Database connection
│   ├── mailer.py              # Email service
│   └── routes/
│       ├── auth.py            # Authentication routes
│       ├── venues.py          # Venue routes
│       ├── bookings.py        # Booking routes
│       ├── payment.py         # Payment routes
│       └── feedback.py        # Feedback routes
│
├── database/
│   └── venue_booking.sql      # Database schema
│
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file

```

## Technology Stack

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling (Bootstrap 5)
- **JavaScript** - Interactivity
- **FullCalendar.js** - Calendar widget
- **Chart.js** - Charts & graphs
- **Font Awesome** - Icons

### Backend
- **Python 3.x** - Language
- **Flask** - Web framework
- **MySQL** - Database
- **Flask-CORS** - CORS handling
- **JWT** - Authentication
- **Razorpay** - Payment gateway
- **Nodemailer** - Email service

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd smart-event-venue-booking
```

### 2. Setup Database

**Create MySQL Database:**
```bash
# Open MySQL shell
mysql -u root -p

# Run the SQL file
source database/venue_booking.sql;
```

### 3. Setup Backend

**Create Virtual Environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Configure Environment:**
```bash
# Copy and edit .env file
cp .env.example .env

# Edit .env with your configuration
# - MySQL credentials
# - Email settings (Gmail App Password)
# - Razorpay API keys
```

**Run Flask Server:**
```bash
cd backend
python server.py
```

Backend will run on `http://localhost:5000`

### 4. Setup Frontend

**Simple HTTP Server:**
```bash
# Windows
cd frontend
python -m http.server 3000

# Mac/Linux
cd frontend
python3 -m http.server 3000
```

Frontend will run on `http://localhost:3000`

Or use VS Code Live Server extension for live reload.

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### Venues
- `GET /api/venues/` - Get all venues with filters
- `GET /api/venues/<id>` - Get venue details
- `GET /api/venues/availability/<id>` - Check availability
- `GET /api/venues/calendar/<id>` - Get booked dates

### Bookings
- `POST /api/bookings/` - Create booking
- `GET /api/bookings/` - Get user bookings
- `GET /api/bookings/<id>` - Get booking details
- `POST /api/bookings/<id>/cancel` - Cancel booking
- `GET /api/bookings/dashboard/stats` - Get dashboard stats

### Payments
- `POST /api/payment/create-order` - Create Razorpay order
- `POST /api/payment/verify-payment` - Verify payment
- `GET /api/payment/payment-history` - Get payment history

### Feedback
- `POST /api/feedback/` - Submit feedback
- `GET /api/feedback/` - Get all feedback
- `GET /api/feedback/<venue_id>/rating` - Get venue rating

## Configuration

### Email Setup (Gmail)

1. Enable 2-Factor Authentication
2. Create App Password at https://myaccount.google.com/apppasswords
3. Add to `.env`:
```
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-password
```

### Razorpay Setup (Payment)

1. Create account at https://razorpay.com
2. Get API Keys from Dashboard
3. Add to `.env`:
```
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
```

4. Update frontend `app.js`:
```javascript
key: 'YOUR_RAZORPAY_KEY_ID'  // Line ~425
```

## Database Schema

### Users Table
```sql
- id (INT, Primary Key)
- name (VARCHAR)
- email (VARCHAR, Unique)
- password (VARCHAR)
- phone (VARCHAR)
- created_at (TIMESTAMP)
```

### Venues Table
```sql
- id (INT, Primary Key)
- venue_name (VARCHAR)
- location (VARCHAR)
- capacity (INT)
- price (INT)
- facilities (VARCHAR)
- image_url (VARCHAR)
- description (TEXT)
- created_at (TIMESTAMP)
```

### Bookings Table
```sql
- id (INT, Primary Key)
- user_id (INT, FK)
- venue_id (INT, FK)
- booking_date (DATE)
- payment_status (VARCHAR)
- booking_status (VARCHAR)
- amount (INT)
- payment_id (VARCHAR)
- created_at (TIMESTAMP)
```

### Feedback Table
```sql
- id (INT, Primary Key)
- user_id (INT, FK)
- booking_id (INT, FK)
- message (TEXT)
- rating (INT, 1-5)
- created_at (TIMESTAMP)
```

## Usage

### User Journey

1. **Register/Login**
   - Go to `login.html`
   - Create account or login
   - Token stored in localStorage

2. **Browse Venues**
   - View all venues on home page
   - Filter by price, location
   - View venue details

3. **Book Venue**
   - Select venue
   - Choose date from calendar
   - Proceed to payment
   - Complete Razorpay transaction

4. **Dashboard**
   - View booking statistics
   - See recent bookings
   - Track spending
   - View booking charts

5. **Feedback**
   - Rate venues (1-5 stars)
   - Write reviews
   - View other reviews

## Sample Test Credentials

After running `venue_booking.sql`:

```
Email: user@example.com
Password: password123
```

(Created by seed data in database)

## Troubleshooting

### Issue: CORS Errors
**Solution:** Ensure Flask-CORS is installed and backend is running on port 5000

### Issue: Database Connection Failed
**Solution:** Check MySQL is running and credentials in `.env` are correct

### Issue: Email not sending
**Solution:** 
- Enable Gmail 2FA
- Use App Password (not regular password)
- Check firewall/antivirus settings

### Issue: Payment not working
**Solution:**
- Update Razorpay key in `app.js`
- Use test keys for development
- Ensure payment gateway is configured

## Future Enhancements

- [ ] Admin panel for venue management
- [ ] Advanced analytics & reports
- [ ] Booking cancellation with refunds
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Advanced search filters
- [ ] Venue comparison tool
- [ ] Photo gallery for venues
- [ ] Reviews with attachments
- [ ] Email reminders for bookings

## Security Notes

⚠️ **Important for Production:**

1. Change `SECRET_KEY` in config.py
2. Use environment variables for sensitive data
3. Enable HTTPS
4. Use strong database passwords
5. Implement rate limiting
6. Add input validation
7. Use password hashing (already implemented with Werkzeug)
8. Add CSRF protection
9. Validate all user inputs
10. Implement logging

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please:
1. Check the troubleshooting section
2. Review API documentation
3. Check browser console for errors
4. Review server logs

## Authors

- Smart Event Venue Booking System Team
- Educational Purpose - College Project

---

**Created:** 2026
**Version:** 1.0.0
**Status:** Active

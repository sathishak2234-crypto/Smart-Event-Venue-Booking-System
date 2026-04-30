from flask import Blueprint, request, jsonify
from config import SECRET_KEY
from functools import wraps
import jwt
import os
import sqlite3 as sq
import logging
from mailer import send_new_venue_admin_notification, send_admin_notification_email
from mailer import send_feedback_request_email_with_status

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
logger = logging.getLogger(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'venue_booking.db')


# Admin auth check decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401

        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            conn = sq.connect(DB_PATH)
            conn.row_factory = sq.Row
            cursor = conn.cursor()
            cursor.execute('SELECT id, is_admin FROM users WHERE id = ?', (decoded['user_id'],))
            user = cursor.fetchone()
            conn.close()

            if not user or not user['is_admin']:
                return jsonify({'error': 'Unauthorized'}), 403

            request.current_user_id = user['id']
        except Exception as e:
            return jsonify({'error': str(e)}), 401

        return f(*args, **kwargs)
    return decorated_function


# Get all venues (admin view with stats)
@admin_bp.route('/venues', methods=['GET'])
@admin_required
def get_venues():
    try:
        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, venue_name, location, capacity, price, isAC, rating, facilities, image_url, thumbnail_url FROM venues'
        )
        venues_rows = cursor.fetchall()
        conn.close()

        venue_list = []
        total_price = 0
        total_rating = 0
        ac_count = 0

        for venue in venues_rows:
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
                'thumbnail_url': venue['thumbnail_url']
            }
            venue_list.append(venue_dict)
            total_price += venue['price']
            total_rating += venue['rating']
            if venue['isAC']:
                ac_count += 1

        avg_price = total_price / len(venue_list) if venue_list else 0
        avg_rating = total_rating / len(venue_list) if venue_list else 0

        return jsonify({
            'venues': venue_list,
            'stats': {
                'total': len(venue_list),
                'ac_count': ac_count,
                'avg_price': round(avg_price),
                'avg_rating': round(avg_rating, 2)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Get single venue
@admin_bp.route('/venues/<int:venue_id>', methods=['GET'])
@admin_required
def get_venue(venue_id):
    try:
        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, venue_name, location, capacity, price, isAC, rating, facilities, image_url, thumbnail_url FROM venues WHERE id = ?',
            (venue_id,)
        )
        venue = cursor.fetchone()
        conn.close()

        if not venue:
            return jsonify({'error': 'Venue not found'}), 404

        return jsonify({
            'venue': {
                'id': venue['id'],
                'venue_name': venue['venue_name'],
                'location': venue['location'],
                'capacity': venue['capacity'],
                'price': venue['price'],
                'isAC': venue['isAC'],
                'rating': venue['rating'],
                'facilities': venue['facilities'],
                'image_url': venue['image_url'],
                'thumbnail_url': venue['thumbnail_url']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Add new venue
@admin_bp.route('/venues', methods=['POST'])
@admin_required
def add_venue():
    data = request.json

    required_fields = ['venue_name', 'location', 'capacity', 'price', 'rating']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        conn = sq.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO venues (venue_name, location, capacity, price, isAC, rating, facilities, image_url, thumbnail_url, owner_email)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                data['venue_name'],
                data['location'],
                data['capacity'],
                data['price'],
                data.get('isAC', 0),
                data['rating'],
                data.get('facilities', ''),
                data.get('image_url', ''),
                data.get('thumbnail_url', ''),
                data.get('owner_email', '')
            )
        )
        venue_payload = {
            'venue_name': data['venue_name'],
            'location': data['location'],
            'capacity': data['capacity'],
            'price': data['price'],
            'rating': data.get('rating', 'N/A')
        }

        conn.commit()
        conn.close()

        # Notify admin email on new venue registration (non-blocking)
        try:
            email_result = send_new_venue_admin_notification(venue_payload)
            if email_result['success']:
                logger.info(f"Admin notified for new venue: {data['venue_name']}")
            else:
                logger.warning(
                    f"Admin notification failed for venue {data['venue_name']}: {email_result.get('error')}"
                )
        except Exception as email_error:
            logger.error(f"Error sending admin new venue notification: {str(email_error)}")

        return jsonify({'message': 'Venue added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Update venue
@admin_bp.route('/venues/<int:venue_id>', methods=['PUT'])
@admin_required
def update_venue(venue_id):
    data = request.json

    try:
        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM venues WHERE id = ?', (venue_id,))
        venue = cursor.fetchone()

        if not venue:
            conn.close()
            return jsonify({'error': 'Venue not found'}), 404

        updates = []
        params = []

        if 'venue_name' in data:
            updates.append('venue_name = ?')
            params.append(data['venue_name'])
        if 'location' in data:
            updates.append('location = ?')
            params.append(data['location'])
        if 'capacity' in data:
            updates.append('capacity = ?')
            params.append(data['capacity'])
        if 'price' in data:
            updates.append('price = ?')
            params.append(data['price'])
        if 'isAC' in data:
            updates.append('isAC = ?')
            params.append(data['isAC'])
        if 'rating' in data:
            updates.append('rating = ?')
            params.append(data['rating'])
        if 'facilities' in data:
            updates.append('facilities = ?')
            params.append(data['facilities'])
        if 'image_url' in data:
            updates.append('image_url = ?')
            params.append(data['image_url'])
        if 'thumbnail_url' in data:
            updates.append('thumbnail_url = ?')
            params.append(data['thumbnail_url'])

        if not updates:
            conn.close()
            return jsonify({'error': 'No fields to update'}), 400

        params.append(venue_id)
        query = f"UPDATE venues SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        conn.close()

        return jsonify({'message': 'Venue updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Delete venue
@admin_bp.route('/venues/<int:venue_id>', methods=['DELETE'])
@admin_required
def delete_venue(venue_id):
    try:
        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM venues WHERE id = ?', (venue_id,))
        venue = cursor.fetchone()

        if not venue:
            conn.close()
            return jsonify({'error': 'Venue not found'}), 404

        cursor.execute('DELETE FROM venues WHERE id = ?', (venue_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Venue deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Get all bookings (admin view)
@admin_bp.route('/bookings', methods=['GET'])
@admin_required
def get_all_bookings():
    try:
        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT b.id, b.user_id, u.name as user_name, u.email, b.venue_id, v.venue_name,
                      b.booking_date, b.start_date, b.end_date, b.start_time, b.end_time,
                      b.payment_status, b.booking_status, b.amount,
                      b.feedback_request_sent, b.feedback_request_status, b.feedback_request_sent_at
               FROM bookings b
               JOIN users u ON b.user_id = u.id
               JOIN venues v ON b.venue_id = v.id
               ORDER BY b.created_at DESC'''
        )
        bookings = cursor.fetchall()
        conn.close()

        booking_list = []
        for booking in bookings:
            booking_list.append({
                'id': booking['id'],
                'user_id': booking['user_id'],
                'user_name': booking['user_name'],
                'user_email': booking['email'],
                'venue_id': booking['venue_id'],
                'venue_name': booking['venue_name'],
                'booking_date': booking['booking_date'],
                'start_date': booking['start_date'] or booking['booking_date'],
                'end_date': booking['end_date'] or booking['booking_date'],
                'start_time': booking['start_time'],
                'end_time': booking['end_time'],
                'payment_status': booking['payment_status'],
                'booking_status': booking['booking_status'],
                'amount': booking['amount'],
                'feedback_request_sent': booking['feedback_request_sent'],
                'feedback_request_status': booking['feedback_request_status'],
                'feedback_request_sent_at': booking['feedback_request_sent_at']
            })

        return jsonify({'bookings': booking_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Send feedback request emails for completed bookings
@admin_bp.route('/bookings/send-feedback-requests', methods=['POST'])
@admin_required
def send_feedback_requests_for_completed_bookings():
    try:
        data = request.get_json(silent=True) or {}
        force_send = bool(data.get('force', False))
        booking_ids = data.get('booking_ids') or []

        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()

        base_query = '''
            SELECT b.id as booking_id, b.user_id, b.venue_id,
                   u.name, u.email,
                   v.venue_name,
                   COALESCE(b.start_date, b.booking_date) as start_date,
                   COALESCE(b.end_date, b.booking_date) as end_date,
                   b.feedback_request_sent,
                   f.id as feedback_id
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN venues v ON b.venue_id = v.id
            LEFT JOIN feedback f ON f.booking_id = b.id
            WHERE date(COALESCE(b.end_date, b.booking_date)) < date('now')
              AND b.booking_status IN ('CONFIRMED', 'COMPLETED')
              AND b.payment_status = 'COMPLETED'
        '''

        params = []
        if booking_ids:
            placeholders = ','.join(['?'] * len(booking_ids))
            base_query += f' AND b.id IN ({placeholders})'
            params.extend(booking_ids)

        cursor.execute(base_query, params)
        rows = cursor.fetchall()

        sent_count = 0
        skipped_count = 0
        failed_count = 0
        processed_booking_ids = []

        for row in rows:
            booking_id = row['booking_id']

            if row['feedback_id']:
                skipped_count += 1
                continue

            if row['feedback_request_sent'] and not force_send:
                skipped_count += 1
                continue

            email_result = send_feedback_request_email_with_status({
                'booking_id': booking_id,
                'name': row['name'],
                'email': row['email'],
                'venue_name': row['venue_name'],
                'start_date': row['start_date'],
                'end_date': row['end_date']
            })

            status = 'SENT' if email_result.get('success') else 'FAILED'
            sent_flag = 1 if email_result.get('success') else 0
            sent_at = 'CURRENT_TIMESTAMP' if email_result.get('success') else 'NULL'

            cursor.execute(
                f'''UPDATE bookings
                    SET feedback_request_sent = ?,
                        feedback_request_status = ?,
                        feedback_request_sent_at = {sent_at}
                    WHERE id = ?''',
                (sent_flag, status, booking_id)
            )

            processed_booking_ids.append(booking_id)
            if email_result.get('success'):
                sent_count += 1
            else:
                failed_count += 1

        conn.commit()
        conn.close()

        return jsonify({
            'message': 'Feedback request processing completed',
            'eligible_count': len(rows),
            'processed_count': len(processed_booking_ids),
            'sent_count': sent_count,
            'failed_count': failed_count,
            'skipped_count': skipped_count,
            'booking_ids': processed_booking_ids
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Get revenue report
@admin_bp.route('/revenue', methods=['GET'])
@admin_required
def get_revenue():
    try:
        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()

        cursor.execute(
            'SELECT SUM(amount), COUNT(*), booking_status FROM bookings GROUP BY booking_status'
        )
        bookings = cursor.fetchall()

        status_revenue = {}
        total_revenue = 0
        total_bookings = 0

        for booking in bookings:
            total = booking[0] or 0
            count = booking[1] or 0
            status = booking[2]

            status_revenue[status] = {
                'total': total,
                'count': count
            }

            if status == 'CONFIRMED':
                total_revenue += total
            total_bookings += count

        cursor.execute(
            '''SELECT strftime('%Y-%m', created_at) as month, SUM(amount) as revenue
               FROM bookings WHERE booking_status = 'CONFIRMED'
               GROUP BY month ORDER BY month DESC LIMIT 12'''
        )
        monthly = cursor.fetchall()
        conn.close()

        monthly_data = []
        for row in monthly:
            monthly_data.append({
                'month': row[0],
                'revenue': row[1] or 0
            })

        return jsonify({
            'total_revenue': total_revenue,
            'total_bookings': total_bookings,
            'status_breakdown': status_revenue,
            'monthly_revenue': monthly_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Update booking status/payment
@admin_bp.route('/bookings/<int:booking_id>/status', methods=['PUT'])
@admin_required
def update_booking_status(booking_id):
    try:
        data = request.get_json() or {}
        booking_status = data.get('booking_status')
        payment_status = data.get('payment_status')

        if not booking_status and not payment_status:
            return jsonify({'error': 'No status fields provided'}), 400

        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM bookings WHERE id = ?', (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            conn.close()
            return jsonify({'error': 'Booking not found'}), 404

        updates = []
        params = []
        if booking_status:
            updates.append('booking_status = ?')
            params.append(booking_status)
        if payment_status:
            updates.append('payment_status = ?')
            params.append(payment_status)

        params.append(booking_id)
        cursor.execute(f"UPDATE bookings SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        conn.close()

        return jsonify({'message': 'Booking status updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Get user analytics
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    try:
        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, name, email, phone, is_admin, created_at,
                      (SELECT COUNT(*) FROM bookings WHERE user_id = users.id) as booking_count
               FROM users
               ORDER BY created_at DESC'''
        )
        users = cursor.fetchall()
        conn.close()

        user_list = []
        for user in users:
            user_list.append({
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'phone': user['phone'],
                'is_admin': user['is_admin'],
                'joined': user['created_at'],
                'bookings': user['booking_count']
            })

        return jsonify({
            'total_users': len(user_list),
            'users': user_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Update user profile fields
@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    try:
        data = request.get_json() or {}
        allowed_fields = ['name', 'email', 'phone']

        updates = []
        params = []
        for field in allowed_fields:
            if field in data:
                updates.append(f'{field} = ?')
                params.append(data[field])

        if not updates:
            return jsonify({'error': 'No fields to update'}), 400

        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404

        params.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        conn.close()

        return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Delete non-admin user
@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        if user_id == getattr(request, 'current_user_id', None):
            return jsonify({'error': 'Cannot delete currently logged in admin'}), 400

        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id, is_admin FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        if user['is_admin']:
            conn.close()
            return jsonify({'error': 'Cannot delete admin user'}), 400

        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Vendor list with optional venue mapping
@admin_bp.route('/vendors', methods=['GET'])
@admin_required
def get_vendors():
    try:
        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT vd.id, vd.name, vd.email, vd.phone, vd.venue_id, vd.is_active, vd.created_at,
                      v.venue_name
               FROM vendors vd
               LEFT JOIN venues v ON vd.venue_id = v.id
               ORDER BY vd.created_at DESC'''
        )
        vendors = cursor.fetchall()
        conn.close()

        return jsonify({
            'vendors': [
                {
                    'id': vendor['id'],
                    'name': vendor['name'],
                    'email': vendor['email'],
                    'phone': vendor['phone'],
                    'venue_id': vendor['venue_id'],
                    'venue_name': vendor['venue_name'],
                    'is_active': vendor['is_active'],
                    'created_at': vendor['created_at']
                }
                for vendor in vendors
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Create vendor
@admin_bp.route('/vendors', methods=['POST'])
@admin_required
def add_vendor():
    try:
        data = request.get_json() or {}
        if not data.get('name') or not data.get('email'):
            return jsonify({'error': 'Vendor name and email are required'}), 400

        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO vendors (name, email, phone, venue_id, is_active) VALUES (?, ?, ?, ?, ?)',
            (
                data['name'].strip(),
                data['email'].strip().lower(),
                data.get('phone', '').strip(),
                data.get('venue_id'),
                int(data.get('is_active', 1))
            )
        )
        vendor_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({'message': 'Vendor added successfully', 'vendor_id': vendor_id}), 201
    except sq.IntegrityError:
        return jsonify({'error': 'Vendor email already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Update vendor
@admin_bp.route('/vendors/<int:vendor_id>', methods=['PUT'])
@admin_required
def update_vendor(vendor_id):
    try:
        data = request.get_json() or {}
        allowed_fields = ['name', 'email', 'phone', 'venue_id', 'is_active']

        updates = []
        params = []
        for field in allowed_fields:
            if field in data:
                updates.append(f'{field} = ?')
                value = data[field]
                if field == 'email' and value:
                    value = str(value).strip().lower()
                params.append(value)

        if not updates:
            return jsonify({'error': 'No fields to update'}), 400

        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM vendors WHERE id = ?', (vendor_id,))
        vendor = cursor.fetchone()
        if not vendor:
            conn.close()
            return jsonify({'error': 'Vendor not found'}), 404

        params.append(vendor_id)
        cursor.execute(f"UPDATE vendors SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        conn.close()

        return jsonify({'message': 'Vendor updated successfully'})
    except sq.IntegrityError:
        return jsonify({'error': 'Vendor email already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Delete vendor
@admin_bp.route('/vendors/<int:vendor_id>', methods=['DELETE'])
@admin_required
def delete_vendor(vendor_id):
    try:
        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM vendors WHERE id = ?', (vendor_id,))
        vendor = cursor.fetchone()
        if not vendor:
            conn.close()
            return jsonify({'error': 'Vendor not found'}), 404

        cursor.execute('DELETE FROM vendors WHERE id = ?', (vendor_id,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Vendor deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Send admin notification email/message to users/vendors
@admin_bp.route('/notifications/send', methods=['POST'])
@admin_required
def send_notifications():
    try:
        data = request.get_json() or {}
        target = (data.get('target') or '').strip().lower()
        subject = (data.get('subject') or '').strip()
        message = (data.get('message') or '').strip()
        recipient_ids = data.get('recipient_ids') or []
        send_email = bool(data.get('send_email', True))

        if target not in ('users', 'vendors', 'all'):
            return jsonify({'error': 'target must be users, vendors, or all'}), 400
        if not subject or not message:
            return jsonify({'error': 'subject and message are required'}), 400

        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()

        recipients = []

        if target in ('users', 'all'):
            query = 'SELECT id, name, email FROM users WHERE is_admin = 0'
            params = []
            if recipient_ids:
                placeholders = ','.join(['?'] * len(recipient_ids))
                query += f' AND id IN ({placeholders})'
                params.extend(recipient_ids)
            cursor.execute(query, params)
            user_rows = cursor.fetchall()
            recipients.extend([
                {'type': 'users', 'id': row['id'], 'name': row['name'], 'email': row['email']}
                for row in user_rows if row['email']
            ])

        if target in ('vendors', 'all'):
            query = 'SELECT id, name, email FROM vendors WHERE is_active = 1'
            params = []
            if recipient_ids and target == 'vendors':
                placeholders = ','.join(['?'] * len(recipient_ids))
                query += f' AND id IN ({placeholders})'
                params.extend(recipient_ids)
            cursor.execute(query, params)
            vendor_rows = cursor.fetchall()
            recipients.extend([
                {'type': 'vendors', 'id': row['id'], 'name': row['name'], 'email': row['email']}
                for row in vendor_rows if row['email']
            ])

        if not recipients:
            conn.close()
            return jsonify({'error': 'No recipients found for selected target'}), 404

        sent_count = 0
        failed_count = 0
        log_ids = []

        for recipient in recipients:
            status = 'SKIPPED'
            if send_email:
                email_result = send_admin_notification_email(
                    recipient,
                    subject,
                    message,
                    audience_label='Vendor' if recipient['type'] == 'vendors' else 'User'
                )
                status = 'SENT' if email_result.get('success') else 'FAILED'
            try:
                cursor.execute(
                    '''INSERT INTO notification_logs
                       (target_type, recipient_name, recipient_email, subject, message, email_status, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (
                        recipient['type'],
                        recipient['name'],
                        recipient['email'],
                        subject,
                        message,
                        status,
                        getattr(request, 'current_user_id', None)
                    )
                )
                log_ids.append(cursor.lastrowid)
            except Exception as log_error:
                logger.error(f'Failed to write notification log: {log_error}')

            if status == 'SENT':
                sent_count += 1
            elif status == 'FAILED':
                failed_count += 1

        conn.commit()
        conn.close()

        return jsonify({
            'message': 'Notifications processed',
            'target': target,
            'recipient_count': len(recipients),
            'sent_count': sent_count,
            'failed_count': failed_count,
            'log_ids': log_ids
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# View latest notification logs
@admin_bp.route('/notifications/logs', methods=['GET'])
@admin_required
def get_notification_logs():
    try:
        limit = request.args.get('limit', default=100, type=int)
        if limit <= 0:
            limit = 100

        conn = sq.connect(DB_PATH)
        conn.row_factory = sq.Row
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, target_type, recipient_name, recipient_email, subject, message,
                      email_status, created_by, created_at
               FROM notification_logs
               ORDER BY created_at DESC
               LIMIT ?''',
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()

        return jsonify({'logs': [dict(row) for row in rows]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Upload venue image
@admin_bp.route('/upload-image', methods=['POST'])
@admin_required
def upload_image():
    """Upload venue image and return URL"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Allowed image extensions
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF, WEBP allowed'}), 400

        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.path.dirname(__file__), '../uploads')
        os.makedirs(uploads_dir, exist_ok=True)

        # Generate unique filename
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + file.filename.replace(' ', '_')

        filepath = os.path.join(uploads_dir, filename)
        file.save(filepath)

        image_url = f'/uploads/{filename}'

        return jsonify({
            'message': 'Image uploaded successfully',
            'image_url': image_url,
            'filename': filename
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Upload venue thumbnail (smaller version)
@admin_bp.route('/upload-thumbnail', methods=['POST'])
@admin_required
def upload_thumbnail():
    """Upload venue thumbnail and return URL"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF, WEBP allowed'}), 400

        uploads_dir = os.path.join(os.path.dirname(__file__), '../uploads')
        os.makedirs(uploads_dir, exist_ok=True)

        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = 'thumb_' + timestamp + file.filename.replace(' ', '_')

        filepath = os.path.join(uploads_dir, filename)
        file.save(filepath)

        thumbnail_url = f'/uploads/{filename}'

        return jsonify({
            'message': 'Thumbnail uploaded successfully',
            'thumbnail_url': thumbnail_url,
            'filename': filename
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

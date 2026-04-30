import sqlite3
import os
import re
from urllib.parse import quote

# SQLite database for testing (no MySQL required)
DB_PATH = os.path.join(os.path.dirname(__file__), 'venue_booking.db')
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
IMAGE_BASE_URL = os.getenv('BACKEND_IMAGE_BASE_URL', 'http://localhost:5000/images')

VENUE_FACILITY_COLUMNS = {
    'seating_capacity': 'INTEGER DEFAULT 0',
    'dining_capacity': 'INTEGER DEFAULT 0',
    'dining_type': "TEXT DEFAULT 'veg'",
    'buffet_available': 'INTEGER DEFAULT 0',
    'kitchen_specialty': "TEXT DEFAULT 'Classic'",
    'kitchen_food_support': "TEXT DEFAULT 'Both'",
    'kitchen_fuel_type': "TEXT DEFAULT 'Gas Cylinder'",
    'gas_cylinder_count': 'INTEGER DEFAULT 0',
    'restrooms_count': 'INTEGER DEFAULT 0',
    'bathrooms_count': 'INTEGER DEFAULT 0',
    'water_taps_count': 'INTEGER DEFAULT 0',
    'two_wheeler_parking_capacity': 'INTEGER DEFAULT 0',
    'car_parking_available': 'INTEGER DEFAULT 0',
    'max_car_parking_capacity': 'INTEGER DEFAULT 0',
    'groom_rooms_count': 'INTEGER DEFAULT 0',
    'bride_rooms_count': 'INTEGER DEFAULT 0',
    'owner_mobile': 'TEXT',
    'owner_name': "TEXT DEFAULT ''",
    'owner_email': "TEXT DEFAULT ''",
    'advance_amount': 'INTEGER DEFAULT 0',
    'advance_details': "TEXT DEFAULT ''",
    'timing_type': "TEXT DEFAULT '12hrs'",
    'disability_ramp_available': 'INTEGER DEFAULT 0',
    'address': "TEXT DEFAULT ''"
}


def normalize_venue_name(value):
    """Normalize venue and image names for stable matching."""
    normalized = value.lower().strip()
    normalized = normalized.replace('a/c', 'ac')
    normalized = re.sub(r'[^a-z0-9]+', '', normalized)
    return normalized


def find_matching_image_filename(venue_name, image_files):
    """Find the best matching image filename for a venue name."""
    exact_stem_map = {
        os.path.splitext(filename)[0].lower().strip(): filename for filename in image_files
    }
    normalized_stem_map = {
        normalize_venue_name(os.path.splitext(filename)[0]): filename for filename in image_files
    }

    manual_aliases = {
        'Dharma Shastha Mandapam': 'Dharma Shastha Kalyana Mandapam.jpg',
        'Meena Mahal A/C': 'Meena Mahal AC.jpg',
        'Srinivasa Mahal A/C': 'Srinivasa Mahal AC.webp',
        'APS Hall A/C': 'APS Hall AC.jpg',
    }

    if venue_name in manual_aliases and manual_aliases[venue_name] in image_files:
        return manual_aliases[venue_name]

    exact_key = venue_name.lower().strip()
    if exact_key in exact_stem_map:
        return exact_stem_map[exact_key]

    normalized_key = normalize_venue_name(venue_name)
    return normalized_stem_map.get(normalized_key)


def sync_venue_image_urls(cursor):
    """Sync venue image_url and thumbnail_url using local images folder filenames."""
    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
    if not os.path.isdir(images_dir):
        print(f"Image directory not found, skipping image sync: {images_dir}")
        return

    image_files = [
        filename
        for filename in os.listdir(images_dir)
        if os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS
    ]

    if not image_files:
        print("No local venue images found to sync")
        return

    cursor.execute('SELECT id, venue_name FROM venues')
    venues = cursor.fetchall()
    updated_count = 0

    for venue in venues:
        venue_id = venue[0]
        venue_name = venue[1]
        matched_filename = find_matching_image_filename(venue_name, image_files)

        if not matched_filename:
            continue

        encoded_filename = quote(matched_filename)
        image_url = f"{IMAGE_BASE_URL}/{encoded_filename}"

        cursor.execute(
            'UPDATE venues SET image_url = ?, thumbnail_url = ? WHERE id = ?',
            (image_url, image_url, venue_id)
        )
        updated_count += 1

    print(f"✓ Synced venue images for {updated_count} venues")


def ensure_venue_facility_columns(cursor):
    """Add extended venue facility columns when upgrading existing databases."""
    cursor.execute("PRAGMA table_info(venues)")
    existing_columns = {column[1] for column in cursor.fetchall()}

    for column_name, column_type in VENUE_FACILITY_COLUMNS.items():
        if column_name not in existing_columns:
            cursor.execute(f'ALTER TABLE venues ADD COLUMN {column_name} {column_type}')
            print(f"✓ Added {column_name} column to venues table")


def build_sample_facility_data(venue):
    """Build deterministic sample facility values so all seeded venues have complete details."""
    venue_id = venue[0]
    venue_name = venue[1]
    location = venue[2]
    base_capacity = int(venue[3] or 0)
    base_price = int(venue[4] or 0)

    seating_capacity = max(base_capacity, 200)
    dining_capacity = max(int(base_capacity * 0.58) + ((venue_id * 13) % 75), 120)
    dining_type = 'veg' if venue_id % 2 == 0 else 'non-veg'
    buffet_available = 1 if venue_id % 4 != 0 else 0
    kitchen_specialty = 'High Quality' if venue_id % 2 == 0 else 'Classic'
    kitchen_food_support = 'Both' if venue_id % 3 == 0 else ('Veg' if venue_id % 3 == 1 else 'Non-Veg')
    kitchen_fuel_type = 'Wood' if venue_id % 5 == 0 else 'Gas Cylinder'
    gas_cylinder_count = 0 if kitchen_fuel_type == 'Wood' else 6 + (venue_id % 8)
    restrooms_count = 4 + (venue_id % 6)
    bathrooms_count = 3 + (venue_id % 5)
    water_taps_count = 8 + (venue_id % 12)
    two_wheeler_parking_capacity = 35 + ((venue_id * 4) % 135)
    # Keep non-zero car parking sample data for every seeded venue.
    car_parking_available = 1
    max_car_parking_capacity = 25 + ((venue_id * 3) % 95)
    groom_rooms_count = 1 + (venue_id % 4)
    bride_rooms_count = 1 + ((venue_id + 1) % 4)
    owner_mobile = f"9{700000000 + venue_id:09d}"
    advance_amount = max(int(base_price * 0.4), 10000)
    advance_details = '40% advance for confirmation and remaining before function date'
    timing_type = '24hrs' if venue_id % 2 == 0 else '12hrs'
    disability_ramp_available = 1 if venue_id % 3 != 1 else 0
    address = f"{venue_name}, {location}, Karaikudi, Tamil Nadu"

    return (
        seating_capacity,
        dining_capacity,
        dining_type,
        buffet_available,
        kitchen_specialty,
        kitchen_food_support,
        kitchen_fuel_type,
        gas_cylinder_count,
        restrooms_count,
        bathrooms_count,
        water_taps_count,
        two_wheeler_parking_capacity,
        car_parking_available,
        max_car_parking_capacity,
        groom_rooms_count,
        bride_rooms_count,
        owner_mobile,
        advance_amount,
        advance_details,
        timing_type,
        disability_ramp_available,
        address,
        venue_id
    )


def backfill_venue_facility_data(cursor):
    """Populate sample facility data for venues that do not yet have full details."""
    cursor.execute(
        '''
        SELECT id, venue_name, location, capacity, price
        FROM venues
        WHERE seating_capacity IS NULL
           OR seating_capacity = 0
              OR max_car_parking_capacity IS NULL
              OR max_car_parking_capacity = 0
              OR car_parking_available IS NULL
              OR car_parking_available = 0
              OR advance_amount IS NULL
              OR advance_amount = 0
              OR advance_details IS NULL
              OR TRIM(advance_details) = ''
           OR owner_mobile IS NULL
           OR TRIM(owner_mobile) = ''
           OR address IS NULL
           OR TRIM(address) = ''
        '''
    )
    venues_to_update = cursor.fetchall()

    if not venues_to_update:
        return

    update_sql = '''
        UPDATE venues
        SET seating_capacity = ?,
            dining_capacity = ?,
            dining_type = ?,
            buffet_available = ?,
            kitchen_specialty = ?,
            kitchen_food_support = ?,
            kitchen_fuel_type = ?,
            gas_cylinder_count = ?,
            restrooms_count = ?,
            bathrooms_count = ?,
            water_taps_count = ?,
            two_wheeler_parking_capacity = ?,
            car_parking_available = ?,
            max_car_parking_capacity = ?,
            groom_rooms_count = ?,
            bride_rooms_count = ?,
            owner_mobile = ?,
            advance_amount = ?,
            advance_details = ?,
            timing_type = ?,
            disability_ramp_available = ?,
            address = ?
        WHERE id = ?
    '''

    for venue in venues_to_update:
        cursor.execute(update_sql, build_sample_facility_data(venue))

    print(f"✓ Added full venue facilities sample data for {len(venues_to_update)} venue(s)")

def convert_sql_to_sqlite(query):
    """Convert MySQL-style SQL to SQLite-compatible SQL"""
    # Replace %s with ? for SQLite
    return query.replace('%s', '?')

def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        is_admin INTEGER DEFAULT 0,
        registration_email_sent INTEGER DEFAULT 0,
        registration_email_status TEXT DEFAULT 'PENDING',
        registration_email_sent_at TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Migration: add registration email tracking columns to existing users table.
    try:
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [column[1] for column in cursor.fetchall()]

        if 'registration_email_sent' not in user_columns:
            cursor.execute('ALTER TABLE users ADD COLUMN registration_email_sent INTEGER DEFAULT 0')
            print("✓ Added registration_email_sent column to users table")
            conn.commit()

        if 'registration_email_status' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN registration_email_status TEXT DEFAULT 'PENDING'")
            print("✓ Added registration_email_status column to users table")
            conn.commit()

        if 'registration_email_sent_at' not in user_columns:
            cursor.execute('ALTER TABLE users ADD COLUMN registration_email_sent_at TIMESTAMP NULL')
            print("✓ Added registration_email_sent_at column to users table")
            conn.commit()

        cursor.execute(
            """
            UPDATE users
            SET registration_email_status = CASE
                WHEN registration_email_sent = 1 THEN 'SENT'
                ELSE 'PENDING'
            END
            WHERE registration_email_status IS NULL OR TRIM(registration_email_status) = ''
            """
        )
        conn.commit()
    except Exception as e:
        print(f"Migration check for users passed or not needed: {e}")
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS venues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venue_name TEXT NOT NULL,
        location TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        price INTEGER NOT NULL,
        isAC INTEGER DEFAULT 0,
        rating REAL DEFAULT 4.0,
        facilities TEXT,
        image_url TEXT,
        thumbnail_url TEXT,
        description TEXT,
        latitude REAL DEFAULT 10.4591,
        longitude REAL DEFAULT 78.1424,
        gmaps_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    ensure_venue_facility_columns(cursor)
    
    # Check if latitude column exists in existing table, if not add it (migration)
    try:
        cursor.execute("PRAGMA table_info(venues)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'latitude' not in columns:
            cursor.execute('ALTER TABLE venues ADD COLUMN latitude REAL DEFAULT 10.4591')
            cursor.execute('ALTER TABLE venues ADD COLUMN longitude REAL DEFAULT 78.1424')
            cursor.execute('ALTER TABLE venues ADD COLUMN gmaps_url TEXT')
            print("✓ Added latitude, longitude, gmaps_url columns to venues table")
            conn.commit()
    except Exception as e:
        print(f"Migration check passed or not needed: {e}")
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        venue_id INTEGER NOT NULL,
        booking_date DATE NOT NULL,
        start_date DATE,
        end_date DATE,
        start_time TEXT DEFAULT '09:00',
        end_time TEXT DEFAULT '21:00',
        payment_status TEXT DEFAULT 'PENDING',
        booking_status TEXT DEFAULT 'CONFIRMED',
        amount INTEGER NOT NULL,
        payment_id TEXT,
        email_sent INTEGER DEFAULT 0,
        email_status TEXT DEFAULT 'PENDING',
        email_sent_at TIMESTAMP NULL,
        feedback_request_sent INTEGER DEFAULT 0,
        feedback_request_status TEXT DEFAULT 'PENDING',
        feedback_request_sent_at TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(venue_id) REFERENCES venues(id)
    )''')
    
    # Migration: Add email_sent columns to existing bookings table if not present
    try:
        cursor.execute("PRAGMA table_info(bookings)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'email_sent' not in columns:
            cursor.execute('ALTER TABLE bookings ADD COLUMN email_sent INTEGER DEFAULT 0')
            cursor.execute('ALTER TABLE bookings ADD COLUMN email_sent_at TIMESTAMP NULL')
            print("✓ Added email_sent and email_sent_at columns to bookings table")
            conn.commit()

        if 'email_status' not in columns:
            cursor.execute("ALTER TABLE bookings ADD COLUMN email_status TEXT DEFAULT 'PENDING'")
            print("✓ Added email_status column to bookings table")
            conn.commit()

        if 'start_date' not in columns:
            cursor.execute('ALTER TABLE bookings ADD COLUMN start_date DATE')
            print("✓ Added start_date column to bookings table")
            conn.commit()

        if 'end_date' not in columns:
            cursor.execute('ALTER TABLE bookings ADD COLUMN end_date DATE')
            print("✓ Added end_date column to bookings table")
            conn.commit()

        if 'start_time' not in columns:
            cursor.execute("ALTER TABLE bookings ADD COLUMN start_time TEXT DEFAULT '09:00'")
            print("✓ Added start_time column to bookings table")
            conn.commit()

        if 'end_time' not in columns:
            cursor.execute("ALTER TABLE bookings ADD COLUMN end_time TEXT DEFAULT '21:00'")
            print("✓ Added end_time column to bookings table")
            conn.commit()

        if 'feedback_request_sent' not in columns:
            cursor.execute('ALTER TABLE bookings ADD COLUMN feedback_request_sent INTEGER DEFAULT 0')
            print("✓ Added feedback_request_sent column to bookings table")
            conn.commit()

        if 'feedback_request_status' not in columns:
            cursor.execute("ALTER TABLE bookings ADD COLUMN feedback_request_status TEXT DEFAULT 'PENDING'")
            print("✓ Added feedback_request_status column to bookings table")
            conn.commit()

        if 'feedback_request_sent_at' not in columns:
            cursor.execute('ALTER TABLE bookings ADD COLUMN feedback_request_sent_at TIMESTAMP NULL')
            print("✓ Added feedback_request_sent_at column to bookings table")
            conn.commit()

        # Backfill legacy rows created before email_status tracking.
        cursor.execute(
            """
            UPDATE bookings
            SET email_status = CASE
                WHEN email_sent = 1 THEN 'SENT'
                ELSE 'FAILED'
            END
            WHERE email_status IS NULL OR TRIM(email_status) = ''
            """
        )

        cursor.execute(
            """
            UPDATE bookings
            SET start_date = COALESCE(start_date, booking_date),
                end_date = COALESCE(end_date, booking_date),
                start_time = COALESCE(NULLIF(TRIM(start_time), ''), '09:00'),
                end_time = COALESCE(NULLIF(TRIM(end_time), ''), '21:00')
            """
        )

        cursor.execute(
            """
            UPDATE bookings
            SET feedback_request_status = CASE
                WHEN feedback_request_sent = 1 THEN 'SENT'
                ELSE COALESCE(NULLIF(TRIM(feedback_request_status), ''), 'PENDING')
            END
            WHERE feedback_request_status IS NULL OR TRIM(feedback_request_status) = '' OR feedback_request_sent = 1
            """
        )
        conn.commit()
    except Exception as e:
        print(f"Migration check for bookings passed or not needed: {e}")

    cursor.execute('''CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        venue_id INTEGER,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(venue_id) REFERENCES venues(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS notification_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_type TEXT NOT NULL,
        recipient_name TEXT,
        recipient_email TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        email_status TEXT DEFAULT 'PENDING',
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(created_by) REFERENCES users(id)
    )''')
    
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        booking_id INTEGER,
        message TEXT,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(booking_id) REFERENCES bookings(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        payment_method TEXT,
        transaction_id TEXT,
        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(booking_id) REFERENCES bookings(id)
    )''')
    
    # Insert 50 wedding venues if they don't exist
    cursor.execute('SELECT COUNT(*) FROM venues')
    if cursor.fetchone()[0] == 0:
        # Define venue coordinates around Karaikudi (base: 10.4591, 78.1424)
        # Adding slight offsets to distribute venues across the city
        venues_with_coords = [
            (1, "Subhalakshmi Mahal", "TT Nagar, Sekkalai", 800, 60000, 1, 4.3, "AC, Parking, Catering", "https://via.placeholder.com/600x400?text=Subhalakshmi", "https://via.placeholder.com/300x200?text=Subhalakshmi", 10.4502, 78.1535),
            (2, "PLP Palace Wedding Hall", "Ananda Nagar", 1000, 85000, 1, 4.5, "AC, DJ, Stage, Parking", "https://via.placeholder.com/600x400?text=PLP+Palace", "https://via.placeholder.com/300x200?text=PLP+Palace", 10.4612, 78.1625),
            (3, "Sathguru Gnananandha Marriage Hall", "Sekkalai", 700, 50000, 0, 4.1, "Stage, Parking", "https://via.placeholder.com/600x400?text=Sathguru", "https://via.placeholder.com/300x200?text=Sathguru", 10.4580, 78.1385),
            (4, "SR Grand Mahal", "Burma Colony", 900, 75000, 1, 4.4, "AC, Catering, Music", "https://via.placeholder.com/600x400?text=SR+Grand", "https://via.placeholder.com/300x200?text=SR+Grand", 10.4720, 78.1450),
            (5, "Apurva Marriage Hall", "Kannadasan Nagar", 600, 45000, 0, 4.0, "Parking, Stage", "https://via.placeholder.com/600x400?text=Apurva", "https://via.placeholder.com/300x200?text=Apurva", 10.4480, 78.1290),
            (6, "KVS Mahal", "Ariyakudi Main Road", 750, 55000, 0, 4.1, "Stage, Parking, Lights", "https://via.placeholder.com/600x400?text=KVS+Mahal", "https://via.placeholder.com/300x200?text=KVS+Mahal", 10.4650, 78.1520),
            (7, "6X Party Hall", "Arumugam Nagar", 300, 25000, 1, 4.0, "AC, DJ, Sound System", "https://via.placeholder.com/600x400?text=6X+Party", "https://via.placeholder.com/300x200?text=6X+Party", 10.4390, 78.1360),
            (8, "Abirami Palace", "NH536, Soorakudi", 1000, 90000, 1, 4.6, "AC, DJ, Catering, Stage", "https://via.placeholder.com/600x400?text=Abirami", "https://via.placeholder.com/300x200?text=Abirami", 10.5020, 78.1680),
            (9, "Shri Maadan Mahal", "Ananda Nagar", 650, 48000, 0, 4.2, "Stage, Parking", "https://via.placeholder.com/600x400?text=Shri+Maadan", "https://via.placeholder.com/300x200?text=Shri+Maadan", 10.4595, 78.1610),
            (10, "Dhanalakshmi Marriage Hall", "Kallukatti", 500, 40000, 0, 4.0, "Parking", "https://via.placeholder.com/600x400?text=Dhanalakshmi", "https://via.placeholder.com/300x200?text=Dhanalakshmi", 10.4850, 78.1290),
            (11, "Anugraha Marriage Hall", "Kallukatti", 700, 100000, 1, 4.5, "AC, DJ, Catering, Parking", "https://via.placeholder.com/600x400?text=Anugraha", "https://via.placeholder.com/300x200?text=Anugraha", 10.4920, 78.1350),
            (12, "LM Marriage Hall", "Devakottai Road, Senjai", 550, 52000, 1, 4.3, "AC, Stage, Parking", "https://via.placeholder.com/600x400?text=LM+Hall", "https://via.placeholder.com/300x200?text=LM+Hall", 10.3980, 78.0950),
            (13, "Alagammai Mahal", "Railway Station Road", 800, 65000, 1, 3.5, "AC, Catering, Parking", "https://via.placeholder.com/600x400?text=Alagammai", "https://via.placeholder.com/300x200?text=Alagammai", 10.4655, 78.1210),
            (14, "Amaravathy Marriage Hall", "Ananda Nagar", 600, 45000, 0, 3.9, "Stage, Parking", "https://via.placeholder.com/600x400?text=Amaravathy", "https://via.placeholder.com/300x200?text=Amaravathy", 10.4620, 78.1680),
            (15, "Rajeswari Mahal", "Kalanivasal", 500, 42000, 0, 4.0, "Parking", "https://via.placeholder.com/600x400?text=Rajeswari", "https://via.placeholder.com/300x200?text=Rajeswari", 10.3850, 78.0820),
            (16, "APS Hall A/C", "Police Colony Road", 300, 30000, 1, 4.1, "AC, DJ", "https://via.placeholder.com/600x400?text=APS+Hall", "https://via.placeholder.com/300x200?text=APS+Hall", 10.4525, 78.1155),
            (17, "Sri Muthukrishna Mahal", "Kalanivasal", 600, 40000, 0, 3.8, "Stage", "https://via.placeholder.com/600x400?text=Sri+Muthukrishna", "https://via.placeholder.com/300x200?text=Sri+Muthukrishna", 10.3900, 78.0880),
            (18, "Krish Hall", "Old Bus Stand", 400, 35000, 1, 4.5, "AC, DJ, Sound", "https://via.placeholder.com/600x400?text=Krish+Hall", "https://via.placeholder.com/300x200?text=Krish+Hall", 10.4440, 78.1045),
            (19, "M.A.M Mahal", "Sekkalai Road", 500, 45000, 1, 4.2, "AC, Stage, Parking", "https://via.placeholder.com/600x400?text=MAM+Mahal", "https://via.placeholder.com/300x200?text=MAM+Mahal", 10.4510, 78.1470),
            (20, "Dhena Valli Mahal", "Devakottai Road", 600, 38000, 0, 3.9, "Stage, Lights", "https://via.placeholder.com/600x400?text=Dhena+Valli", "https://via.placeholder.com/300x200?text=Dhena+Valli", 10.3950, 78.1020),
            (21, "Meena Mahal A/C", "Iluppakkudi Road", 700, 55000, 1, 4.1, "AC, Catering, DJ", "https://via.placeholder.com/600x400?text=Meena+Mahal", "https://via.placeholder.com/300x200?text=Meena+Mahal", 10.5150, 78.1550),
            (22, "Dharma Shastha Mandapam", "Soodamanipuram", 500, 35000, 0, 4.0, "Stage, Parking", "https://via.placeholder.com/600x400?text=Dharma+Shastha", "https://via.placeholder.com/300x200?text=Dharma+Shastha", 10.3750, 78.1180),
            (23, "Saana Meena Thirumana Mandapam", "Sekkalai", 800, 60000, 1, 4.2, "AC, Stage, Catering", "https://via.placeholder.com/600x400?text=Saana+Meena", "https://via.placeholder.com/300x200?text=Saana+Meena", 10.4485, 78.1385),
            (24, "Sankara Mani Mandapam", "Sekkalai", 400, 30000, 0, 4.1, "Stage", "https://via.placeholder.com/600x400?text=Sankara+Mani", "https://via.placeholder.com/300x200?text=Sankara+Mani", 10.4570, 78.1340),
            (25, "Prasanna Mahal", "Pari Nagar", 750, 58000, 1, 4.3, "AC, DJ, Parking", "https://via.placeholder.com/600x400?text=Prasanna", "https://via.placeholder.com/300x200?text=Prasanna", 10.4750, 78.1290),
            (26, "Vasavi Mahal", "Bharathi Nagar", 500, 35000, 0, 4.0, "Stage, Parking", "https://via.placeholder.com/600x400?text=Vasavi", "https://via.placeholder.com/300x200?text=Vasavi", 10.4330, 78.1105),
            (27, "Srinivasa Mahal A/C", "Ariyakudi Road", 650, 50000, 1, 4.2, "AC, Catering", "https://via.placeholder.com/600x400?text=Srinivasa", "https://via.placeholder.com/300x200?text=Srinivasa", 10.4800, 78.1450),
            (28, "Lena Meena Mahal", "Near Temple", 900, 70000, 1, 4.4, "AC, DJ, Catering", "https://via.placeholder.com/600x400?text=Lena+Meena", "https://via.placeholder.com/300x200?text=Lena+Meena", 10.4950, 78.1590),
            (29, "Ganapathy Mahal", "Karaikudi Local", 400, 25000, 0, 3.8, "Stage", "https://via.placeholder.com/600x400?text=Ganapathy", "https://via.placeholder.com/300x200?text=Ganapathy", 10.4400, 78.1220),
            (30, "Rajalakshmi Mahal", "Karaikudi", 600, 45000, 1, 4.0, "AC, Parking", "https://via.placeholder.com/600x400?text=Rajalakshmi", "https://via.placeholder.com/300x200?text=Rajalakshmi", 10.4590, 78.1320),
            (31, "Kalaignar Arivalayam", "Karaikudi Central", 1200, 95000, 1, 4.6, "AC, DJ, Catering, Stage", "https://via.placeholder.com/600x400?text=Kalaignar", "https://via.placeholder.com/300x200?text=Kalaignar", 10.4615, 78.1450),
            (32, "Sethu Meena Mahal", "Karaikudi", 500, 35000, 0, 3.9, "Stage, Parking", "https://via.placeholder.com/600x400?text=Sethu+Meena", "https://via.placeholder.com/300x200?text=Sethu+Meena", 10.4530, 78.1180),
            (33, "Sai Sakthi Marriage Hall", "Karaikudi", 450, 30000, 0, 4.0, "Stage", "https://via.placeholder.com/600x400?text=Sai+Sakthi", "https://via.placeholder.com/300x200?text=Sai+Sakthi", 10.4650, 78.1280),
            (34, "Sri Raghavendra Marriage Hall", "Karaikudi", 550, 40000, 0, 4.1, "Stage, Parking", "https://via.placeholder.com/600x400?text=Sri+Raghavendra", "https://via.placeholder.com/300x200?text=Sri+Raghavendra", 10.4720, 78.1520),
            (35, "Murugan Kalyana Mandapam", "Karaikudi", 600, 38000, 0, 4.0, "Stage", "https://via.placeholder.com/600x400?text=Murugan", "https://via.placeholder.com/300x200?text=Murugan", 10.4490, 78.1410),
            (36, "Shakthi Duraisamy Mandapam", "Karaikudi", 700, 50000, 1, 4.2, "AC, Stage, Catering", "https://via.placeholder.com/600x400?text=Shakthi", "https://via.placeholder.com/300x200?text=Shakthi", 10.4580, 78.1620),
            (37, "Sri Bhavani Mandapam", "Karaikudi", 500, 35000, 0, 3.8, "Stage", "https://via.placeholder.com/600x400?text=Sri+Bhavani", "https://via.placeholder.com/300x200?text=Sri+Bhavani", 10.4430, 78.1070),
            (38, "Meenambika Mandapam", "Karaikudi", 400, 30000, 0, 4.1, "Stage, Parking", "https://via.placeholder.com/600x400?text=Meenambika", "https://via.placeholder.com/300x200?text=Meenambika", 10.4780, 78.1350),
            (39, "Ayyanar Kalyana Mandapam", "Karaikudi", 800, 55000, 0, 4.0, "Stage, Lights", "https://via.placeholder.com/600x400?text=Ayyanar", "https://via.placeholder.com/300x200?text=Ayyanar", 10.4520, 78.1560),
            (40, "Seetha Mahal", "Karaikudi", 650, 48000, 1, 4.3, "AC, DJ, Parking", "https://via.placeholder.com/600x400?text=Seetha", "https://via.placeholder.com/300x200?text=Seetha", 10.4850, 78.1210),
            (41, "Sri Aranganathan Marriage Hall", "Karaikudi", 500, 35000, 0, 4.0, "Stage", "https://via.placeholder.com/600x400?text=Sri+Aranganathan", "https://via.placeholder.com/300x200?text=Sri+Aranganathan", 10.4370, 78.1340),
            (42, "Lakshmi Narasimha Marriage Hall", "Karaikudi", 600, 42000, 0, 4.1, "Stage, Parking", "https://via.placeholder.com/600x400?text=Lakshmi+Narasimha", "https://via.placeholder.com/300x200?text=Lakshmi+Narasimha", 10.4640, 78.1580),
            (43, "Sri Sakthi Marriage Hall", "Karaikudi", 450, 32000, 0, 3.9, "Stage", "https://via.placeholder.com/600x400?text=Sri+Sakthi", "https://via.placeholder.com/300x200?text=Sri+Sakthi", 10.4510, 78.1120),
            (44, "Sri Durga Parameswari Hall", "Karaikudi", 500, 35000, 1, 4.1, "AC, DJ", "https://via.placeholder.com/600x400?text=Sri+Durga", "https://via.placeholder.com/300x200?text=Sri+Durga", 10.4760, 78.1470),
            (45, "Arunachala Mahal", "Karaikudi", 900, 75000, 1, 4.5, "AC, DJ, Catering", "https://via.placeholder.com/600x400?text=Arunachala", "https://via.placeholder.com/300x200?text=Arunachala", 10.4420, 78.1250),
            (46, "Sri Venkateswara Marriage Hall", "Karaikudi", 700, 45000, 0, 4.0, "Stage, Lights", "https://via.placeholder.com/600x400?text=Sri+Venkateswara", "https://via.placeholder.com/300x200?text=Sri+Venkateswara", 10.4910, 78.1680),
            (47, "Sri Krishna Marriage Hall", "Karaikudi", 550, 38000, 0, 3.9, "Stage", "https://via.placeholder.com/600x400?text=Sri+Krishna", "https://via.placeholder.com/300x200?text=Sri+Krishna", 10.4480, 78.1580),
            (48, "Sri Lakshmi Marriage Hall", "Karaikudi", 600, 40000, 0, 4.0, "Stage, Parking", "https://via.placeholder.com/600x400?text=Sri+Lakshmi", "https://via.placeholder.com/300x200?text=Sri+Lakshmi", 10.4620, 78.1050),
            (49, "Sri Balaji Marriage Hall", "Karaikudi", 500, 35000, 0, 4.1, "Stage", "https://via.placeholder.com/600x400?text=Sri+Balaji", "https://via.placeholder.com/300x200?text=Sri+Balaji", 10.4740, 78.1620),
            (50, "Sri Ganesh Marriage Hall", "Karaikudi", 400, 28000, 0, 3.8, "Stage", "https://via.placeholder.com/600x400?text=Sri+Ganesh", "https://via.placeholder.com/300x200?text=Sri+Ganesh", 10.4350, 78.0950),
        ]
        cursor.executemany(
            'INSERT INTO venues (id, venue_name, location, capacity, price, isAC, rating, facilities, image_url, thumbnail_url, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            venues_with_coords
        )
        
        # Generate and update Google Maps URLs for all venues
        cursor.execute('SELECT id, latitude, longitude FROM venues')
        all_venues = cursor.fetchall()
        for venue in all_venues:
            # venue is a tuple: (id, latitude, longitude)
            venue_id = venue[0]
            latitude = venue[1]
            longitude = venue[2]
            gmaps_url = f"https://www.google.com/maps?q={latitude},{longitude}&ll={latitude},{longitude}&z=15"
            cursor.execute('UPDATE venues SET gmaps_url = ? WHERE id = ?', (gmaps_url, venue_id))
        print("✓ Generated Google Maps URLs for all 50 venues")

    backfill_venue_facility_data(cursor)

    # Sync local venue images by matching filenames to venue names.
    sync_venue_image_urls(cursor)
    
    # Create admin user if doesn't exist
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    if cursor.fetchone()[0] == 0:
        from werkzeug.security import generate_password_hash
        admin_password = generate_password_hash('admin123')
        cursor.execute(
            'INSERT INTO users (name, email, password, phone, is_admin) VALUES (?, ?, ?, ?, ?)',
            ('Admin', 'admin@venue.com', admin_password, '9876543210', 1)
        )
    
    conn.commit()
    conn.close()
    print("SQLite Database Initialized with 50 venues successfully")

def get_db_connection():
    """Create and return a SQLite database connection"""
    try:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        print("SQLite Connected Successfully")
        return connection
    except Exception as err:
        print(f"Database Error: {err}")
        return None

def execute_query(query, params=None):
    """Execute a database query and return results"""
    connection = get_db_connection()
    if connection is None:
        return None
    
    query = convert_sql_to_sqlite(query)
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            return [dict(row) for row in results]
        else:
            return cursor.lastrowid
    except Exception as err:
        print(f"Error: {err}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()

def execute_fetch_one(query, params=None):
    """Execute a query and return single result"""
    connection = get_db_connection()
    if connection is None:
        return None
    
    query = convert_sql_to_sqlite(query)
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        return dict(result) if result else None
    except Exception as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        connection.close()

def execute_fetch_all(query, params=None):
    """Execute a query and return all results"""
    connection = get_db_connection()
    if connection is None:
        return None
    
    query = convert_sql_to_sqlite(query)
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        connection.close()

-- Smart Event Venue Booking System Database Schema

-- Create Database
CREATE DATABASE IF NOT EXISTS venue_booking;
USE venue_booking;

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VENUES TABLE
CREATE TABLE IF NOT EXISTS venues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venue_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    capacity INT NOT NULL,
    price INT NOT NULL,
    facilities VARCHAR(255),
    image_url VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BOOKINGS TABLE
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    venue_id INT NOT NULL,
    booking_date DATE NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'PENDING',
    booking_status VARCHAR(50) DEFAULT 'CONFIRMED',
    amount INT NOT NULL,
    payment_id VARCHAR(100),
    email_sent INT DEFAULT 0,
    email_sent_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (venue_id) REFERENCES venues(id)
);

-- FEEDBACK TABLE
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    booking_id INT,
    message TEXT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);

-- PAYMENTS TABLE
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    amount INT NOT NULL,
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);

-- Insert Sample Venues
INSERT INTO venues (venue_name, location, capacity, price, facilities, description) VALUES
('Royal Mahal', 'Erode', 800, 60000, 'AC, Parking, Catering, Stage', 'Premium wedding venue with all facilities'),
('Elite Hall', 'Salem', 500, 45000, 'AC, Parking, WiFi, Stage', 'Modern conference and party hall'),
('Grand Palace', 'Coimbatore', 1000, 80000, 'AC, Parking, Catering, Stage, DJ', 'Largest venue for mega events'),
('Silver Crown', 'Erode', 600, 50000, 'AC, Parking, Decoration, Stage', 'Elegant venue for all occasions'),
('Golden Venue', 'Salem', 700, 55000, 'AC, Parking, Catering, DJ', 'Perfect for weddings and parties');

-- Add email tracking columns for existing databases
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS email_sent INT DEFAULT 0;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS email_sent_at TIMESTAMP NULL;

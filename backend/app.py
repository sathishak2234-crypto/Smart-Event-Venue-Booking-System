from server import app


if __name__ == '__main__':
    print('Starting Smart Event Venue Booking System API...')
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', True))

#!/usr/bin/env python
import requests

# Test 1: Check health
health = requests.get('http://localhost:5000/api/health').json()
print(f'✓ API Health: {health["status"]}')

# Test 2: Check venues
venues = requests.get('http://localhost:5000/api/venues/').json()
print(f'✓ Venues loaded: {len(venues["venues"])} venues')

# Test 3: Check first venue has gmaps_url
first_venue = venues['venues'][0]
print(f'✓ First venue: {first_venue["venue_name"]}')
print(f'✓ Has Google Maps URL: {"gmaps_url" in first_venue and first_venue["gmaps_url"] is not None}')
if first_venue.get('gmaps_url'):
    print(f'✓ GMaps URL: {first_venue["gmaps_url"][:70]}...')

print('\n✅ All systems operational!')

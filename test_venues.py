#!/usr/bin/env python
import requests
import json

r = requests.get('http://localhost:5000/api/venues/')
data = r.json()

if data.get('venues') and len(data['venues']) > 0:
    print("✓ Database populated with venues")
    print(f"\nTotal Venues: {len(data['venues'])}")
    
    # Check first venue
    venue = data['venues'][0]
    print(f"\n--- First Venue Details ---")
    print(f"Name: {venue.get('venue_name')}")
    print(f"Location: {venue.get('location')}")
    print(f"Latitude: {venue.get('latitude')}")
    print(f"Longitude: {venue.get('longitude')}")
    print(f"Google Maps URL: {venue.get('gmaps_url')}")
    
    # Check if gmaps_url exists in all venues
    has_gmaps_all = all('gmaps_url' in v for v in data['venues'])
    print(f"\n✓ All venues have Google Maps URLs: {has_gmaps_all}")
    
    # Show sample URL
    if venue.get('gmaps_url'):
        print(f"\nSample URL: {venue.get('gmaps_url')}")
else:
    print("✗ No venues found")
    print(f"Response: {data}")

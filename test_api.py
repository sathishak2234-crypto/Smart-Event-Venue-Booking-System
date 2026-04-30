import json
import urllib.request
import urllib.error

print("Testing Backend API...")

try:
    # Test venues endpoint
    with urllib.request.urlopen('http://localhost:5000/api/venues?max_price=100000', timeout=5) as response:
        data = json.loads(response.read().decode())
        if 'venues' in data:
            print(f"✓ Venues API: {len(data['venues'])} venues found")
        else:
            print(f"✗ Venues API Response: {data}")
except Exception as e:
    print(f"✗ Venues API ERROR: {str(e)}")

try:
    # Test health endpoint
    with urllib.request.urlopen('http://localhost:5000/api/health', timeout=5) as response:
        data = json.loads(response.read().decode())
        print(f"✓ Health Check: {data.get('status', 'unknown')}")
except Exception as e:
    print(f"✗ Health Check ERROR: {str(e)}")

print("\nAll API tests completed!")

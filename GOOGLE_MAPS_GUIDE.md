# Google Maps Venue Viewer - Complete Guide

## Overview

The **Venue Map** feature displays all venues on an interactive Google Map with their images, prices, and ratings. Users can:
- View all venues plotted on a map
- Click markers to see detailed information with images
- Filter venues by name and price
- Switch between map types (Roadmap, Satellite, Terrain, Hybrid)

---

## Access the Map

**URL:** `http://localhost:5000/venue-map.html`

Or navigate from main menu:
1. Go to homepage
2. Click "Map View" in navigation
3. You'll see all venues on an interactive map

---

## Features

### 1. Interactive Google Map
- **Zoom & Pan** - Scroll and drag to explore
- **Multiple Map Types** - Switch between Roadmap, Satellite, Terrain, and Hybrid views
- **Fullscreen Mode** - Click fullscreen button for better viewing
- **Auto-Fit** - Map automatically fits all markers in view

### 2. Venue Markers
- **Color-Coded** - Different colors for different venues for easy identification
- **Clickable** - Click any marker to see venue details
- **Animated** - Markers drop with animation effect
- **Info Windows** - Shows venue image, name, location, price, and rating

### 3. Venue Details in Info Window
When you click a marker, you get:
- **Main Image** - Large preview of venue
- **Venue Name** - Title
- **Location** - Address/area
- **Capacity** - How many people it can hold
- **Rating** - Star rating
- **Price** - Cost per event
- **View Details Button** - Link to full venue page

### 4. Sidebar List
Left sidebar shows:
- **All Venues** - Scrollable list with thumbnails
- **Search** - Filter by venue name or location
- **Price Range Slider** - Filter by maximum price
- **Venue Count** - Shows how many venues match filters
- **Active Highlighting** - Selected venue highlighted in both list and map

---

## How to Use

### View All Venues
1. Open [venue-map.html](venue-map.html)
2. All venues automatically displayed on map
3. See purple/blue/red markers for different venues

### Click on a Marker
1. Find a marker on the map
2. Click it
3. Info window opens showing:
   - Venue image
   - Name, location, capacity, rating, price
   - "View Details" button

### Search for Venue
1. Type in "Search venue name..." box
2. Map updates in real-time
3. Shows only matching venues
4. Clear search to see all again

### Filter by Price
1. Drag the "Price Range" slider
2. See only venues up to that price
3. Map and list update instantly
4. Click "Reset" to show all venues

### View Different Map Types
1. Click the map type selector (top-right)
2. Choose: Roadmap, Satellite, Terrain, or Hybrid
3. Map view changes instantly

### Fullscreen Mode
1. Click fullscreen button (top-right)
2. Map expands to full screen
3. Ideal for presentations or detailed exploration

---

## Map Locations & Data

### Default Center
- **Location:** Karaikudi, Tamil Nadu, India
- **Coordinates:** 10.4591°N, 78.1424°E
- **Zoom Level:** Starts at level 9 (regional view)

### Venue Coordinates
Each venue can have:
- **Latitude** - North-South position
- **Longitude** - East-West position
- **Default:** If not set, uses Karaikudi coordinates

### How to Update Venue Locations
1. Open database (backend/venue_booking.db)
2. Update `latitude` and `longitude` columns
3. Or via API:

```bash
curl -X PUT http://localhost:5000/api/admin/venues/1 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 10.7905,
    "longitude": 78.7047
  }'
```

---

## Marker Colors

Each venue gets a unique marker color:
- 🔴 Red (#FF6B6B)
- 🟢 Green (#4ECDC4)
- 🔵 Blue (#45B7D1)
- 🟠 Orange (#FFA07A)
- 🟦 Teal (#98D8C8)
- 🟪 Purple (#667eea)
- 🟤 Dark Purple (#764ba2)

Colors cycle through venues for easy differentiation.

---

## Features Breakdown

### Real-Time Filtering
```
User Types in Search → Map updates
User Changes Price Slider → 25 venues → 15 venues → 8 venues
```

### Venue Card Features
- Thumbnail image from `thumbnail_url`
- Venue name and location
- Capacity (people count)
- Star rating
- Price display in rupees
- Click to highlight on map

### Info Window Features
- Main image from `image_url`
- All venue details
- One-click navigation to full venue page
- Clean, readable format
- Auto-closes when clicking other markers

---

## Database Integration

The map pulls data from the `venues` table:

```sql
SELECT id, venue_name, location, capacity, 
       price, rating, image_url, thumbnail_url, 
       latitude, longitude, gmaps_url FROM venues
```

**Required fields:**
- `venue_name` - Name to display
- `location` - Address/area
- `price` - Cost
- `capacity` - People capacity
- `latitude` - Map position (default: 10.4591)
- `longitude` - Map position (default: 78.1424)

**Optional fields:**
- `image_url` - Main venue image
- `thumbnail_url` - Small preview
- `rating` - Star rating (default: 4.0)

---

## API Integration

The map uses the existing `/api/venues/` endpoint:

```javascript
GET /api/venues/
```

**Response:**
```json
{
  "venues": [
    {
      "id": 1,
      "venue_name": "Royal Mahal",
      "location": "Erode",
      "capacity": 800,
      "price": 60000,
      "rating": 4.5,
      "image_url": "https://...",
      "thumbnail_url": "https://...",
      "latitude": 10.7905,
      "longitude": 78.7047
    }
  ]
}
```

---

## Google Maps API

### API Key
Location: `venue-map.html`
```javascript
<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBi-dRH-q7DDLHbYO5N00KlklVu528n8-E"></script>
```

### Getting Your Own API Key

If you want to use your own key:

1. **Go to Google Cloud Console**
   - https://console.cloud.google.com/

2. **Create a new project**
   - Click "Select a project" → "New Project"

3. **Enable Google Maps API**
   - Search for "Maps JavaScript API"
   - Click "Enable"

4. **Create API Key**
   - Go to "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy the key

5. **Update in venue-map.html**
   ```html
   <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY"></script>
   ```

### Restrictions (Optional)
In Google Cloud Console:
- Set HTTP referrers: `localhost:*`, `yourdomain.com`
- Set key restrictions to Maps JavaScript API only

---

## Customization

### Change Default Location
In `venue-map.html`:
```javascript
const defaultLocation = { lat: 10.4591, lng: 78.1424 };
```

### Change Default Zoom
```javascript
map = new google.maps.Map(document.getElementById('mapContainer'), {
    zoom: 9,  // Change this number (1-21, higher = closer)
    center: defaultLocation,
});
```

### Add Different Marker Icons
Modify `getMarkerIcon()` function to use custom icons:
```javascript
function getMarkerIcon(index) {
    return 'path/to/custom-icon.png';
}
```

### Change Marker Colors
Edit the colors array in `getMarkerIcon()`:
```javascript
const colors = ['FF6B6B', '4ECDC4', 'YOUR_COLOR', ...];
```

---

## Responsive Design

- **Desktop (> 992px)** - Map on left (8 columns), Sidebar on right (4 columns)
- **Tablet (768px - 992px)** - Map full width, Sidebar below
- **Mobile (< 768px)** - Stacked layout, optimized for touch

---

## Performance

- **Lazy loading** - Only loads venues when page opens
- **Efficient filtering** - Real-time updates without lag
- **Marker clustering** (Optional) - Can be added for 100+ venues
- **Image optimization** - Uses thumbnail URLs for list, main URLs for info windows

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Map not showing | Check Google Maps API key is valid |
| Markers not appearing | Verify that venues have latitude/longitude set |
| Images not loading | Check image URLs are valid and accessible |
| Map takes too long | Clear browser cache, check internet speed |
| Filters not working | Refresh page, check console for JS errors |
| Info window not showing | Try clicking marker again, check pop-up blockers |

---

## Sample Venue Data with Coordinates

```json
{
  "id": 1,
  "venue_name": "Royal Mahal",
  "location": "Erode",
  "capacity": 800,
  "price": 60000,
  "rating": 4.5,
  "image_url": "https://images.unsplash.com/photo-1519671482677...",
  "thumbnail_url": "https://images.unsplash.com/photo-1519671482677...",
  "latitude": 10.7905,
  "longitude": 78.7047
}
```

---

## SEO & Sharing

The map page includes:
- Meta tags for social sharing
- Bootstrap responsive classes
- Accessibility features
- Print-friendly styling

---

## Future Enhancements

Potential features to add:
- [ ] Marker clustering for many venues
- [ ] Route planning (directions)
- [ ] Nearby amenities (hotels, parking)
- [ ] User reviews overlay
- [ ] Street view integration
- [ ] Booking calendar view
- [ ] Heat map for popular venues

---

## File Structure

```
frontend/
├── venue-map.html        (NEW - Map viewer)
├── home.html             (Has link to map)
├── venues.html           (List view alternative)
├── js/
│   └── app.js            (Uses existing functions)
└── css/
    └── style.css         (Uses existing styles)

backend/
├── routes/
│   └── venues.py         (Provides /api/venues/)
└── server.py             (Serves map files)
```

---

## Summary

✅ **What You Get:**
- Interactive Google Map of all venues
- Real-time search and filtering
- Venue images in markers
- Responsive design (desktop/mobile)
- Click through to booking

✅ **Key Data Points:**
- Venue name, location, capacity, price, rating
- High-quality venue images
- Accurate GPS coordinates
- Live updates from database

✅ **User Experience:**
- Intuitive map interface
- Smooth animations
- Fast loading
- Mobile-friendly
- Accessibility features

---

**Start Using:** Open [venue-map.html](venue-map.html) and explore!

For support, check [IMAGE_UPLOAD_GUIDE.md](IMAGE_UPLOAD_GUIDE.md) and [IMAGE_URL_GUIDE.md](IMAGE_URL_GUIDE.md) for image management.

# How to Upload Images for Venues - Step by Step Guide

## Overview
This guide shows you the easiest way to upload venue images to your Smart Event Venue Booking system. The system now supports image uploads with a user-friendly admin interface.

---

## Method 1: Using the Admin Upload Interface (EASIEST) ⭐

### Prerequisites
- Admin login credentials
- Access to admin-upload.html page

### Step 1: Navigate to Upload Page
1. Log in as an admin
2. Go to: `http://localhost:5000/admin-upload.html`
3. You should see the "Venue Image Management" page

### Step 2: Select a Venue
1. Click the dropdown that says "-- Select a Venue --"
2. Choose a venue from the list (e.g., "Royal Mahal (Erode)")
3. Click the "Load Venue Details" button
4. You'll see the current venue information and existing images

### Step 3: Upload Main Image
1. Look for the section titled "Step 2: Upload Main Image"
2. Either:
   - **Drag and drop** your image onto the blue drop zone, OR
   - **Click** the drop zone and select an image from your computer
3. Preview your image will appear below
4. Click the "Upload Main Image" button
5. A green success message will appear with your image URL

**Recommended size:** 600x400px or larger

### Step 4: Upload Thumbnail Image
1. Look for the section titled "Step 3: Upload Thumbnail"
2. Either:
   - **Drag and drop** your image onto the green drop zone, OR
   - **Click** the drop zone and select an image from your computer
3. Preview your image will appear below
4. Click the "Upload Thumbnail" button
5. A green success message will appear with your image URL

**Recommended size:** 300x200px

### Step 5: Save to Database
1. After uploading both images, click the blue button "Save Images to Database"
2. The system will automatically save the image URLs to the database
3. You'll see a success confirmation message
4. The page will refresh

✅ **Done!** Your images are now live on the website.

---

## Method 2: Using cURL (For API Automation)

If you want to upload images automatically or via command line:

### Upload Main Image
```bash
curl -X POST http://localhost:5000/api/admin/upload-image \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@/path/to/main-image.jpg"
```

**Response:**
```json
{
  "message": "Image uploaded successfully",
  "image_url": "/uploads/20260416_143022_main-image.jpg",
  "filename": "20260416_143022_main-image.jpg"
}
```

### Upload Thumbnail
```bash
curl -X POST http://localhost:5000/api/admin/upload-thumbnail \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@/path/to/thumbnail.jpg"
```

**Response:**
```json
{
  "message": "Thumbnail uploaded successfully",
  "thumbnail_url": "/uploads/thumb_20260416_143022_thumbnail.jpg",
  "filename": "thumb_20260416_143022_thumbnail.jpg"
}
```

### Update Venue with Image URLs
```bash
curl -X PUT http://localhost:5000/api/admin/venues/1 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "/uploads/20260416_143022_main-image.jpg",
    "thumbnail_url": "/uploads/thumb_20260416_143022_thumbnail.jpg"
  }'
```

---

## Method 3: Manual Database Update (Advanced)

If you already have image files available online:

### Update Venue Directly
```bash
curl -X PUT http://localhost:5000/api/admin/venues/1 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/venue-main.jpg",
    "thumbnail_url": "https://example.com/venue-thumb.jpg"
  }'
```

---

## Supported Image Formats

✅ **Supported:**
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- WebP (.webp)

❌ **Not Supported:**
- BMP
- TIFF
- SVG

**Max File Size:** No limit set (configure as needed)

---

## Image Location in System

Uploaded images are stored here:
```
backend/uploads/
├── 20260416_143022_royal-mahal.jpg       (main image)
├── thumb_20260416_143022_royal-mahal.jpg (thumbnail)
├── 20260416_145100_elite-hall.jpg
└── thumb_20260416_145100_elite-hall.jpg
```

Images are served through: `http://localhost:5000/uploads/FILENAME`

---

## Troubleshooting

### Issue: Upload Button Not Appearing
**Solution:** Make sure you've selected a file. Drag and drop or click to select an image.

### Issue: "Invalid file type" Error
**Solution:** Make sure you're uploading a PNG, JPG, GIF, or WEBP file. Check that the file extension is correct.

### Issue: "No file provided" Error
**Solution:** Make sure you selected a file before clicking upload.

### Issue: "Unauthorized" Error
**Solution:** Make sure you're logged in as an admin and have a valid token.

### Issue: Images Not Showing on Website
**Solution:** 
1. Make sure the image URLs were saved correctly in database
2. Check that the backend/uploads folder exists
3. Verify the server is running: `http://localhost:5000/api/health`

---

## File Structure After Setup

```
SEV/
├── backend/
│   ├── routes/
│   │   └── admin.py              (✅ Updated with upload endpoints)
│   ├── uploads/                  (✅ NEW FOLDER - stores images)
│   └── server.py                 (✅ Updated to serve images)
└── frontend/
    └── admin-upload.html         (✅ NEW - upload interface)
```

---

## Quick Reference - Image URLs

After uploading, you'll get URLs like this:

**Main Image URL:**
```
/uploads/20260416_143022_royal-mahal.jpg
```

**Thumbnail URL:**
```
/uploads/thumb_20260416_143022_royal-mahal.jpg
```

These are automatically stored in the database for:
- Homepage venue display
- Venue detail pages
- Admin dashboard
- Search results

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/admin/upload-image` | Upload main venue image |
| POST | `/api/admin/upload-thumbnail` | Upload thumbnail |
| PUT | `/api/admin/venues/{id}` | Update venue with image URLs |
| GET | `/uploads/{filename}` | Serve uploaded image |

---

## Best Practices

1. **Image Names:** Use descriptive names (e.g., `royal-mahal-main.jpg`)
2. **Dimensions:** Keep main images 600x400+ and thumbnails 300x200
3. **File Size:** Keep under 2MB for faster loading
4. **Formats:** Use JPG for photos, PNG for graphics
5. **Backup:** Keep originals before uploading
6. **Consistency:** Use similar styling/filters across all venue images

---

## Key Features Included

✅ **Drag & Drop Upload** - Easy file selection  
✅ **File Preview** - See images before uploading  
✅ **Auto Rename** - Prevents filename conflicts  
✅ **Copy URL Button** - Easily copy image paths  
✅ **Error Handling** - Clear error messages  
✅ **Admin Auth** - Secure uploads  
✅ **Automatic DB Update** - Save URLs to database  
✅ **Image Serving** - Serve from backend  

---

## Example: Complete Image Upload Workflow

```
1. User goes to http://localhost:5000/admin-upload.html
   ↓
2. Selects "Royal Mahal" from dropdown
   ↓
3. Loads venue details
   ↓
4. Drags main image → Click Upload Main Image
   ↓ (Uploaded to backend/uploads/)
5. Gets URL: /uploads/20260416_143022_royal-mahal.jpg
   ↓
6. Drags thumbnail → Click Upload Thumbnail
   ↓ (Uploaded to backend/uploads/)
7. Gets URL: /uploads/thumb_20260416_143022_royal-mahal.jpg
   ↓
8. Clicks "Save Images to Database"
   ↓ (Updates database)
9. Images now visible on:
   - Homepage
   - Venue listings
   - Venue detail page
   - Admin dashboard
```

---

## Next Steps

1. **Upload some images** using the admin-upload.html interface
2. **Verify** images appear on home.html and venues.html
3. **Test** on mobile to ensure responsive display
4. **Update** bootstrap classes if needed for styling

---

For more help, check the [DATA_FLOW_VERIFICATION.md](DATA_FLOW_VERIFICATION.md) file for system architecture.

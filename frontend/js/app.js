// ==========================================
// Smart Event Venue Booking System - JavaScript
// ==========================================

function resolveApiBaseUrl() {
    if (window.API_BASE_URL && typeof window.API_BASE_URL === 'string') {
        return window.API_BASE_URL.replace(/\/$/, '');
    }

    // Allow manual override for troubleshooting without code changes.
    const savedBaseUrl = localStorage.getItem('apiBaseUrl');
    if (savedBaseUrl) {
        return savedBaseUrl.replace(/\/$/, '');
    }

    return 'http://localhost:5000/api';
}

const API_BASE_URL = resolveApiBaseUrl();
let currentUser = null;
let currentVenue = null;
let selectedStartDate = null;
let selectedEndDate = null;
let selectedStartTime = '09:00';
let selectedEndTime = '21:00';
let currentBookingId = null;

function applyBookingTimeFrame(frameValue) {
    if (!frameValue || frameValue === 'custom') {
        return;
    }

    const [startTime, endTime] = frameValue.split('|');
    if (!startTime || !endTime) {
        return;
    }

    selectedStartTime = startTime;
    selectedEndTime = endTime;

    const startTimeInput = document.getElementById('bookingStartTime');
    const endTimeInput = document.getElementById('bookingEndTime');
    if (startTimeInput) {
        startTimeInput.value = startTime;
    }
    if (endTimeInput) {
        endTimeInput.value = endTime;
    }
}

// ==========================================
// Utility Functions
// ==========================================

function getAuthToken() {
    return localStorage.getItem('authToken');
}

function setAuthToken(token) {
    localStorage.setItem('authToken', token);
}

function setCurrentUser(user) {
    currentUser = user;
    localStorage.setItem('currentUser', JSON.stringify(user));
}

function getCurrentUser() {
    const user = localStorage.getItem('currentUser');
    return user ? JSON.parse(user) : null;
}

function isAuthenticated() {
    return getAuthToken() !== null;
}

function redirectToLogin() {
    window.location.href = 'login.html';
}

function redirectToHome() {
    window.location.href = 'profile.html';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatPrice(price) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0
    }).format(price);
}

function isTruthyFlag(value) {
    return value === 1 || value === true || value === '1';
}

function safeText(value, fallback = 'Not specified') {
    if (value === null || value === undefined) {
        return fallback;
    }

    const stringValue = String(value).trim();
    return stringValue ? stringValue : fallback;
}

function buildGoogleMapsUrl(venue) {
    const placeQuery = [venue.venue_name, venue.location, venue.address]
        .filter((value) => value !== null && value !== undefined && String(value).trim())
        .map((value) => String(value).trim())
        .join(', ');

    if (placeQuery) {
        return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(placeQuery)}`;
    }

    if (venue.gmaps_url) {
        return venue.gmaps_url;
    }

    return 'https://www.google.com/maps';
}

function getVenueGallery(venue) {
    const rawImages = [venue.image_url, venue.thumbnail_url]
        .filter(Boolean)
        .flatMap((value) => String(value).split(','))
        .map((value) => value.trim())
        .filter(Boolean);

    const uniqueImages = [...new Set(rawImages)];
    if (uniqueImages.length === 0) {
        return ['https://via.placeholder.com/900x500?text=' + encodeURIComponent(venue.venue_name || 'Venue')];
    }

    return uniqueImages;
}

function openVenueModal() {
    const modalElement = document.getElementById('venueModal');
    if (!modalElement) {
        throw new Error('Venue modal element not found on this page.');
    }

    if (window.bootstrap && bootstrap.Modal) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
        modal.show();
        return;
    }

    // Fallback for edge cases where Bootstrap JS is not loaded.
    modalElement.style.display = 'block';
    modalElement.classList.add('show');
    modalElement.removeAttribute('aria-hidden');
}

function buildVenueDetailsHtml(venue) {
    const rating = venue.rating || 4.0;
    const gallery = getVenueGallery(venue);
    const primaryImage = gallery[0];
    const mapsUrl = buildGoogleMapsUrl(venue);
    const parkingAvailable = isTruthyFlag(venue.car_parking_available);
    const buffetAvailable = isTruthyFlag(venue.buffet_available);
    const rampAvailable = isTruthyFlag(venue.disability_ramp_available);

    const thumbnailHtml = gallery.length > 1
        ? `<div class="venue-thumbnails mt-2 mb-3">
                ${gallery.map((imageUrl, index) => `
                    <img
                        src="${imageUrl}"
                        alt="${venue.venue_name} thumbnail ${index + 1}"
                        class="venue-thumb"
                        onclick="document.getElementById('venueMainImage').src='${imageUrl}'"
                        onerror="this.style.display='none'"
                    >
                `).join('')}
            </div>`
        : '';

    const parkingText = parkingAvailable ? `Available (${venue.max_car_parking_capacity || 0} cars)` : 'Not Available';
    const rampText = rampAvailable ? 'Available' : 'Not Available';
    const buffetText = buffetAvailable ? 'Available' : 'Not Available';

    return `
        <img id="venueMainImage" src="${primaryImage}" alt="${venue.venue_name}" class="img-fluid mb-3 rounded" style="max-height: 400px; object-fit: cover; width: 100%;" onerror="this.src='https://via.placeholder.com/900x500?text=${encodeURIComponent(venue.venue_name)}'">
        ${thumbnailHtml}

        <div class="heading-hero-box">
            <div class="heading-hero-row">
                <h3>${venue.venue_name}</h3>
                <div class="heading-rating-pill">
                    <i class="fas fa-star"></i>
                    ${rating.toFixed(1)}/5.0 Rating
                </div>
            </div>
            <p>Elegant details, complete amenities, and booking-ready venue insights.</p>
        </div>

        <a href="${mapsUrl}" target="_blank" class="map-cta-btn">
            <i class="fas fa-map-location-dot"></i>View ${venue.venue_name} on Google Maps
        </a>

        <div class="section-heading-box">
            <div class="section-heading-box-title">Venue Essentials</div>
            <div class="section-heading-box-subtitle">Quick overview of location, capacity, and event planning basics.</div>
        </div>

        <div class="details-list-grid">
            <div class="details-list-item"><span><i class="fas fa-map-marker-alt"></i> Location</span><strong>${safeText(venue.location)}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-location-dot"></i> Address</span><strong>${safeText(venue.address)}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-users"></i> Hall Capacity</span><strong>${venue.seating_capacity || venue.capacity || 0} seats</strong></div>
            <div class="details-list-item"><span><i class="fas fa-utensils"></i> Dining Seats</span><strong>${venue.dining_capacity || 0}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-bowl-food"></i> Dining Type</span><strong>${safeText(venue.dining_type)}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-bell-concierge"></i> Buffet</span><strong>${buffetText}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-clock"></i> Timing</span><strong>${safeText(venue.timing_type)}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-indian-rupee-sign"></i> Advance</span><strong>${formatPrice(venue.advance_amount || 0)}</strong></div>
        </div>

        <div class="section-heading-box">
            <div class="section-heading-box-title">Facilities & Utilities</div>
            <div class="section-heading-box-subtitle">Kitchen support, parking, rooms, and operational amenities.</div>
        </div>

        <div class="details-list-grid">
            <div class="details-list-item"><span><i class="fas fa-kitchen-set"></i> Kitchen Specialty</span><strong>${safeText(venue.kitchen_specialty)}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-leaf"></i> Kitchen Food Support</span><strong>${safeText(venue.kitchen_food_support)}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-fire"></i> Kitchen Fuel</span><strong>${safeText(venue.kitchen_fuel_type)}${safeText(venue.kitchen_fuel_type) === 'Gas Cylinder' ? ` (${venue.gas_cylinder_count || 0} cylinders)` : ''}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-restroom"></i> Restrooms / Bathrooms</span><strong>${venue.restrooms_count || 0} / ${venue.bathrooms_count || 0}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-faucet"></i> Water Taps</span><strong>${venue.water_taps_count || 0}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-motorcycle"></i> Two-Wheeler Parking</span><strong>${venue.two_wheeler_parking_capacity || 0}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-car"></i> Car Parking</span><strong>${parkingText}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-wheelchair"></i> wheel chairn assistant</span><strong>${rampText}</strong></div>
        </div>

        <div class="section-heading-box">
            <div class="section-heading-box-title">Rooms, Contact & Notes</div>
            <div class="section-heading-box-subtitle">Useful final details before you confirm your booking.</div>
        </div>

        <div class="details-list-grid">
            <div class="details-list-item"><span><i class="fas fa-person-booth"></i> Groom Rooms</span><strong>${venue.groom_rooms_count || 0}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-person-dress"></i> Bride Rooms</span><strong>${venue.bride_rooms_count || 0}</strong></div>
            <div class="details-list-item"><span><i class="fas fa-phone"></i> Owner Mobile</span><strong>${safeText(venue.owner_mobile)}</strong></div>
            <div class="details-list-item full-width"><span><i class="fas fa-note-sticky"></i> Advance Details</span><strong>${safeText(venue.advance_details)}</strong></div>
            <div class="details-list-item full-width"><span><i class="fas fa-check-circle"></i> Additional Facilities</span><strong>${safeText(venue.facilities, 'Not specified')}</strong></div>
        </div>

        <div class="layout-note-box">
            <i class="fas fa-sparkles"></i>
            Smooth layout update applied: better readability for long venue detail lists.
        </div>
    `;
}

async function apiCall(endpoint, method = 'GET', data = null) {
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const token = getAuthToken();
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        let response;

        try {
            response = await fetch(`${API_BASE_URL}${normalizedEndpoint}`, options);
        } catch (primaryError) {
            // Retry with 127.0.0.1 if localhost resolution fails on some systems.
            if (API_BASE_URL.includes('localhost')) {
                const fallbackBaseUrl = API_BASE_URL.replace('localhost', '127.0.0.1');
                response = await fetch(`${fallbackBaseUrl}${normalizedEndpoint}`, options);
            } else {
                throw primaryError;
            }
        }

        const result = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.clear();
                redirectToLogin();
            }
            throw new Error(result.message || 'API Error');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);

        if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
            throw new Error('Cannot connect to backend. Start API with: python server.py (inside backend folder).');
        }

        throw error;
    }
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('main') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// ==========================================
// Authentication Functions
// ==========================================

function switchForm(formType) {
    document.getElementById('loginForm').style.display = formType === 'login' ? 'block' : 'none';
    document.getElementById('registerForm').style.display = formType === 'register' ? 'block' : 'none';
}

// Login Form Submit
if (document.getElementById('loginFormElement')) {
    document.getElementById('loginFormElement').addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        try {
            const response = await apiCall('/auth/login', 'POST', { email, password });
            
            setAuthToken(response.token);
            setCurrentUser(response.user);
            
            showAlert('Login successful! Redirecting...', 'success');
            setTimeout(() => redirectToHome(), 1500);
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    });
}

// Register Form Submit
if (document.getElementById('registerFormElement')) {
    document.getElementById('registerFormElement').addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('registerName').value;
        const email = document.getElementById('registerEmail').value;
        const phone = document.getElementById('registerPhone').value;
        const password = document.getElementById('registerPassword').value;
        const confirmPassword = document.getElementById('registerConfirmPassword').value;

        if (password !== confirmPassword) {
            showAlert('Passwords do not match', 'danger');
            return;
        }

        try {
            await apiCall('/auth/register', 'POST', { name, email, phone, password });
            showAlert('Registration successful! Please login.', 'success');
            setTimeout(() => switchForm('login'), 1500);
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    });
}

function logout() {
    localStorage.clear();
    redirectToLogin();
}

// Check authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    const currentPage = window.location.pathname;
    
    // Pages that don't require authentication
    const publicPages = ['login.html', 'register.html', 'index.html', '/'];
    const isPublicPage = publicPages.some(page => currentPage.includes(page));

    if (!isPublicPage && !isAuthenticated()) {
        redirectToLogin();
    }
});

// ==========================================
// Venue Functions
// ==========================================

async function loadAllVenues() {
    try {
        const response = await apiCall('/venues/');
        const venuesList = document.getElementById('venuesList') || document.getElementById('featuredVenues');
        const noVenuesFound = document.getElementById('noVenuesFound');
        
        if (!venuesList) return;

        venuesList.innerHTML = '';

        if (!response.venues || response.venues.length === 0) {
            if (noVenuesFound) noVenuesFound.style.display = 'block';
            return;
        }

        if (noVenuesFound) noVenuesFound.style.display = 'none';

        // Update venue count
        const venueCount = document.getElementById('venueCount');
        if (venueCount) {
            venueCount.textContent = `Showing ${response.venues.length} amazing venues`;
        }

        response.venues.forEach((venue, index) => {
            const venueCard = document.createElement('div');
            venueCard.className = 'col-md-6 col-lg-4 venue-card-animated';
            
            // Generate star rating display
            const rating = venue.rating || 4.0;
            const stars = '★'.repeat(Math.floor(rating)) + (rating % 1 >= 0.5 ? '★' : '');
            const emptyStars = '☆'.repeat(5 - Math.ceil(rating));
            
            // Use thumbnail URL from database, fallback to placeholder
            const imageUrl = venue.thumbnail_url || venue.image_url || 'https://via.placeholder.com/400x250?text=' + encodeURIComponent(venue.venue_name);
            
            const acBadge = venue.isAC ? '<span class="venue-badge">❄️ AC Available</span>' : '';
            const parkingText = isTruthyFlag(venue.car_parking_available) ? `Parking: ${venue.max_car_parking_capacity || 0} cars` : 'Parking: Not Available';
            const diningText = `Dining: ${venue.dining_capacity || 0}`;
            
            venueCard.innerHTML = `
                <div class="card venue-card h-100" style="position: relative;">
                    ${acBadge}
                    <img src="${imageUrl}" alt="${venue.venue_name}" class="card-img-top" onerror="this.src='https://via.placeholder.com/400x250?text=${encodeURIComponent(venue.venue_name)}'">
                    <div class="card-body d-flex flex-column">
                        <h5 class="venue-name">${venue.venue_name}</h5>
                        <p class="venue-location"><i class="fas fa-map-marker-alt"></i> ${venue.location}</p>
                        <p class="venue-capacity"><i class="fas fa-users"></i> Capacity: ${venue.capacity} people</p>
                        <p class="venue-rating"><i class="fas fa-star"></i> ${rating.toFixed(1)}/5.0</p>
                        <p class="venue-price"><i class="fas fa-rupee-sign"></i> ${formatPrice(venue.price)}</p>
                        <p class="venue-facilities"><i class="fas fa-check-circle"></i> ${venue.facilities || 'Premium Facilities'}</p>
                        <p class="venue-facilities mb-1"><i class="fas fa-utensils"></i> ${diningText}</p>
                        <p class="venue-facilities"><i class="fas fa-car"></i> ${parkingText}</p>
                        <div class="d-grid gap-2 mt-auto">
                            <button class="btn btn-sm btn-view-details" onclick="viewVenueDetails(${venue.id})">
                                <i class="fas fa-eye me-1"></i> View Details
                            </button>
                            <button class="btn btn-sm btn-book-venue" onclick="selectVenueForBooking(${venue.id})">
                                <i class="fas fa-calendar me-1"></i> Book Now
                            </button>
                        </div>
                    </div>
                </div>
            `;
            venuesList.appendChild(venueCard);
        });
    } catch (error) {
        console.error('Error loading venues:', error);
        showAlert('Failed to load venues', 'danger');
    }
}

async function viewVenueDetails(venueId) {
    window.location.href = `venue-details.html?venueId=${venueId}`;
}

function selectVenueForBooking(venueId) {
    currentVenue = { id: venueId };
    window.location.href = `booking.html?venueId=${venueId}`;
}

function proceedToBooking() {
    if (currentVenue) {
        selectVenueForBooking(currentVenue.id);
    }
}

async function initializeVenueDetailsPage() {
    const detailsContainer = document.getElementById('venueDetailsPageContent');
    if (!detailsContainer) {
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const venueId = urlParams.get('venueId');

    if (!venueId) {
        detailsContainer.innerHTML = '<div class="alert alert-danger">Invalid venue selected. Please go back and choose a venue.</div>';
        return;
    }

    try {
        const response = await apiCall(`/venues/${venueId}`);
        const venue = response.venue;
        currentVenue = venue;

        const pageTitle = document.getElementById('venueDetailsPageTitle');
        const pageSubtitle = document.getElementById('venueDetailsPageSubtitle');
        if (pageTitle) {
            pageTitle.textContent = venue.venue_name;
        }
        if (pageSubtitle) {
            pageSubtitle.textContent = `${safeText(venue.location)} | ${safeText(venue.address)}`;
        }

        detailsContainer.innerHTML = buildVenueDetailsHtml(venue);
    } catch (error) {
        console.error('Error loading venue details page:', error);
        detailsContainer.innerHTML = '<div class="alert alert-danger">Failed to load venue details.</div>';
    }
}

async function filterVenues() {
    try {
        const location = document.getElementById('searchVenueLocation')?.value || '';
        const minPrice = 10000;
        const maxPrice = parseInt(document.getElementById('priceSlider')?.value) || 100000;

        let url = `/venues/?min_price=${minPrice}&max_price=${maxPrice}`;
        if (location) {
            url += `&location=${encodeURIComponent(location)}`;
        }

        const response = await apiCall(url);
        const venuesList = document.getElementById('venuesList');
        const noVenuesFound = document.getElementById('noVenuesFound');
        
        venuesList.innerHTML = '';

        if (!response.venues || response.venues.length === 0) {
            if (noVenuesFound) noVenuesFound.style.display = 'block';
            return;
        }

        if (noVenuesFound) noVenuesFound.style.display = 'none';

        // Update count
        const venueCount = document.getElementById('venueCount');
        if (venueCount) {
            venueCount.textContent = `Found ${response.venues.length} venue(s) matching your criteria`;
        }

        response.venues.forEach((venue, index) => {
            const venueCard = document.createElement('div');
            venueCard.className = 'col-md-6 col-lg-4 venue-card-animated';
            
            // Generate star rating
            const rating = venue.rating || 4.0;
            const imageUrl = venue.thumbnail_url || venue.image_url || 'https://via.placeholder.com/400x250?text=' + encodeURIComponent(venue.venue_name);
            const acBadge = venue.isAC ? '<span class="venue-badge">❄️ AC Available</span>' : '';
            const parkingText = isTruthyFlag(venue.car_parking_available) ? `Parking: ${venue.max_car_parking_capacity || 0} cars` : 'Parking: Not Available';
            const diningText = `Dining: ${venue.dining_capacity || 0}`;
            
            venueCard.innerHTML = `
                <div class="card venue-card h-100" style="position: relative;">
                    ${acBadge}
                    <img src="${imageUrl}" alt="${venue.venue_name}" class="card-img-top" onerror="this.src='https://via.placeholder.com/400x250?text=${encodeURIComponent(venue.venue_name)}'">
                    <div class="card-body d-flex flex-column">
                        <h5 class="venue-name">${venue.venue_name}</h5>
                        <p class="venue-location"><i class="fas fa-map-marker-alt"></i> ${venue.location}</p>
                        <p class="venue-capacity"><i class="fas fa-users"></i> Capacity: ${venue.capacity} people</p>
                        <p class="venue-rating"><i class="fas fa-star"></i> ${rating.toFixed(1)}/5.0</p>
                        <p class="venue-price"><i class="fas fa-rupee-sign"></i> ${formatPrice(venue.price)}</p>
                        <p class="venue-facilities"><i class="fas fa-check-circle"></i> ${venue.facilities || 'Premium Facilities'}</p>
                        <p class="venue-facilities mb-1"><i class="fas fa-utensils"></i> ${diningText}</p>
                        <p class="venue-facilities"><i class="fas fa-car"></i> ${parkingText}</p>
                        <div class="d-grid gap-2 mt-auto">
                            <button class="btn btn-sm btn-view-details" onclick="viewVenueDetails(${venue.id})">
                                <i class="fas fa-eye me-1"></i> View Details
                            </button>
                            <button class="btn btn-sm btn-book-venue" onclick="selectVenueForBooking(${venue.id})">
                                <i class="fas fa-calendar me-1"></i> Book Now
                            </button>
                        </div>
                    </div>
                </div>
            `;
            venuesList.appendChild(venueCard);
        });
    } catch (error) {
        console.error('Error filtering venues:', error);
        showAlert('Failed to filter venues', 'danger');
    }
}

function searchVenues() {
    filterVenues();
}

function updatePriceSlider() {
    const priceSlider = document.getElementById('priceSlider');
    if (!priceSlider) return;
    
    const maxPrice = parseInt(priceSlider.value) || 100000;
    const minPrice = 10000;
    
    // Format price with fallback for browsers that don't support toLocaleString
    const formatPrice = (price) => {
        try {
            return price.toLocaleString('en-IN');
        } catch (e) {
            return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        }
    };
    
    const maxPriceElem = document.getElementById('maxPriceValue');
    const minPriceElem = document.getElementById('minPriceValue');
    
    if (minPriceElem) minPriceElem.value = formatPrice(minPrice);
    if (maxPriceElem) maxPriceElem.value = formatPrice(maxPrice) + '+';
    
    // Auto-filter venues when slider changes
    filterVenues();
}

function updatePrice() {
    const minPrice = document.getElementById('minPrice')?.value || 10000;
    const maxPrice = document.getElementById('maxPrice')?.value || 100000;

    document.getElementById('minPriceValue').textContent = minPrice;
    document.getElementById('maxPriceValue').textContent = maxPrice;
    document.getElementById('priceDisplay').textContent = `₹${minPrice} - ₹${maxPrice}`;
}

// ==========================================
// Booking Functions
// ==========================================

async function initializeBooking() {
    const urlParams = new URLSearchParams(window.location.search);
    const venueId = urlParams.get('venueId');

    if (!venueId) {
        showAlert('Invalid venue selection', 'danger');
        return;
    }

    try {
        const response = await apiCall(`/venues/${venueId}`);
        const venue = response.venue;

        document.getElementById('bookingVenueName').textContent = venue.venue_name;
        document.getElementById('bookingVenueLocation').textContent = venue.location;
        document.getElementById('bookingVenueCapacity').textContent = venue.capacity;
        document.getElementById('bookingVenuePrice').textContent = venue.price;
        document.getElementById('totalAmount').textContent = venue.price;

        const today = new Date().toISOString().split('T')[0];
        const startDateInput = document.getElementById('bookingStartDate');
        const endDateInput = document.getElementById('bookingEndDate');
        const timeFrameSelect = document.getElementById('bookingTimeFrame');
        const startTimeInput = document.getElementById('bookingStartTime');
        const endTimeInput = document.getElementById('bookingEndTime');

        if (startDateInput) {
            startDateInput.min = today;
            startDateInput.value = today;
            selectedStartDate = today;
        }

        if (endDateInput) {
            endDateInput.min = today;
            endDateInput.value = today;
            selectedEndDate = today;
        }

        if (timeFrameSelect) {
            applyBookingTimeFrame(timeFrameSelect.value);
        }

        if (startTimeInput) {
            startTimeInput.value = selectedStartTime;
        }

        if (endTimeInput) {
            endTimeInput.value = selectedEndTime;
        }

        attachBookingInputListeners();
        refreshBookingSelectionDisplay();

        currentVenue = venue;

        initializeCalendar(venueId);
    } catch (error) {
        showAlert('Failed to load venue details', 'danger');
    }
}

function initializeCalendar(venueId) {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: ''
        },
        dateClick: function(info) {
            if (info.date < new Date()) {
                showAlert('Cannot book dates in the past', 'danger');
                return;
            }

            const clickedDate = info.date.toISOString().split('T')[0];
            selectedStartDate = clickedDate;
            selectedEndDate = clickedDate;

            const startDateInput = document.getElementById('bookingStartDate');
            const endDateInput = document.getElementById('bookingEndDate');
            if (startDateInput) {
                startDateInput.value = clickedDate;
            }
            if (endDateInput) {
                endDateInput.value = clickedDate;
            }
            refreshBookingSelectionDisplay();
            
            // Highlight selected date
            calendar.view.calendar.getEvents().forEach(event => event.remove());
            calendar.addEvent({
                start: clickedDate,
                end: clickedDate,
                display: 'background',
                backgroundColor: '#28a745'
            });
        },
        events: async function(info, successCallback, failureCallback) {
            try {
                const response = await apiCall(`/bookings/calendar/${venueId}`);
                const events = response.booked_dates.map(date => ({
                    start: date,
                    end: date,
                    display: 'background',
                    backgroundColor: '#dc3545'
                }));
                successCallback(events);
            } catch (error) {
                failureCallback(error);
            }
        }
    });

    calendar.render();
}


function attachBookingInputListeners() {
    const startDateInput = document.getElementById('bookingStartDate');
    const endDateInput = document.getElementById('bookingEndDate');
    const timeFrameSelect = document.getElementById('bookingTimeFrame');
    const startTimeInput = document.getElementById('bookingStartTime');
    const endTimeInput = document.getElementById('bookingEndTime');

    if (timeFrameSelect) {
        timeFrameSelect.addEventListener('change', () => {
            applyBookingTimeFrame(timeFrameSelect.value);
            refreshBookingSelectionDisplay();
        });
    }

    if (startDateInput) {
        startDateInput.addEventListener('change', () => {
            selectedStartDate = startDateInput.value;
            if (endDateInput && endDateInput.value < selectedStartDate) {
                endDateInput.value = selectedStartDate;
                selectedEndDate = selectedStartDate;
            }
            if (endDateInput) {
                endDateInput.min = selectedStartDate;
            }
            refreshBookingSelectionDisplay();
        });
    }

    if (endDateInput) {
        endDateInput.addEventListener('change', () => {
            selectedEndDate = endDateInput.value;
            refreshBookingSelectionDisplay();
        });
    }

    if (startTimeInput) {
        startTimeInput.addEventListener('change', () => {
            selectedStartTime = startTimeInput.value || '09:00';
            if (timeFrameSelect) {
                timeFrameSelect.value = 'custom';
            }
            refreshBookingSelectionDisplay();
        });
    }

    if (endTimeInput) {
        endTimeInput.addEventListener('change', () => {
            selectedEndTime = endTimeInput.value || '21:00';
            if (timeFrameSelect) {
                timeFrameSelect.value = 'custom';
            }
            refreshBookingSelectionDisplay();
        });
    }
}


function calculateBookingDays(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const dayMs = 1000 * 60 * 60 * 24;
    const diff = Math.floor((end - start) / dayMs) + 1;
    return Math.max(1, diff);
}


function refreshBookingSelectionDisplay() {
    if (!selectedStartDate || !selectedEndDate) {
        return;
    }

    const selectedDateEl = document.getElementById('selectedDate');
    if (selectedDateEl) {
        const startLabel = formatDate(selectedStartDate);
        const endLabel = formatDate(selectedEndDate);
        const dateLabel = selectedStartDate === selectedEndDate
            ? startLabel
            : `${startLabel} to ${endLabel}`;
        selectedDateEl.textContent = `${dateLabel} (${selectedStartTime} - ${selectedEndTime})`;
    }

    const totalAmountEl = document.getElementById('totalAmount');
    if (totalAmountEl && currentVenue && currentVenue.price !== undefined) {
        const days = calculateBookingDays(selectedStartDate, selectedEndDate);
        const total = Number(currentVenue.price) * days;
        totalAmountEl.textContent = total.toLocaleString('en-IN');
    }
}

async function confirmBooking() {
    // Validate all required fields
    if (!selectedStartDate || !selectedEndDate || !selectedStartTime || !selectedEndTime) {
        showAlert('⚠️ Please select start/end date and time', 'danger');
        return;
    }

    if (selectedEndDate < selectedStartDate) {
        showAlert('⚠️ End date cannot be before start date', 'danger');
        return;
    }

    if (selectedStartDate === selectedEndDate && selectedEndTime <= selectedStartTime) {
        showAlert('⚠️ End time must be after start time for same-day booking', 'danger');
        return;
    }
    
    if (!currentVenue) {
        showAlert('⚠️ Venue information not found. Please reload the page.', 'danger');
        return;
    }
    
    if (!currentVenue.id || !currentVenue.venue_name || currentVenue.price === undefined) {
        showAlert('⚠️ Incomplete venue details. Please reload the page.', 'danger');
        console.error('Missing venue properties:', currentVenue);
        return;
    }

    try {
        showAlert('⏳ Processing your booking...', 'info');
        
        // Create booking (email is automatically sent by backend)
        const bookingResponse = await apiCall('/bookings/', 'POST', {
            venue_id: currentVenue.id,
            booking_date: selectedStartDate,
            start_date: selectedStartDate,
            end_date: selectedEndDate,
            start_time: selectedStartTime,
            end_time: selectedEndTime
        });

        if (!bookingResponse || !bookingResponse.booking_id) {
            throw new Error(bookingResponse?.message || 'Failed to create booking');
        }

        currentBookingId = bookingResponse.booking_id;
        
        // Show success message
        showAlert(
            `✅ Booking Confirmed!\n\n` +
            `📧 Confirmation email has been sent to your registered email address.\n\n` +
            `Venue: ${bookingResponse.venue_name}\n` +
            `Booking Window: ${bookingResponse.start_date} ${bookingResponse.start_time} to ${bookingResponse.end_date} ${bookingResponse.end_time}\n` +
            `Amount: ₹${bookingResponse.amount}\n` +
            `Booking ID: ${bookingResponse.booking_id}`,
            'success'
        );
        
        // Redirect to dashboard after booking
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 3000);
        
    } catch (error) {
        // Check if it's a double booking error
        if (error.message && (error.message.includes('already booked') || error.message.includes('already booked on this date'))) {
            showAlert('⚠️ This date is no longer available. Please select another date.', 'danger');
        } else {
            showAlert('❌ Error confirming booking: ' + (error.message || 'Unknown error'), 'danger');
        }
        console.error('Booking error:', error);
    }
}

// ==========================================
// Dashboard Functions
// ==========================================

async function loadDashboardStats() {
    try {
        // Load user profile
        await loadUserProfile();

        const statsResponse = await apiCall('/bookings/dashboard/stats');
        const stats = statsResponse.stats;

        document.getElementById('totalBookings').textContent = stats.total_bookings;
        document.getElementById('confirmedBookings').textContent = stats.confirmed_bookings;
        document.getElementById('totalSpent').textContent = stats.total_spent;

        // Load bookings
        await loadRecentBookings();

        // Initialize charts
        initializeCharts();
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

async function loadUserProfile() {
    try {
        const response = await apiCall('/auth/profile');
        const user = response.user;

        // Display user name in bold
        document.getElementById('userNameDisplay').textContent = user.name;
        
        // Display user email
        document.getElementById('userEmailDisplay').textContent = user.email;

        // Update current user
        setCurrentUser(user);
    } catch (error) {
        console.error('Error loading user profile:', error);
    }
}

async function loadRecentBookings() {
    try {
        const response = await apiCall('/bookings/');
        const bookings = response.bookings || [];

        const recentBookingsDiv = document.getElementById('recentBookings');
        if (!recentBookingsDiv) return;

        if (bookings.length === 0) {
            recentBookingsDiv.innerHTML = '<p class="text-center text-muted">No bookings yet. <a href="venues.html">Browse venues</a> to make your first booking.</p>';
            return;
        }

        const upcoming = bookings.filter(b => new Date(b.booking_date) > new Date()).length;
        document.getElementById('upcomingBookings').textContent = upcoming;

        let html = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-primary">
                        <tr>
                            <th>Venue Name</th>
                            <th>Location</th>
                            <th>Booking Date</th>
                            <th>Amount</th>
                            <th>Payment Status</th>
                            <th>Booking Status</th>
                            <th>Email Notification</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        bookings.forEach(booking => {
            const bookingDate = new Date(booking.booking_date);
            const today = new Date();
            const isUpcoming = bookingDate > today;
            
            let emailStatus = '';
            if (booking.email_sent === 1) {
                const emailTime = booking.email_sent_at 
                    ? new Date(booking.email_sent_at).toLocaleString('en-IN', {year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'})
                    : 'Just now';
                emailStatus = `<span class="badge bg-success" title="Sent on: ${emailTime}"><i class="fas fa-check"></i> ✉️ Sent</span><br><small class="text-muted">${emailTime}</small>`;
            } else {
                emailStatus = '<span class="badge bg-warning"><i class="fas fa-clock"></i> Pending</span>';
            }
            
            html += `
                <tr>
                    <td><strong>${booking.venue_name}</strong></td>
                    <td>${booking.location}</td>
                    <td>${formatDate(booking.booking_date)}</td>
                    <td>${formatPrice(booking.amount)}</td>
                    <td>
                        <span class="badge bg-${booking.payment_status === 'PAID' ? 'success' : booking.payment_status === 'PENDING' ? 'warning' : 'danger'}">
                            ${booking.payment_status}
                        </span>
                    </td>
                    <td>
                        <span class="badge bg-${booking.booking_status === 'CONFIRMED' ? 'success' : 'secondary'}">
                            ${booking.booking_status}
                        </span>
                    </td>
                    <td>
                        ${emailStatus}
                    </td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="viewBooking(${booking.id})">
                            <i class="fas fa-eye"></i> View
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        recentBookingsDiv.innerHTML = html;
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

function toggleEmailNotification(bookingId, enabled) {
    const status = enabled ? 'Notification enabled' : 'Notification disabled';
    const alertType = enabled ? 'success' : 'warning';
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${alertType} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-bell me-2"></i>${status} for booking #${bookingId}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('.dashboard').insertBefore(alertDiv, document.querySelector('.dashboard').firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

function initializeCharts() {
    // Booking Statistics Chart
    const bookingCtx = document.getElementById('bookingChart');
    if (bookingCtx) {
        new Chart(bookingCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Bookings',
                    data: [10, 15, 8, 20, 18, 22],
                    backgroundColor: '#0d6efd',
                    borderColor: '#0b5bdb',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true
                    }
                }
            }
        });
    }

    // Revenue Chart
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue (₹)',
                    data: [50000, 75000, 40000, 100000, 90000, 110000],
                    borderColor: '#198754',
                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                    borderWidth: 2,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true
                    }
                }
            }
        });
    }
}

function viewBooking(bookingId) {
    // Placeholder - can be expanded with modal view
    alert('Viewing booking ' + bookingId);
}

// ==========================================
// Booking Cancellation Functions
// ==========================================

function cancelBookingConfirm(bookingId, venueName) {
    if (confirm(`Are you sure you want to cancel this booking for ${venueName}? This action cannot be undone.`)) {
        cancelBooking(bookingId);
    }
}

async function cancelBooking(bookingId) {
    try {
        showAlert('⏳ Processing cancellation...', 'info');
        
        const response = await apiCall(`/bookings/${bookingId}/cancel`, 'POST');
        
        showAlert('✅ Booking cancelled successfully!', 'success');
        
        // Reload the bookings after a short delay
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    } catch (error) {
        showAlert('❌ Error cancelling booking: ' + (error.message || 'Unknown error'), 'danger');
        console.error('Cancellation error:', error);
    }
}

// ==========================================
// Feedback Functions
// ==========================================

async function loadUserBookings() {
    try {
        const response = await apiCall('/bookings/');
        const bookings = response.bookings || [];

        const select = document.getElementById('bookingSelect');
        if (!select) return;

        bookings.forEach(booking => {
            const option = document.createElement('option');
            option.value = booking.id;
            option.textContent = `${booking.venue_name} - ${formatDate(booking.booking_date)}`;
            select.appendChild(option);
        });

        const params = new URLSearchParams(window.location.search);
        const bookingIdFromUrl = params.get('booking_id');
        if (bookingIdFromUrl && bookings.some((booking) => String(booking.id) === bookingIdFromUrl)) {
            select.value = bookingIdFromUrl;
        }
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

async function loadAllFeedback() {
    try {
        const response = await apiCall('/feedback/');
        const feedbacks = response.feedback || [];

        const allFeedbackDiv = document.getElementById('allFeedback');
        if (!allFeedbackDiv) return;

        if (feedbacks.length === 0) {
            allFeedbackDiv.innerHTML = '<p class="text-center">No feedback yet.</p>';
            return;
        }

        let html = '';
        feedbacks.forEach(feedback => {
            const stars = '⭐'.repeat(feedback.rating) + '☆'.repeat(5 - feedback.rating);
            html += `
                <div class="card mb-3">
                    <div class="card-body">
                        <h6 class="card-title">${feedback.name}</h6>
                        <p class="mb-2">${stars}</p>
                        <p class="card-text">${feedback.message || 'No comment'}</p>
                        <small class="text-muted">Reviewed venue: ${feedback.venue_name || 'N/A'}</small>
                    </div>
                </div>
            `;
        });

        allFeedbackDiv.innerHTML = html;
    } catch (error) {
        console.error('Error loading feedback:', error);
    }
}

// Feedback Form Submit
if (document.getElementById('feedbackForm')) {
    document.getElementById('feedbackForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const bookingId = document.getElementById('bookingSelect').value;
        const rating = document.querySelector('input[name="rating"]:checked')?.value;
        const message = document.getElementById('feedbackMessage').value;

        if (!bookingId || !rating) {
            showAlert('Please select a booking and rating', 'danger');
            return;
        }

        try {
            await apiCall('/feedback/', 'POST', {
                booking_id: parseInt(bookingId),
                rating: parseInt(rating),
                message
            });

            showAlert('Feedback submitted successfully!', 'success');
            document.getElementById('feedbackForm').reset();
            loadAllFeedback();
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    });
}

// Initialize page-specific functions
if (window.location.pathname.includes('booking.html')) {
    document.addEventListener('DOMContentLoaded', initializeBooking);
}

if (window.location.pathname.includes('home.html')) {
    document.addEventListener('DOMContentLoaded', () => {
        loadAllVenues();
        updatePriceSlider();
    });
}

if (window.location.pathname.includes('venues.html')) {
    document.addEventListener('DOMContentLoaded', () => {
        loadAllVenues();
        updatePriceSlider();
    });
}

if (window.location.pathname.includes('venue-details.html')) {
    document.addEventListener('DOMContentLoaded', initializeVenueDetailsPage);
}

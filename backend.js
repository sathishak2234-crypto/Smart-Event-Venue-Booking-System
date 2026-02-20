window.onload = function () {

/* ================= VARIABLES ================= */

let currentUser = "";
let bookings = JSON.parse(localStorage.getItem("bookings")) || [];

/* ================= VENUE DATA ================= */

const venues = [ 
    { id: 1, name: "Subhalakshmi Mahal", location: "TT Nagar, Sekkalai", capacity: 800, price: 60000, isAC: true, rating: 4.3 },
  { id: 2, name: "PLP Palace Wedding Hall", location: "Ananda Nagar", capacity: 1000, price: 85000, isAC: true, rating: 4.5 },
  { id: 3, name: "Sathguru Gnananandha Marriage Hall", location: "Sekkalai", capacity: 700, price: 50000, isAC: false, rating: 4.1 },
  { id: 4, name: "SR Grand Mahal", location: "Burma Colony", capacity: 900, price: 75000, isAC: true, rating: 4.4 },
  { id: 5, name: "Apurva Marriage Hall", location: "Kannadasan Nagar", capacity: 600, price: 45000, isAC: false, rating: 4.0 },
  { id: 6, name: "KVS Mahal", location: "Ariyakudi Main Road", capacity: 750, price: 55000, isAC: false, rating: 4.1 },
  { id: 7, name: "6X Party Hall", location: "Arumugam Nagar", capacity: 300, price: 25000, isAC: true, rating: 4.0 },
  { id: 8, name: "Abirami Palace", location: "NH536, Soorakudi", capacity: 1000, price: 90000, isAC: true, rating: 4.6 },
  { id: 9, name: "Shri Maadan Mahal", location: "Ananda Nagar", capacity: 650, price: 48000, isAC: false, rating: 4.2 },
  { id: 10, name: "Dhanalakshmi Marriage Hall", location: "Kallukatti", capacity: 500, price: 40000, isAC: false, rating: 4.0 },
  { id: 11, name: "Anugraha Marriage Hall", location: "Kallukatti", capacity: 700, price: 100000, isAC: true, rating: 4.5 },
  { id: 12, name: "LM Marriage Hall", location: "Devakottai Road, Senjai", capacity: 550, price: 52000, isAC: true, rating: 4.3 },
  { id: 13, name: "Alagammai Mahal", location: "Railway Station Road", capacity: 800, price: 65000, isAC: true, rating: 3.5 },
  { id: 14, name: "Amaravathy Marriage Hall", location: "Ananda Nagar", capacity: 600, price: 45000, isAC: false, rating: 3.9 },
  { id: 15, name: "Rajeswari Mahal", location: "Kalanivasal", capacity: 500, price: 42000, isAC: false, rating: 4.0 },
  { id: 16, name: "APS Hall A/C", location: "Police Colony Road", capacity: 300, price: 30000, isAC: true, rating: 4.1 },
  { id: 17, name: "Sri Muthukrishna Mahal", location: "Kalanivasal", capacity: 600, price: 40000, isAC: false, rating: 3.8 },
  { id: 18, name: "Krish Hall", location: "Old Bus Stand", capacity: 400, price: 35000, isAC: true, rating: 4.5 },
  { id: 19, name: "M.A.M Mahal", location: "Sekkalai Road", capacity: 500, price: 45000, isAC: true, rating: 4.2 },
  { id: 20, name: "Dhena Valli Mahal", location: "Devakottai Road", capacity: 600, price: 38000, isAC: false, rating: 3.9 },
  { id: 21, name: "Meena Mahal A/C", location: "Iluppakkudi Road", capacity: 700, price: 55000, isAC: true, rating: 4.1 },
  { id: 22, name: "Dharma Shastha Mandapam", location: "Soodamanipuram", capacity: 500, price: 35000, isAC: false, rating: 4.0 },
  { id: 23, name: "Saana Meena Thirumana Mandapam", location: "Sekkalai", capacity: 800, price: 60000, isAC: true, rating: 4.2 },
  { id: 24, name: "Sankara Mani Mandapam", location: "Sekkalai", capacity: 400, price: 30000, isAC: false, rating: 4.1 },
  { id: 25, name: "Prasanna Mahal", location: "Pari Nagar", capacity: 750, price: 58000, isAC: true, rating: 4.3 },
  { id: 26, name: "Vasavi Mahal", location: "Bharathi Nagar", capacity: 500, price: 35000, isAC: false, rating: 4.0 },
  { id: 27, name: "Srinivasa Mahal A/C", location: "Ariyakudi Road", capacity: 650, price: 50000, isAC: true, rating: 4.2 },
  { id: 28, name: "Lena Meena Mahal", location: "Near Temple", capacity: 900, price: 70000, isAC: true, rating: 4.4 },
  { id: 29, name: "Ganapathy Mahal", location: "Karaikudi Local", capacity: 400, price: 25000, isAC: false, rating: 3.8 },
  { id: 30, name: "Rajalakshmi Mahal", location: "Karaikudi", capacity: 600, price: 45000, isAC: true, rating: 4.0 },
  { id: 31, name: "Kalaignar Arivalayam", location: "Karaikudi Central", capacity: 1200, price: 95000, isAC: true, rating: 4.6 },
  { id: 32, name: "Sethu Meena Mahal", location: "Karaikudi", capacity: 500, price: 35000, isAC: false, rating: 3.9 },
  { id: 33, name: "Sai Sakthi Marriage Hall", location: "Karaikudi", capacity: 450, price: 30000, isAC: false, rating: 4.0 },
  { id: 34, name: "Sri Raghavendra Marriage Hall", location: "Karaikudi", capacity: 550, price: 40000, isAC: false, rating: 4.1 },
  { id: 35, name: "Murugan Kalyana Mandapam", location: "Karaikudi", capacity: 600, price: 38000, isAC: false, rating: 4.0 },
  { id: 36, name: "Shakthi Duraisamy Mandapam", location: "Karaikudi", capacity: 700, price: 50000, isAC: true, rating: 4.2 },
  { id: 37, name: "Sri Bhavani Mandapam", location: "Karaikudi", capacity: 500, price: 35000, isAC: false, rating: 3.8 },
  { id: 38, name: "Meenambika Mandapam", location: "Karaikudi", capacity: 400, price: 30000, isAC: false, rating: 4.1 },
  { id: 39, name: "Ayyanar Kalyana Mandapam", location: "Karaikudi", capacity: 800, price: 55000, isAC: false, rating: 4.0 },
  { id: 40, name: "Seetha Mahal", location: "Karaikudi", capacity: 650, price: 48000, isAC: true, rating: 4.3 },
  { id: 41, name: "Sri Aranganathan Marriage Hall", location: "Karaikudi", capacity: 500, price: 35000, isAC: false, rating: 4.0 },
  { id: 42, name: "Lakshmi Narasimha Marriage Hall", location: "Karaikudi", capacity: 600, price: 42000, isAC: false, rating: 4.1 },
  { id: 43, name: "Sri Sakthi Marriage Hall", location: "Karaikudi", capacity: 450, price: 32000, isAC: false, rating: 3.9 },
  { id: 44, name: "Sri Durga Parameswari Hall", location: "Karaikudi", capacity: 500, price: 35000, isAC: true, rating: 4.1 },
  { id: 45, name: "Arunachala Mahal", location: "Karaikudi", capacity: 900, price: 75000, isAC: true, rating: 4.5 },
  { id: 46, name: "Sri Venkateswara Marriage Hall", location: "Karaikudi", capacity: 700, price: 45000, isAC: false, rating: 4.0 },
  { id: 47, name: "Sri Krishna Marriage Hall", location: "Karaikudi", capacity: 550, price: 38000, isAC: false, rating: 3.9 },
  { id: 48, name: "Sri Lakshmi Marriage Hall", location: "Karaikudi", capacity: 600, price: 40000, isAC: false, rating: 4.0 },
  { id: 49, name: "Sri Balaji Marriage Hall", location: "Karaikudi", capacity: 500, price: 35000, isAC: false, rating: 4.1 },
  { id: 50, name: "Sri Ganesh Marriage Hall", location: "Karaikudi", capacity: 400, price: 28000, isAC: false, rating: 3.8 }
];

/* ================= DOM ELEMENTS ================= */

let venueList = document.getElementById("venueList");
let venueSelect = document.getElementById("venueSelect");
let bookingHistory = document.getElementById("bookingHistory");

let profileSection = document.getElementById("profileSection");
let profileName = document.getElementById("profileName");
let totalBookings = document.getElementById("totalBookings");
let profileBookings = document.getElementById("profileBookings");

let priceRange = document.getElementById("priceRange");
let minInput = document.getElementById("minPrice");
let maxInput = document.getElementById("maxPrice");

/* ================= AUTO LOGIN ================= */

let savedUser = localStorage.getItem("currentUser");

if (savedUser) {
    currentUser = savedUser;
    document.getElementById("welcome").innerHTML = "Welcome, " + currentUser;
    profileSection.style.display = "block";
    profileName.innerText = currentUser;
    updateProfile();
}

/* ================= DISPLAY VENUES ================= */

function displayVenues(minPrice, maxPrice) {

    venueList.innerHTML = "";
    venueSelect.innerHTML = "";

    venues.forEach((v, index) => {

        if (v.price >= minPrice && v.price <= maxPrice) {

            venueList.innerHTML += `
            <div class="card">
                <h3>${v.name}</h3>
                <p><b>Location:</b> ${v.location}</p>
                <p><b>Capacity:</b> ${v.capacity}</p>
                <p><b>Price:</b> ₹${v.price}</p>
                <p><b>AC:</b> ${v.isAC ? "Yes" : "No"}</p>
                <p><b>Rating:</b> ⭐ ${v.rating}</p>
                <button onclick="showMap('${v.name}', '${v.location}')">
                    📍 View Map
                </button>
            </div>
            `;

            venueSelect.innerHTML += `
                <option value="${index}">${v.name}</option>
            `;
        }
    });
}

displayVenues(0, priceRange.value);

/* ================= PRICE FILTER ================= */

priceRange.addEventListener("input", function () {
    maxInput.value = this.value;
    displayVenues(parseInt(minInput.value), parseInt(this.value));
});

window.filterVenues = function () {

    let min = parseInt(minInput.value);
    let max = parseInt(maxInput.value);

    if (min > max) {
        alert("Minimum price cannot be greater than Maximum price");
        return;
    }

    displayVenues(min, max);
};

/* ================= LOGIN ================= */

window.login = function () {

    currentUser = document.getElementById("username").value.trim();

    if (currentUser === "") {
        alert("Enter username!");
        return;
    }

    localStorage.setItem("currentUser", currentUser);

    document.getElementById("welcome").innerHTML =
        "Welcome, " + currentUser;

    profileSection.style.display = "block";
    profileName.innerText = currentUser;

    updateProfile();
};

/* ================= BOOKING ================= */

window.checkAvailability = function () {

    let date = document.getElementById("date").value;
    let venueIndex = venueSelect.value;

    let isBooked = bookings.some(
        b => b.date == date && b.venueIndex == venueIndex
    );

    alert(isBooked ? "❌ Date already booked!" : "✅ Date available!");
};
window.confirmBooking = function () {

    if (currentUser === "") {
        alert("Login first!");
        return;
    }

    let venueIndex = venueSelect.value;
    let date = document.getElementById("date").value;
    let eventType = document.getElementById("eventType").value;

    if (date === "" || eventType === "") {
        alert("Fill all details!");
        return;
    }

    let isBooked = bookings.some(
        b => b.date === date && b.venueIndex == venueIndex
    );

    if (isBooked) {
        alert("❌ Date already booked!");
        return;
    }

    let booking = {
        user: currentUser,
        venue: venues[venueIndex].name,
        venueIndex: venueIndex,
        date: date,
        event: eventType
    };

    bookings.push(booking);
    localStorage.setItem("bookings", JSON.stringify(bookings));

    bookingHistory.innerHTML += `
        <p><b>${booking.user}</b> booked 
        <b>${booking.venue}</b> on 
        ${booking.date} for ${booking.event}</p>
    `;

    alert("🎉 Booking Confirmed!");
    updateProfile();
};

/* ================= PROFILE ================= */

function updateProfile() {

    let userBookings = bookings.filter(
        b => b.user === currentUser
    );

    totalBookings.innerText = userBookings.length;
    profileBookings.innerHTML = "";

    if (userBookings.length === 0) {
        profileBookings.innerHTML = "<p>No bookings yet.</p>";
        return;
    }

    userBookings.forEach((b) => {

        profileBookings.innerHTML += `
            <div class="profile-card">
                <p><b>Venue:</b> ${b.venue}</p>
                <p><b>Date:</b> ${b.date}</p>
                <p><b>Event:</b> ${b.event}</p>
                <button onclick="cancelBooking('${b.venueIndex}','${b.date}')">
                    ❌ Cancel Booking
                </button>
                <hr>
            </div>
        `;
    });
}

/* ================= CANCEL BOOKING ================= */

window.cancelBooking = function (venueIndex, date) {

    let confirmCancel = confirm("Are you sure you want to cancel this booking?");

    if (!confirmCancel) return;

    bookings = bookings.filter(b =>
        !(b.user === currentUser &&
          b.venueIndex == venueIndex &&
          b.date === date)
    );

    localStorage.setItem("bookings", JSON.stringify(bookings));

    alert("✅ Booking Cancelled Successfully");

    updateProfile();
};

/* ================= LOGOUT ================= */

window.logout = function () {

    currentUser = "";
    localStorage.removeItem("currentUser");

    profileSection.style.display = "none";
    document.getElementById("welcome").innerHTML = "";
};

/* ================= GOOGLE MAP ================= */

window.showMap = function (venueName, location) {

    let selectedLocation = venueName + ", " + location;

    window.open(
        "https://www.google.com/maps/search/?api=1&query=" +
        encodeURIComponent(selectedLocation),
        "_blank"
    );
};

};

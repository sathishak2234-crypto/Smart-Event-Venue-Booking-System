# 🎉 Smart Event Venue Booking System

A full-stack web application designed to simplify the process of booking event venues. Users can browse venues, check availability, and make bookings, while administrators can manage venues and reservations efficiently.

---

## 🚀 Features

### 👤 User Features

* Browse available event venues
* View venue details (capacity, location, pricing)
* Book venues for specific dates
* View booking history

### 🛠️ Admin Features

* Add / update / delete venues
* Manage bookings
* View user activity
* Admin dashboard

---

## 🧰 Tech Stack

### 🔹 Frontend

* HTML, CSS, JavaScript

### 🔹 Backend

* Python (FastAPI / Flask)

### 🔹 Database

* SQLite / MySQL (based on your setup)

---

## 📂 Project Structure

```
SEV/
│
├── backend/          # API and server logic
├── frontend/         # UI files (HTML, CSS, JS)
├── database/         # Database schema or config
├── images/           # Sample images
│
├── app.py            # Main backend entry
├── backend.js        # (if used for frontend logic)
├── requirements.txt  # Python dependencies
├── .gitignore
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/sathishak2234-crypto/Smart-Event-Venue-Booking-System.git
cd Smart-Event-Venue-Booking-System
```

---

### 2️⃣ Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Run backend server

```bash
uvicorn backend.main:app --reload
```

---

### 5️⃣ Open frontend

Open `frontend/index.html` in your browser

---

## 🔐 Environment Variables

Create a `.env` file in root:

```
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
```

---

## 📸 Screenshots

*(Add screenshots here for better presentation)*

---

## 📈 Future Improvements

* Online payment integration
* Real-time booking availability
* Email/SMS notifications
* User authentication (JWT/OAuth)
* Mobile responsiveness

---

## 🤝 Contributing

Contributions are welcome!
Feel free to fork this repo and submit a pull request.

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 👨‍💻 Author

**Sathish Kumar**
GitHub: https://github.com/sathishak2234-crypto

---

⭐ If you like this project, don’t forget to star the repository!

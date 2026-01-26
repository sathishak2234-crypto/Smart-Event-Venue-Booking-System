from flask import Flask, render_template, request, redirect, url_for
import face_recognition
import os
from cryptography.fernet import Fernet

app = Flask(__name__)

UPLOAD_FOLDER = "encrypted_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load known face
known_image = face_recognition.load_image_file("faces/user1.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]

# Generate encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        file = request.files["face"]

        unknown_image = face_recognition.load_image_file(file)
        unknown_encodings = face_recognition.face_encodings(unknown_image)

        if len(unknown_encodings) == 0:
            return "No face detected ❌"

        result = face_recognition.compare_faces(
            [known_encoding], unknown_encodings[0]
        )

        if result[0]:
            return redirect(url_for("upload"))
        else:
            return "Face Not Matched ❌ Access Denied"

    return render_template("login.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        data = file.read()

        encrypted_data = cipher.encrypt(data)

        with open(os.path.join(UPLOAD_FOLDER, file.filename), "wb") as f:
            f.write(encrypted_data)

        return "File Encrypted & Stored Securely 🔐"

    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)

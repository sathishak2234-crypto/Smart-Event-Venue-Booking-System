from flask import Flask, render_template, request
import face_recognition
import os
from cryptography.fernet import Fernet

app = Flask(__name__)

# Load known face
known_image = face_recognition.load_image_file("faces/user1.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]

# Generate encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        file = request.files['face']
        unknown_image = face_recognition.load_image_file(file)
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

        result = face_recognition.compare_faces(
            [known_encoding], unknown_encoding
        )

        if result[0]:
            return "Face Verified! Access Granted ✅"
        else:
            return "Face Not Matched ❌"

    return render_template('login.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    data = file.read()
    encrypted = cipher.encrypt(data)

    with open("encrypted_files/" + file.filename, 'wb') as f:
        f.write(encrypted)

    return "File Encrypted & Stored Securely 🔐"

if __name__ == '__main__':
    app.run(debug=True)

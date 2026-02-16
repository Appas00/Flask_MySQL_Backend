import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()  # Local .env for development; Railway injects automatically in production

# -----------------------------
# Import database configuration
# -----------------------------
from db_config import db_config

# -----------------------------
# Initialize Flask app
# -----------------------------
app = Flask(__name__)

# Allow requests from GitHub Pages frontend
CORS(app, origins=[
    "https://appas00.github.io",
    "https://appas00.github.io/portfolio"
])

# -----------------------------
# Gmail credentials
# -----------------------------
GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# -----------------------------
# Root route
# -----------------------------
@app.get("/")
def home():
    return jsonify({"status": "ok", "message": "Backend is running on Railway!"})

# -----------------------------
# Contact form route
# -----------------------------
@app.post("/contact")
def contact():
    try:
        data = request.json or {}  # Safe fallback if request body is empty

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        message_body = data.get("message")

        # Validate required fields
        if not name or not email or not message_body:
            return jsonify({
                "status": "error",
                "message": "Name, Email, and Message are required."
            }), 400

        # -----------------------------
        # Save to MySQL
        # -----------------------------
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO contacts (name, email, phone, message)
                VALUES (%s, %s, %s, %s)
            """, (name, email, phone, message_body))

            conn.commit()
            cursor.close()
            conn.close()

        except Error as e:
            return jsonify({
                "status": "error",
                "message": f"MySQL Error: {str(e)}"
            }), 500

        # -----------------------------
        # Send Gmail notification
        # -----------------------------
        try:
            msg = EmailMessage()
            msg["Subject"] = f"Portfolio Contact Message from {name}"
            msg["From"] = GMAIL_USERNAME
            msg["To"] = GMAIL_USERNAME
            msg.set_content(
                f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message_body}"
            )

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
                server.send_message(msg)

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Email Error: {str(e)}"
            }), 500

        # -----------------------------
        # Success response
        # -----------------------------
        return jsonify({"status": "success", "message": "Message sent successfully!"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500

# -----------------------------
# Local development
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

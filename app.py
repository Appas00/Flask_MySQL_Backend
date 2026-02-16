from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()
from db_config import db_config

app = Flask(__name__)

# Allow frontend (React) - You can add Clever Cloud domain later
CORS(app, origins=["http://localhost:5174"])

# Gmail Credentials
GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# --------------------------------------------------------
# Test Route
# --------------------------------------------------------
@app.get("/")
def home():
    return jsonify({"status": "ok", "message": "Backend is running!"})

# --------------------------------------------------------
# Contact Form Route
# --------------------------------------------------------
@app.post("/contact")
def contact():
    try:
        data = request.json

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        message_body = data.get("message")

        if not name or not email or not message_body:
            return jsonify({"status": "error", "message": "Name, Email, and Message are required"}), 400

        # --------------------------------------------------------
        # Save to MySQL (Clever Cloud)
        # --------------------------------------------------------
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

        # --------------------------------------------------------
        # Send Gmail Email
        # --------------------------------------------------------
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

        return jsonify({"status": "success", "message": "Message sent!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --------------------------------------------------------
# Run Flask
# --------------------------------------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)

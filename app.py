from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

# Load .env (Railway injects automatically)
load_dotenv()

# Import DB config
from db_config import db_config

app = Flask(__name__)

# CORS for your GitHub Pages portfolio
CORS(app, origins=[
    "https://appas00.github.io",
    "https://appas00.github.io/portfolio",
    "https://appas00.github.io/portfolio/"
])

GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


@app.get("/")
def home():
    return jsonify({"status": "ok", "message": "Backend running"})


@app.post("/contact")
def contact():
    try:
        data = request.json

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        message_body = data.get("message")

        if not name or not email or not message_body:
            return jsonify({"status": "error", "message": "Required fields missing"}), 400

        # Store in MySQL
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
            return jsonify({"status": "error", "message": f"MySQL Error: {str(e)}"}), 500

        # Send Gmail notification
        try:
            msg = EmailMessage()
            msg["Subject"] = f"Portfolio Contact from {name}"
            msg["From"] = GMAIL_USERNAME
            msg["To"] = GMAIL_USERNAME

            msg.set_content(
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Phone: {phone}\n"
                f"\nMessage:\n{message_body}"
            )

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
                server.send_message(msg)

        except Exception as e:
            return jsonify({"status": "error", "message": f"Email Error: {str(e)}"}), 500

        return jsonify({"status": "success", "message": "Message sent successfully!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

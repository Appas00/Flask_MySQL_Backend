from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# -------------------------------
# ✅ ENABLE CORS FOR YOUR GITHUB
# -------------------------------
# In app.py, update CORS to allow your GitHub Pages domain
CORS(app, origins=[
    "https://appas00.github.io",
    "https://appas00.github.io/portfolio",
    "http://localhost:3000",  # For local development
    "http://127.0.0.1:3000"
], supports_credentials=True)


# -------------------------------
# ✅ DATABASE CONFIG (Railway)
# -------------------------------
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="YOUR_RAILWAY_HOST",
            user="YOUR_RAILWAY_USER",
            password="YOUR_RAILWAY_PASSWORD",
            database="YOUR_RAILWAY_DATABASE",
            port=3306
        )
    except Error as e:
        print("❌ Database connection failed:", e)
        return None


# -------------------------------
# ✅ CONTACT ROUTE
# -------------------------------
@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    message = data.get("message")
    phone = data.get("phone", "")

    if not name or not email or not message:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "DB connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contacts (name, email, phone, message)
            VALUES (%s, %s, %s, %s)
        """, (name, email, phone, message))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Message saved successfully"}), 200

    except Exception as e:
        print("❌ ERROR inserting:", e)
        return jsonify({"success": False, "error": "Internal Server Error"}), 500


# -------------------------------
# ✅ ROOT TEST ROUTE
# -------------------------------
@app.route("/")
def home():
    return jsonify({"status": "Backend is running!"})


# -------------------------------
# ✅ MAIN
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

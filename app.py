from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from db_config import db_config

app = Flask(__name__)

# Allow GitHub Pages (your frontend)
CORS(app, origins=["https://appas00.github.io", "https://appas00.github.io/portfolio"])

# ----------------------------------------------------
# Test Route
# ----------------------------------------------------
@app.get("/")
def home():
    return jsonify({"status": "ok", "message": "Backend running on Railway!"})

# ----------------------------------------------------
# Contact Form Route
# ----------------------------------------------------
@app.post("/contact")
def contact():
    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        message = data.get("message")

        if not name or not email or not message:
            return jsonify({"error": "Name, Email, and Message are required"}), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO contacts (name, email, phone, message)
            VALUES (%s, %s, %s, %s)
        """, (name, email, phone, message))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Message saved successfully!"})

    except Error as e:
        return jsonify({"error": f"MySQL Error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# Start Flask (Railway uses Gunicorn in production)
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

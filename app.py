from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from db_config import db_config

app = Flask(__name__)
CORS(app)

def get_connection():
    return mysql.connector.connect(**db_config)

@app.route("/")
def home():
    return jsonify({"status": "API working successfully!"})

@app.route("/contact", methods=["POST"])
def save_contact():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    message = data.get("message")

    if not name or not email or not message:
        return jsonify({"error": "Name, email & message are required"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO contacts (name, email, phone, message)
            VALUES (%s, %s, %s, %s)
        """, (name, email, phone, message))

        conn.commit()

        return jsonify({"success": True, "message": "Successfully saved!"})

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

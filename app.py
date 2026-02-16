app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# -------------------------------
# ✅ ENABLE CORS FOR YOUR GITHUB
# -------------------------------
CORS(app, origins=[
    "https://appas00.github.io",
    "https://appas00.github.io/portfolio",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
])


# -------------------------------
# ✅ DATABASE CONFIG (Railway)
# -------------------------------
def get_db_connection():
    try:
        # Get database config from environment variables
        config = {
            "host": os.getenv("MYSQLHOST", "mysql.railway.internal"),
            "user": os.getenv("MYSQLUSER", "root"),
            "password": os.getenv("MYSQLPASSWORD", ""),
            "database": os.getenv("MYSQLDATABASE", "railway"),
            "port": int(os.getenv("MYSQLPORT", 3306))
        }
        
        print(f"🔌 Connecting to MySQL at {config['host']}:{config['port']}")
        
        return mysql.connector.connect(**config)
    except Error as e:
        print("❌ Database connection failed:", e)
        return None


# -------------------------------
# ✅ CONTACT ROUTE
# -------------------------------
@app.route("/contact", methods=["POST", "OPTIONS"])
def contact():
    # Handle preflight requests
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        data = request.get_json()
        print("📨 Received contact form data:", data)

        name = data.get("name")
        email = data.get("email")
        message = data.get("message")
        phone = data.get("phone", "")

        if not name or not email or not message:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "error": "Database connection failed"}), 500

        try:
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    phone VARCHAR(50),
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                INSERT INTO contacts (name, email, phone, message)
                VALUES (%s, %s, %s, %s)
            """, (name, email, phone, message))

            conn.commit()
            cursor.close()
            conn.close()

            print("✅ Message saved successfully")
            return jsonify({"success": True, "message": "Message saved successfully"}), 200

        except Exception as e:
            print("❌ ERROR inserting:", e)
            return jsonify({"success": False, "error": str(e)}), 500

    except Exception as e:
        print("❌ ERROR in contact route:", e)
        return jsonify({"success": False, "error": "Internal Server Error"}), 500


# -------------------------------
# ✅ HEALTH CHECK ROUTE
# -------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Backend is running!",
        "message": "Flask MySQL API is active",
        "endpoints": {
            "GET /": "This message",
            "POST /contact": "Submit contact form"
        }
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "timestamp": __import__('datetime').datetime.now().isoformat()})


# -------------------------------
# ✅ MAIN
# -------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

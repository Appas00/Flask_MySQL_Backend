import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import logging
import time
from datetime import datetime

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# Configure logging
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -----------------------------
# Database configuration - Support both Railway and Clever-Cloud
# -----------------------------
# Railway provides MySQL variables with different names
db_config = {
    'host': os.getenv('DB_HOST') or os.getenv('MYSQLHOST') or 'bmqdodlsvrs4eiohpyuj-mysql.services.clever-cloud.com',
    'database': os.getenv('DB_NAME') or os.getenv('MYSQLDATABASE') or 'bmqdodlsvrs4eiohpyuj',
    'user': os.getenv('DB_USER') or os.getenv('MYSQLUSER') or 'u3n1wy3bh5dbph7h',
    'password': os.getenv('DB_PASS') or os.getenv('MYSQLPASSWORD') or '7hsxNRqBlgV9IalgyIgw',
    'port': int(os.getenv('DB_PORT') or os.getenv('MYSQLPORT') or 3306),
    'connection_timeout': 30,
    'use_pure': True
}

# -----------------------------
# Gmail credentials
# -----------------------------
GMAIL_USERNAME = os.getenv("GMAIL_USERNAME", "appasm321@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "byuabzoldtygwznm")

# -----------------------------
# Initialize Flask app
# -----------------------------
app = Flask(__name__)

# -----------------------------
# Comprehensive CORS configuration
# -----------------------------
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://appas00.github.io",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://flask-mysql-backend.up.railway.app"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"],
        "supports_credentials": True
    }
})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://appas00.github.io')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# -----------------------------
# Database connection helper with better error handling
# -----------------------------
def get_db_connection():
    """Get database connection with retry logic"""
    retries = 3
    last_error = None
    
    for i in range(retries):
        try:
            logger.info(f"Connecting to MySQL ({i+1}/{retries}) - Host: {db_config['host']}, DB: {db_config['database']}")
            conn = mysql.connector.connect(**db_config)
            if conn.is_connected():
                logger.info("✅ Connected to MySQL successfully!")
                return conn
        except Error as e:
            last_error = e
            logger.error(f"❌ Connection attempt {i+1} failed: {str(e)}")
            if i < retries - 1:
                time.sleep(2)
    
    logger.error(f"❌ All connection attempts failed: {last_error}")
    return None

# -----------------------------
# Initialize database and check table
# -----------------------------
def init_database():
    """Check if contacts table exists and has correct structure"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Check if contacts table exists
            cursor.execute("SHOW TABLES LIKE 'contacts'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                logger.info("✅ Contacts table exists")
                
                # Show table structure
                cursor.execute("DESCRIBE contacts")
                columns = cursor.fetchall()
                logger.info("Table structure:")
                for col in columns:
                    logger.info(f"  - {col[0]} {col[1]}")
                
                # Count records
                cursor.execute("SELECT COUNT(*) FROM contacts")
                count = cursor.fetchone()[0]
                logger.info(f"📊 Total records in contacts table: {count}")
            else:
                logger.warning("❌ Contacts table does not exist, creating...")
                # Create the table if it doesn't exist
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
                conn.commit()
                logger.info("✅ Contacts table created successfully!")
            
            cursor.close()
            conn.close()
            return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        return False

# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Backend is running on Railway with MySQL!",
        "timestamp": datetime.now().isoformat(),
        "database": db_config['host']
    })

@app.get("/health")
def health_check():
    """Health check endpoint"""
    db_status = "ok"
    db_message = ""
    record_count = 0
    
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            record_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            db_message = f"Connected, {record_count} records"
        else:
            db_status = "error"
            db_message = "Could not connect to database"
    except Exception as e:
        db_status = "error"
        db_message = str(e)
        logger.error(f"Health check error: {str(e)}")
    
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "database": {
            "status": db_status,
            "message": db_message,
            "records": record_count
        },
        "services": {
            "gmail": "configured" if GMAIL_USERNAME and GMAIL_APP_PASSWORD else "not configured"
        }
    })

@app.get("/test-db")
def test_db():
    """Test database connection and show data"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "status": "error",
                "message": "Could not connect to database"
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        # Get contacts data
        cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC LIMIT 10")
        contacts = cursor.fetchall()
        
        # Convert datetime objects to strings
        for contact in contacts:
            if 'created_at' in contact:
                contact['created_at'] = contact['created_at'].isoformat() if contact['created_at'] else None
        
        cursor.close()
        conn.close()
        
        # Format table names
        table_list = []
        for table in tables:
            for value in table.values():
                table_list.append(value)
        
        return jsonify({
            "status": "success",
            "message": "✅ Connected to MySQL",
            "database_info": {
                "host": db_config['host'],
                "database": db_config['database'],
                "user": db_config['user']
            },
            "tables": table_list,
            "recent_contacts": contacts,
            "total_contacts": len(contacts)
        })
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }), 500

@app.post("/contact")
def contact():
    """Handle contact form submissions"""
    logger.info("📨 Received contact form submission")
    
    try:
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400

        logger.info(f"Form data: {data}")

        # Extract and validate fields
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        phone = data.get("phone", "").strip()
        message_body = data.get("message", "").strip()

        if not name:
            return jsonify({"status": "error", "message": "Name is required"}), 400
        if not email:
            return jsonify({"status": "error", "message": "Email is required"}), 400
        if "@" not in email or "." not in email:
            return jsonify({"status": "error", "message": "Valid email is required"}), 400
        if not message_body:
            return jsonify({"status": "error", "message": "Message is required"}), 400

        # Save to database
        insert_id = None
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({
                    "status": "error",
                    "message": "Database connection failed - please try again later"
                }), 503

            cursor = conn.cursor()

            # Insert the data
            cursor.execute("""
                INSERT INTO contacts (name, email, phone, message)
                VALUES (%s, %s, %s, %s)
            """, (name, email, phone, message_body))

            conn.commit()
            insert_id = cursor.lastrowid
            logger.info(f"✅ Message saved with ID: {insert_id}")
            
            cursor.close()
            conn.close()

        except Error as e:
            logger.error(f"MySQL Error: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Database error occurred. Please try again."
            }), 500

        # Send email notification (optional - don't fail if email doesn't work)
        email_sent = False
        if GMAIL_USERNAME and GMAIL_APP_PASSWORD:
            try:
                msg = EmailMessage()
                msg["Subject"] = f"Portfolio Contact: {name}"
                msg["From"] = GMAIL_USERNAME
                msg["To"] = GMAIL_USERNAME
                msg.set_content(
                    f"New message from your portfolio!\n\n"
                    f"Name: {name}\n"
                    f"Email: {email}\n"
                    f"Phone: {phone}\n\n"
                    f"Message:\n{message_body}\n\n"
                    f"---\n"
                    f"ID: {insert_id}\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )

                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
                    server.send_message(msg)
                
                email_sent = True
                logger.info(f"✅ Email notification sent")
            except Exception as e:
                logger.error(f"Email Error: {str(e)}")
                # Don't fail the request if email fails

        return jsonify({
            "status": "success",
            "message": "Message sent successfully!",
            "data": {
                "id": insert_id,
                "name": name,
                "email": email,
                "timestamp": datetime.now().isoformat(),
                "email_notification": email_sent
            }
        })

    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred. Please try again."
        }), 500

@app.route('/contact', methods=['OPTIONS'])
def handle_options():
    return '', 200

# -----------------------------
# Initialize on startup
# -----------------------------
with app.app_context():
    init_database()
    logger.info("✅ Application started successfully")

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

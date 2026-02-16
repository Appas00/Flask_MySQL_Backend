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
from datetime datetime
import urllib.parse

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# Configure logging
# -----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -----------------------------
# Database configuration - Using Railway MySQL Reference
# -----------------------------
def get_db_config():
    """Parse database config from Railway MySQL URL"""
    
    # Railway provides MYSQL_URL in format: mysql://user:password@host:port/database
    database_url = os.getenv('DATABASE_URL') or os.getenv('MYSQL_URL')
    
    if database_url and database_url.startswith('mysql://'):
        # Parse MySQL URL
        parsed = urllib.parse.urlparse(database_url)
        
        db_config = {
            'host': parsed.hostname,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path[1:],  # Remove leading '/'
            'port': parsed.port or 3306,
            'connection_timeout': 30,
            'use_pure': True
        }
        logger.info(f"✅ Using Railway MySQL: {db_config['host']}/{db_config['database']}")
        return db_config
    else:
        # Fallback to individual variables (for local development)
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'railway'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASS', ''),
            'port': int(os.getenv('DB_PORT', 3306)),
            'connection_timeout': 30,
            'use_pure': True
        }
        logger.info(f"✅ Using local/individual DB config: {db_config['host']}/{db_config['database']}")
        return db_config

# Get database config
db_config = get_db_config()

# -----------------------------
# Gmail credentials
# -----------------------------
GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# -----------------------------
# Initialize Flask app
# -----------------------------
app = Flask(__name__)

# -----------------------------
# CORS configuration
# -----------------------------
CORS(app, origins=[
    "https://appas00.github.io",
    "https://appas00.github.io/portfolio"
])


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# -----------------------------
# Database connection helper
# -----------------------------
def get_db_connection():
    """Get database connection with retry logic"""
    retries = 3
    for i in range(retries):
        try:
            logger.info(f"Connecting to MySQL ({i+1}/{retries})...")
            conn = mysql.connector.connect(**db_config)
            if conn.is_connected():
                logger.info("✅ Connected to MySQL successfully!")
                return conn
        except Error as e:
            logger.error(f"❌ Connection attempt {i+1} failed: {str(e)}")
            if i == retries - 1:
                raise e
            time.sleep(2)
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
        "timestamp": datetime.now().isoformat()
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
                "database": db_config['database']
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
                    "message": "Database connection failed"
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

        # Send email notification
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

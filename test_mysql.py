from db_config import db_config
import mysql.connector

try:
    print("Loaded config:", db_config)
    conn = mysql.connector.connect(**db_config)
    print("✅ MySQL Connected Successfully!")
    conn.close()
except Exception as e:
    print("❌ MySQL Connection Failed:", e)

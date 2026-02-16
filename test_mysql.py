from db_config import db_config
import mysql.connector

try:
    conn = mysql.connector.connect(**db_config)
    print("✅ Connection successful")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)

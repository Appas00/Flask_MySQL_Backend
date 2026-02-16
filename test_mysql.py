import mysql.connector
from db_config import db_config

try:
    conn = mysql.connector.connect(**db_config)
    print("✅ Connected to Clever-Cloud MySQL!")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)

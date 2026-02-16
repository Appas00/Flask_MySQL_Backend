db_config.py
import os
from dotenv import load_dotenv

load_dotenv()

db_config = {
    "host": os.getenv("MYSQLHOST", "mysql.railway.internal"),
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", ""),
    "database": os.getenv("MYSQLDATABASE", "railway"),
    "port": int(os.getenv("MYSQLPORT", 3306))
}

print("📋 Database config loaded:")
print(f"  Host: {db_config['host']}")
print(f"  Database: {db_config['database']}")
print(f"  User: {db_config['user']}")

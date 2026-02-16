import os
from dotenv import load_dotenv

# Load .env locally (Railway uses real environment variables)
load_dotenv()

db_config = {
    "host": os.getenv("MYSQLHOST", "mysql.railway.internal"),
    "port": int(os.getenv("MYSQLPORT", 3306)),
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", ""),
    "database": os.getenv("MYSQLDATABASE", "railway"),
}

# Debug print to verify
print("DB Config Loaded:", db_config)

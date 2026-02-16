import os
from dotenv import load_dotenv

# Load .env file locally
load_dotenv()

db_config = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_NAME")
}

# Debug print
print("DB Config Loaded:", db_config)

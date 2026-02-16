import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration for Clever-Cloud MySQL
db_config = {
    'host': os.getenv('DB_HOST', 'bmqdodlsvrs4eiohpyuj-mysql.services.clever-cloud.com'),
    'database': os.getenv('DB_NAME', 'bmqdodlsvrs4eiohpyuj'),
    'user': os.getenv('DB_USER', 'u3n1wy3bh5dbph7h'),
    'password': os.getenv('DB_PASS', '7hsxNRqBlgV9IalgyIgw'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'connection_timeout': 30,
    'use_pure': True
}

print(f"✅ Database config loaded for {db_config['host']}")

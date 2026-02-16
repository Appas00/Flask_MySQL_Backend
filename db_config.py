# db_config.py
import os

db_config = {
    "host": os.getenv("DB_HOST", "mysql-3f297111-appasm321-e8a6.k.aivencloud.com"),
    "user": os.getenv("DB_USER", "avnadmin"),
    "password": os.getenv("DB_PASSWORD", "AVNS_FLKQh4Rgnsk6jfp1fxG"),
    "database": os.getenv("DB_NAME", "defaultdb"),
    "port": int(os.getenv("DB_PORT", 15298)),
    "ssl_ca": "/path/to/ca.pem",  # Aiven provides a CA certificate file
}

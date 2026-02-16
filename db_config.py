import os

db_config = {
    "host": os.getenv("DB_HOST", "mysql.railway.internal"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "lYbgLpYGrcWPUsVWRwPnGswYFsieywmC"),
    "database": os.getenv("DB_NAME", "railway")
}

# Optional debug
print("DB Config Loaded:", db_config)

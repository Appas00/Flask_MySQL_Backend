import os

db_config = {
    "host": os.getenv("MYSQLHOST"),              # mysql.railway.internal
    "user": os.getenv("MYSQLUSER"),              # root
    "password": os.getenv("MYSQLPASSWORD"),      # MYSQL_ROOT_PASSWORD
    "database": os.getenv("MYSQLDATABASE"),      # railway
    "port": int(os.getenv("MYSQLPORT", 3306))    # 3306
}

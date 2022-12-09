from backend_db_lib.models import base
from backend_db_lib.manager import DatabaseManager

DATABASE_URL = "postgresql://backendgang:backendgang@db:8010/backend"

dbm = DatabaseManager(base, DATABASE_URL)
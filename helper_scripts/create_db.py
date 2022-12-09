from backend_db_lib.manager import DatabaseManager
from backend_db_lib.models import base

DATABASE_URL = "postgresql://backendgang:backendgang@127.0.0.1:8010/backend"

db = DatabaseManager(base, DATABASE_URL)
db.drop_all()
db.create_all()
db.create_initial_data()
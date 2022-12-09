import uvicorn
from fastapi import FastAPI, Header

from backend_db_lib.models import base, LPAAudit
from backend_db_lib.manager import DatabaseManager

DATABASE_URL = "postgresql://backendgang:backendgang@db:8010/backend"

dbm = DatabaseManager(base, DATABASE_URL)
app = FastAPI()

@app.get("/healthcheck")
def healthcheck():
    return { "Status": "Up" }

@app.get("/audit")
def get_audits(authorization: str | None = Header(default=None)):
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
import os

class Settings:
    AUDIT_API_URL: str = None
    DB_USER: str = None
    DB_PASSWORD: str = None
    DB_NAME: str = None
    DB_HOSTNAME: str = None
    DB_PORT: str = None



settings = Settings()
settings.DB_USER = os.environ["DB_USER"]
settings.DB_PASSWORD = os.environ["DB_PASSWORD"]
settings.DB_NAME = os.environ["DB_NAME"]
settings.DB_HOSTNAME = os.environ["DB_HOSTNAME"]
settings.DB_PORT = os.environ["DB_PORT"]

settings.AUDIT_API_URL="http://localhost:8000"
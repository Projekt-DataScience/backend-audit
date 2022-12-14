import os

class Settings:
    AUDIT_API_URL: str = None
    DB_USER: str = None
    DB_PASSWORD: str = None
    DB_NAME: str = None
    DB_HOSTNAME: str = None
    DB_PORT: str = None
    TEST_DATABASE: str = None



settings = Settings()
settings.DB_USER = os.environ.get("DB_USER")
settings.DB_PASSWORD = os.environ.get("DB_PASSWORD")
settings.DB_NAME = os.environ.get("DB_NAME")
settings.DB_HOSTNAME = os.environ.get("DB_HOSTNAME")
settings.DB_PORT = os.environ.get("DB_PORT")
settings.TEST_DATABASE = os.environ.get("TEST_DATABASE")

if settings.DB_USER is None and settings.TEST_DATABASE is None:
    settings.TEST_DATABASE = "sqlite:///test.db"

settings.AUDIT_API_URL="http://localhost:8000"
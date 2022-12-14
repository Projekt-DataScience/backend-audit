import os
import requests

from backend_db_lib.models import User


def get_user(session, id: int):
    HOSTNAME = os.environ.get("USER_MANAGEMENT_SERVICE_HOSTNAME")
    PORT = os.environ.get("USER_MANAGEMENT_SERVICE_PORT")
    PATH = f"/api/user_management/user/{id}"

    URL = f"http://{HOSTNAME}:{PORT}{PATH}"
    response = requests.get(URL)
    if response.status_code != 200:
        user = session.query(User).get(id)
        user.password_hash = ""
    else:
        user = response.json()["data"]

    print(user)
    return user

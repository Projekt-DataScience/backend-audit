import os
import requests

from fastapi import HTTPException, status

from backend_db_lib.models import User

HOSTNAME = os.environ.get("USER_MANAGEMENT_SERVICE_HOSTNAME")
PORT = os.environ.get("USER_MANAGEMENT_SERVICE_PORT")

def generate_url(path: str):
    return f"http://{HOSTNAME}:{PORT}{path}"

def validate_jwt(jwt: str):
    jwt = jwt.replace("Bearer ", "")
    PATH = "/api/user_management/validateJWT/?jwt=" + jwt
    URL = generate_url(PATH)
    print(URL)

    response = requests.post(URL)

    if response.status_code == 200:
        return response.json()["payload"]
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT") 


def validate_authorization(authorization: str):
    if authorization is None:
        raise HTTPException(
            status_code=401, detail="Authorization header not found")

    return validate_jwt(authorization)


def get_user(session, id: int):
    PATH = f"/api/user_management/user/{id}"

    URL = generate_url(PATH)
    response = requests.get(URL)
    if response.status_code != 200:
        user = session.query(User).get(id)
        user.password_hash = ""
    else:
        user = response.json()["data"]

    print(user)
    return user


def get_group(id: int, token: str):
    PATH = f"/api/user_management/group/{id}"

    URL = generate_url(PATH)
    response = requests.get(URL, headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        return None
    else:
        return response.json()["data"][0]["group"]


def get_layer(id: int, token: str):
    PATH = f"/api/user_management/layers/"

    URL = generate_url(PATH)
    response = requests.get(URL, headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        return None
    else:
        for layer in response.json()["data"]:
            if layer["id"] == id:
                return layer
    return None

def login():
    """
    Function should only be used for tests

    :param client: FastAPI test client
    :returns: JWT Token as string
    """
    PATH = "/api/user_management/login/"
    URL = generate_url(PATH)
    credentials = {
        "email": "josef@test.de",
        "password": "test"
    }
    print("login url", URL)

    response = requests.post(URL, json=credentials)
    print("login response", response.json())

    return response.json().get("token")

from httpx import Response
from test.utils import *
from dependencies import get_current_user, get_db
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response: Response = client.get("/user/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "awesome"


def test_change_password_success(test_user):
    response: Response = client.put(
        "/user/change_password", json={"password": "1234567", "new_password": "7654321"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid(test_user):
    response: Response = client.put(
        "/user/change_password",
        json={"password": "wrongpassword", "new_password": "7654321"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Wrong password"}

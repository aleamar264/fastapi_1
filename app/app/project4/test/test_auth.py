from test.utils import *
from routers.auth import authenticated_user
from dependencies import get_db, get_current_user, SECRET_KEY, ALGORITHM
from jose import jwt
import pytest
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db


def test_authenthicated_user(test_user):
    db = TestingSessionLocal()
    authenticate_user = authenticated_user(test_user.username, "1234567", db)
    assert authenticate_user is not None
    assert authenticate_user.username == test_user.username

    non_existing_user = authenticated_user("Wronguser", "1234567", db)
    assert non_existing_user is False


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {"sub": "testuser", "id": 1, "role": "admin"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {"username": "testuser", "id": 1, "user_role": "admin"}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {"role": "user"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=token)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate user."

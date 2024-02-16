from http import client

from httpx import Response
from dependencies import get_db, get_current_user
from sqlalchemy import select
from test.utils import *
from schemas import TodoRequest
from models import Todos
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo: Todos):
    response: Response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "complete": False,
            "description": "Need to learn everyday!",
            "id": 1,
            "owner_id": 1,
            "title": "Learn to code",
            "priority": 5,
        }
    ]


def test_read_one_authenticated(test_todo: Todos):
    response: Response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "priority": 5,
        "id": 1,
        "owner_id": 1,
        "description": "Need to learn everyday!",
        "complete": False,
        "title": "Learn to code",
    }


def test_read_one_authenticated_not_found(test_todo: Todos):
    response: Response = client.get("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}


def test_create_todo(test_todo: Todos):
    request_data = TodoRequest(
        title="New Todo!",
        description="New todo description",
        priority=1,
        complete=False,
    )
    response: Response = client.post("/todo/", json=request_data.model_dump())
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    stmt = select(Todos).filter(Todos.id == 2)
    model = db.execute(stmt).scalar_one()
    assert model.title == request_data.title
    assert model.description == request_data.description


def test_update_todo(test_todo: Todos):
    request_data = TodoRequest(
        title="Changed title",
        description="New description",
        priority=5,
        complete=False,
    )
    response: Response = client.put("/todo/1", json=request_data.model_dump())
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    stmt = select(Todos).filter(Todos.id == 1)
    model = db.execute(stmt).scalar_one()
    assert model.title == request_data.title
    assert model.description == request_data.description


def test_update_todo_not_found():
    request_data = TodoRequest(
        title="Changed title",
        description="New description",
        priority=5,
        complete=False,
    )
    response: Response = client.put("/todo/99", json=request_data.model_dump())
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}


def test_delete_todo(test_todo: Todos):
    response: Response = client.delete("/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    stmt = select(Todos).filter(Todos.id == 1)
    model = db.execute(stmt).scalar_one_or_none()
    assert model is None


def test_delete_todo_not_found():
    response: Response = client.delete("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}

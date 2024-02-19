from httpx import Response
from fastapi import status
from sqlalchemy import select
from test.utils import *
from dependencies import get_current_user, get_db

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all_authenticated(test_todo):
    response: Response = client.get("/admin/todo")
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


def test_admin_delete_todos(test_todo):
    response: Response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    stmt = select(Todos).filter(Todos.id == 1)
    result = db.execute(stmt).scalar_one_or_none()
    assert result is None


def test_admin_delete_not_found_todos(test_todo):
    response: Response = client.delete("/admin/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}

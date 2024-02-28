from typing import Sequence
from dependencies import db_dependency, user_dependency
from fastapi import APIRouter, HTTPException, Path
from models import Todos
from schemas import TodoRequest, TodoResponse
from starlette import status
from sqlalchemy import delete, select, update

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency) -> Sequence[TodoResponse]:
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    model = select(Todos)
    return db.execute(model).scalars().all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed")
    stmt = select(Todos).filter(Todos.id == todo_id)
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    stmt = delete(Todos).where(Todos.id == todo_id)
    db.execute(stmt)
    db.commit()

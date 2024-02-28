from typing import Sequence
from dependencies import db_dependency, user_dependency
from fastapi import APIRouter, HTTPException, Path
from models import Todos
from schemas import TodoRequest, TodoResponse
from starlette import status
from sqlalchemy import delete, select, update

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency) -> Sequence[TodoResponse]:
    model = select(Todos).filter(Todos.owner_id == user.get("id"))
    return db.execute(model).scalars().all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
) -> TodoResponse:
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    stmt = (
        select(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
    )
    todo_model = db.execute(stmt).scalar_one_or_none()
    if todo_model is not None:
        return TodoResponse(**todo_model.__dict__)
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, body: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = Todos(**body.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    body: TodoRequest,
    todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    stmt = (
        select(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
    )
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    stmt = update(Todos).filter(Todos.id == todo_id).values(**body.model_dump())
    db.execute(stmt)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    stmt = (
        select(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
    )
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    stmt = (
        delete(Todos)
        .where(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
    )
    db.execute(stmt)
    db.commit()

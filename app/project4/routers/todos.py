import sys

sys.path.append("...")
from typing import Sequence, Annotated
from dependencies import db_dependency, user_dependency
from fastapi import APIRouter, HTTPException, Path, Request, Form
from fastapi.responses import RedirectResponse
from models import Todos
from schemas import TodoRequest, TodoResponse
from starlette import status
from sqlalchemy import delete, select, update

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/todos", tags=["todos"], responses={404: {"description": "Not found"}}
)

templates = Jinja2Templates(directory="templates")

str_form = Annotated[str, Form(...)]


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: db_dependency):
    stmt = select(Todos).filter(Todos.owner_id == 1)
    todos = db.execute(stmt).scalars().all()
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})


@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    db: db_dependency,
    title: str_form,
    description: str_form,
    priority: Annotated[int, Form(...)],
):
    todo_model = Todos(
        title=title,
        description=description,
        priority=priority,
        complete=False,
        owner_id=1,
    )
    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: db_dependency):
    stmt = select(Todos).filter(Todos.id == todo_id)
    result = db.execute(stmt).scalar_one_or_none()
    return templates.TemplateResponse(
        "edit-todo.html", {"request": request, "todo": result}
    )


@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(
    request: Request,
    todo_id: int,
    db: db_dependency,
    title: str_form,
    description: str_form,
    priority: Annotated[int, Form(...)],
):
    stmt = (
        update(Todos)
        .filter(Todos.id == todo_id)
        .values(
            title=title,
            description=description,
            priority=priority,
        )
    )
    db.execute(stmt)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: db_dependency):
    stmt = select(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == 1)
    if (result := db.execute(stmt).scalar_one_or_none()) is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    stmt = delete(Todos).filter(Todos.id == todo_id)
    db.execute(stmt)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: db_dependency):
    stmt = select(Todos).filter(Todos.id == todo_id)
    if (result := db.execute(stmt).scalar_one_or_none()) is None:
        return RedirectResponse(url="/not-found", status_code=status.HTTP_404_NOT_FOUND)
    result.complete = not result.complete
    db.add(result)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

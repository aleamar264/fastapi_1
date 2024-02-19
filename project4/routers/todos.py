import sys

sys.path.append("...")
from typing import Annotated
from dependencies import db_dependency, get_current_user
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from models import Todos
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
    if (user := await get_current_user(request)) is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    stmt = select(Todos).filter(Todos.owner_id == user.get("id"))
    todos = db.execute(stmt).scalars().all()
    return templates.TemplateResponse(
        "home.html", {"request": request, "todos": todos, "user": user}
    )


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    if (user := await get_current_user(request)) is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "add-todo.html", {"request": request, "user": user}
    )


@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    db: db_dependency,
    title: str_form,
    description: str_form,
    priority: Annotated[int, Form(...)],
):
    if (user := await get_current_user(request)) is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = Todos(
        title=title,
        description=description,
        priority=priority,
        complete=False,
        owner_id=user.get("id"),
    )
    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: db_dependency):
    if (user := await get_current_user(request)) is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    stmt = select(Todos).filter(Todos.id == todo_id)
    result = db.execute(stmt).scalar_one_or_none()
    return templates.TemplateResponse(
        "edit-todo.html", {"request": request, "todo": result, "user": user}
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
    if (user := await get_current_user(request)) is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    stmt = (
        select(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
    )
    if (result := db.execute(stmt).scalar_one_or_none()) is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    stmt = delete(Todos).filter(Todos.id == todo_id)
    db.execute(stmt)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: db_dependency):
    if (user := await get_current_user(request)) is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    stmt = select(Todos).filter(Todos.id == todo_id)
    if (result := db.execute(stmt).scalar_one_or_none()) is None:
        return RedirectResponse(url="/not-found", status_code=status.HTTP_404_NOT_FOUND)
    result.complete = not result.complete
    db.add(result)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

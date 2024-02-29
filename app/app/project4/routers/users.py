from re import template
import sys
from typing import Annotated

from sqlalchemy import select, update

sys.path.append("..")

from fastapi import status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import Depends, APIRouter, Request, Form
import models
from database import engine, session_
from sqlalchemy.orm import Session
from pydantic import BaseModel
from dependencies import get_current_user, db_dependency
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

router = APIRouter(
    prefix="/users", tags=["users"], responses={404: {"description": "Not Found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")
STR_FORM = Annotated[str, Form(...)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str


@router.get("/edit-password", response_class=HTMLResponse)
async def edit_user_view(request: Request):
    if (user := await get_current_user(request)) is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "edit-user-password.html",
        {"request": request, "user": user},
    )


@router.post("/edit-password", response_class=HTMLResponse)
async def user_password_change(
    request: Request,
    username: STR_FORM,
    password: STR_FORM,
    password2: STR_FORM,
    db: db_dependency,
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    stmt = select(models.Users).filter(models.Users.username == username)
    msg = "Invalid username or password"
    if (user_data := db.execute(stmt).scalar_one_or_none()) is not None:
        if username == user_data.username and bcrypt_context.verify(
            password, user_data.hashed_password
        ):
            password_ = {"hashed_password": bcrypt_context.hash(password2)}
            stmt = (
                update(models.Users)
                .where(models.Users.username == username)
                .values(**password_)
            )
            db.execute(stmt)
            db.commit()
            msg = "Password updated"
    return templates.TemplateResponse(
        "edit-user-password.html", {"request": request, "user": user, "msg": msg}
    )

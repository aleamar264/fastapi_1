from datetime import timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Form, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from models import Users
from passlib.context import CryptContext
from schemas import CreateUserRequest
from starlette import status
from schemas import UserModel
from sqlalchemy import select
from dependencies import db_dependency, form_data, create_access_token
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/auth", tags=["auth"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
STR_FORM = Annotated[str, Form(...)]


def authenticated_user(username: str, password: str, db) -> UserModel | bool:
    stmt = select(Users).filter(Users.username == username)
    user = db.execute(stmt).scalar_one_or_none()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


class LoginForm:
    def __init__(self, request: Request) -> None:
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


@router.post("/token")
async def login_for_access_token(
    response: Response, form: form_data, db: db_dependency
):
    user = authenticated_user(form.username, form.password, db)
    if not user:
        return False
    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=60)
    )
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True


@router.get("/", response_class=HTMLResponse)
async def authpapge(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: db_dependency):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(
            response=response, form=form, db=db
        )
        if not validate_user_cookie:
            msg = "Incorrect username or password"
            return templates.TemplateResponse(
                "login.html", {"request": request, "msg": msg}
            )
        return response
    except HTTPException:
        msg = "Uknown Error"
        return templates.TemplateResponse(
            "login.html", {"request": request, "msg": msg}
        )


@router.get("/logout")
async def logout(request: Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse(
        "login.html", {"request": request, "msg": msg}
    )
    response.delete_cookie("access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def sign_up_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    email: STR_FORM,
    username: STR_FORM,
    firstname: STR_FORM,
    lastname: STR_FORM,
    password: STR_FORM,
    password2: STR_FORM,
    db: db_dependency,
):
    stmt = select(Users).filter(Users.username == username)
    validation1 = db.execute(stmt).scalar_one_or_none()
    stmt = select(Users).filter(Users.email == email)
    validation2 = db.execute(stmt).scalar_one_or_none()

    if password != password2 or validation1 is not None or validation2 is not None:
        msg = "Invalid registration request"
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg}
        )

    user = CreateUserRequest(
        username=username,
        email=email,
        first_name=firstname,
        last_name=lastname,
        role="",
        is_active=True,
        phone_number="",
        password=password,
    )
    new_user = user.model_copy(deep=True).model_dump()
    new_user["hashed_password"] = bcrypt_context.hash(new_user.pop("password"))
    user_ = Users(**new_user)
    db.add(user_)
    db.commit()

    msg = "User succefully created"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

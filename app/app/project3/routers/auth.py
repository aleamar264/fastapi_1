from datetime import timedelta
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models import Users
from passlib.context import CryptContext
from schemas import CreateUserRequest
from starlette import status
from schemas import UserModel, Token
from sqlalchemy import select
from dependencies import db_dependency, form_data, create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def authenticated_user(username: str, password: str, db) -> UserModel | bool:
    stmt = select(Users).filter(Users.username == username)
    user = db.execute(stmt).scalar_one_or_none()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


@router.get("/get_users")
async def get_users(db: db_dependency): ...


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user: CreateUserRequest):
    new_user = user.model_copy(deep=True).model_dump()
    new_user["hashed_password"] = bcrypt_context.hash(new_user.pop("password"))
    user_ = Users(**new_user)
    db.add(user_)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(form: form_data, db: db_dependency):
    user = authenticated_user(form.username, form.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )
    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=20)
    )
    return JSONResponse(
        {"access_token": token, "token_type": "bearer"}, status_code=200
    )

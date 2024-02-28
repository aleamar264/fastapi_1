from typing import Optional
from dependencies import db_dependency, user_dependency
from fastapi import APIRouter, HTTPException, Path
from passlib.context import CryptContext
from models import Users
from schemas import UserModel
from starlette import status
from schemas import UserVerification
from sqlalchemy import select, update


router = APIRouter(tags=["users"], prefix="/user")
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(db: db_dependency, user: user_dependency) -> Optional[UserModel]:
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    stmt = select(Users).where(Users.id == user.get("id"))
    if (result := db.execute(stmt).scalar_one_or_none()) is None:
        return result
    result = result.__dict__
    del result["hashed_password"]
    return UserModel(**result)


@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    db: db_dependency, user: user_dependency, password: UserVerification
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    stmt = select(Users).filter(Users.id == user.get("id"))
    result = db.execute(stmt).scalar_one()
    if not bcrypt_context.verify(password.password, result.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong password"
        )
    new_password = password.model_dump()
    password_ = {"hashed_password": bcrypt_context.hash(new_password["password"])}
    stmt = update(Users).where(Users.id == user.get("id")).values(**password_)
    db.execute(stmt)
    db.commit()


@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
def change_phone_number(
    db: db_dependency,
    user: user_dependency,
    phone_number: str = Path(min_length=11, max_length=13),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    stmt = (
        update(Users)
        .where(Users.id == user.get("id"))
        .values(**{"phone_number": phone_number})
    )
    db.execute(stmt)
    db.commit()

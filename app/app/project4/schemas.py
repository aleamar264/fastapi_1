from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Todo title",
                "description": "Description of todo",
                "priority": 3,
                "complete": True,
            }
        }


class GeneralPassword(BaseModel):
    password: str


class UserModel(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    is_active: bool
    phone_number: Optional[str] = None


class UserVerification(GeneralPassword):
    new_password: str = Field(min_length=6)


class CreateUserRequest(GeneralPassword, UserModel):
    class Config:
        json_schema_extra = {
            "example": {
                "username": "Almigthy user",
                "email": "superuser@email.com",
                "first_name": "Jhon",
                "last_name": "Doe",
                "role": "admin",
                "is_active": True,
                "phone_number": "+1 999999999",
                "password": "secret-password (shhhh)",
            }
        }


class AdminReturnUser(UserModel):
    id: int
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TodoResponse(BaseModel):
    priority: int
    id: int
    owner_id: int
    description: str
    complete: bool
    title: str

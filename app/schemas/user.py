from pydantic import BaseModel, EmailStr
from .token import Token


class UserBaseSchemas(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str


class UserCreateSchemas(UserBaseSchemas):
    password: str


class UserLoginSchemas(BaseModel):
    email: EmailStr
    password: str


class UserResponseSchemas(UserBaseSchemas):
    id: int

    class Config:
        orm_mode = True

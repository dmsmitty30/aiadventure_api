from enum import Enum
from typing import Optional

from pydantic import AliasChoices, BaseModel, EmailStr, Field


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"


class RegistrationStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"


class UserLoginStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER


class RegistrationResponse(BaseModel):
    access_token: str
    token_type: str


class UserLoginResponse(BaseModel):
    access_token: str


class User(BaseModel):
    user_id: str
    username: str = Field(validation_alias=AliasChoices("username", "email"))
    role: UserRole = UserRole.USER


class UserInDB(User):
    hashed_password: str
    role: UserRole = UserRole.USER

from pydantic import BaseModel, EmailStr, Field, AliasChoices
from typing import Optional
from enum import Enum


class RegistrationStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"

class UserLoginStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RegistrationResponse(BaseModel):
    access_token: str
    token_type: str

class UserLoginResponse(BaseModel):
    access_token: str

class User(BaseModel):
    user_id: str
    username: str = Field(validation_alias=AliasChoices('username', 'email'))


class UserInDB(User):
    
    hashed_password: str
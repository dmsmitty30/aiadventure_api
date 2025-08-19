import os
from datetime import datetime, timedelta

from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.database import create_user, get_user_by_email, get_user_by_id

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")
)  # 12 weeks default
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    hashed_password = pwd_context.hash(password)
    return hashed_password


"""
async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
"""


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user_object(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return user_id  # You can use this to fetch user details from DB
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def register_user(email: str, password: str, role: str = "user"):
    hashed_password = hash_password(password)
    existing_user = await get_user_by_email(email)
    if not existing_user:
        new_user_id = await create_user(email, hashed_password, datetime.utcnow(), role)
        return new_user_id
    else:
        raise HTTPException(
            status_code=409, detail="User with that name already exists."
        )


async def is_user_admin(user_id: str) -> bool:
    """Check if a user has admin role."""
    try:
        user = await get_user_by_id(user_id)
        if user and user.get("role") == "admin":
            return True
        return False
    except Exception:
        return False


async def get_user_role(user_id: str) -> str:
    """Get the role of a user."""
    try:
        user = await get_user_by_id(user_id)
        if user:
            return user.get("role", "user")
        return "user"
    except Exception:
        return "user"


async def login(email: str, plain_password: str):
    try:
        existing_user = await get_user_by_email(email)
        await verify_password(plain_password, existing_user["hashed_password"])
        return {"msg": "Login successful."}
    except:
        return None
        # raise HTTPException(status_code=401, detail="Invalid credentials")


def create_access_token(data: dict):
    to_encode = data.copy()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + access_token_expires
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token payload")
        return user_id
    except JWTError:
        raise ValueError("Invalid token")

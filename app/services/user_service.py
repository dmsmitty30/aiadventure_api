from app.database import get_user_by_email, create_user, get_user_by_id
from bson.objectid import ObjectId
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends
from jose import JWTError, jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
import bcrypt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 12*7*24*60 #12 weeks expiration.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:     
    hashed_password = pwd_context.hash(password)
    return hashed_password

'''
async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
'''
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_user_object(user_id):
    user=get_user_by_id(user_id)
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

async def register_user(email: str, password: str):
    hashed_password=hash_password(password)
    existing_user = await get_user_by_email(email)
    if not existing_user: 
        new_user_id=await create_user(email, hashed_password, datetime.utcnow()) 
        return new_user_id
    else:
        raise HTTPException(status_code=409, detail="User with that name already exists.")

async def login(email: str, plain_password: str):
    try: 
        existing_user = await get_user_by_email(email)
        await verify_password(plain_password, existing_user["hashed_password"])
        return {"msg": "Login successful."}
    except:
        return None
        #raise HTTPException(status_code=401, detail="Invalid credentials")



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






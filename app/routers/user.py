import json
from datetime import datetime, timedelta
from typing import Annotated

import httpx
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app.database import get_user_by_email
from app.schemas.user import UserCreate, UserLogin, UserLoginResponse
from app.services.user_service import (create_access_token, hash_password,
                                       register_user, verify_password)
from app.security import sanitize_email, validate_string_length

router = APIRouter()


@router.post("/register", response_model=UserLoginResponse)
async def register(user: UserCreate):
    try:
        # Sanitize and validate inputs
        email = sanitize_email(user.email)
        password = validate_string_length(user.password, min_length=8, max_length=128, field_name="Password")
        
        new_user_id = await register_user(email, password, user.role.value)
        access_token = create_access_token(data={"sub": str(new_user_id)})
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=409, detail={"status": "error", "error_message": str(e)}
        )


"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from jose import JWTError, jwt
import httpx
from app.auth import create_access_token  # Function for generating internal access tokens

# Replace with your OpenID Provider (Google, Auth0, Okta, etc.)
OIDC_PROVIDER_URL = "https://your-openid-provider.com"
CLIENT_ID = "your-client-id"

class OpenIDLogin(BaseModel):
    id_token: str  # Token from OpenID Provider

@router.post("/register", response_model=dict)
async def register(user: OpenIDLogin):
    try:
        # Verify the OpenID token with the provider
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OIDC_PROVIDER_URL}/userinfo", headers={"Authorization": f"Bearer {user.id_token}"})
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid OpenID token")

        user_info = response.json()
        user_email = user_info.get("email")
        user_id = user_info.get("sub")  # Unique identifier from OpenID

        if not user_email:
            raise HTTPException(status_code=400, detail="Email not found in OpenID token")

        # Here, check if the user exists in your DB (optional)
        # If not, create a user entry in your database

        # Generate an internal access token for your API
        access_token = create_access_token(data={"sub": user_id, "email": user_email})
        
        return {"access_token": access_token, "token_type": "bearer"}

    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "error_message": str(e)})


@router.post("/login", response_model=UserLoginResponse)
async def login(form_data: UserLogin):
    user_in_db =  await get_user_by_email(form_data.email)
    if not user_in_db or not verify_password(form_data.password, user_in_db["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"StatusCode":401, "status":"error", "error_code":"Bad Email or Password"}
    access_token = create_access_token(
        data={"sub": str(user_in_db["_id"])}
    )
    #return {"StatusCode":200, "status":"success", "access_token":access_token}
    return {"access_token": access_token, "token_type": "bearer"}"""

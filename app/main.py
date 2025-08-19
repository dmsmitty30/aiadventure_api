from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.database import get_user_by_email
from app.routers import admin, adventure, auth, user
from app.schemas.user import UserInDB
from app.services.user_service import create_access_token, verify_password

app = FastAPI()


app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers

app.include_router(adventure.router, prefix="/adventure", tags=["adventure"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
# app.include_router(web.router, prefix="/adventure", tags=["adventure"])

# app.include_router(web.router)


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = await get_user_by_email(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": str(user_dict["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}

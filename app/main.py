from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel

from app.database import get_user_by_email
from app.routers import admin, adventure, auth, user
from app.schemas.user import UserInDB
from app.services.user_service import create_access_token, verify_password

# Create a Bearer scheme for the docs
bearer_scheme = HTTPBearer(auto_error=False)

app = FastAPI(
    title="AI Adventure API",
    description="API for AI-powered adventure stories",
    version="1.0.0",
    openapi_tags=[
        {"name": "adventure", "description": "Adventure management endpoints"},
        {"name": "user", "description": "User management endpoints"},
        {"name": "admin", "description": "Admin-only endpoints"},
        {"name": "auth", "description": "Authentication endpoints"},
    ]
)

# Add global security scheme for Bearer token authentication
app.openapi_schema = None

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    
    # Add Bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


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

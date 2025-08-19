from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.schemas.adventure import AdventureCreate, AdventureNode
from app.services.adventure_service import (fetch_adventures,
                                            get_adventure_by_id)
from app.services.user_service import decode_access_token, get_user_object

router = APIRouter()
import os

cwd = os.getcwd()
print(cwd)

# Convert the Pydantic instance to a dictionary

config = AdventureCreate(
    prompt="Create an adventure starring a person named Dave that is based on the Olympic Peninsula of Washington State",
    min_words_per_level=100,
    max_words_per_level=200,
    max_levels=10,
    perspective="Second Person",
)

config_dict = config.dict()
# For choices, generate them from field types


templates = Jinja2Templates(directory="app/templates")


# Home Page
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    access_token = request.cookies.get("access_token")
    adventures = None
    user = None
    if access_token:
        user_id = decode_access_token(access_token)
        print("xxxxxxxxx")
        print(user_id)
        print(access_token)
        if user_id:
            adventures = await fetch_adventures(user_id)
            user = await get_user_object(user_id)

    print(user)
    return templates.TemplateResponse(
        "index.html", {"user": user, "request": request, "adventures": adventures}
    )


# Adventure Page
@router.get("/adventure/{adventure_id}/{adventure_node}", response_class=HTMLResponse)
async def adventure_node(adventure_id: str, adventure_node: int, request: Request):
    adventure = await get_adventure_by_id(adventure_id)
    access_token = request.cookies.get("access_token")
    return templates.TemplateResponse(
        "adventure.html",
        {
            "user": user,
            "request": request,
            "adventure": adventure,
            "adventure_id": adventure_id,
            "node_index": adventure_node,
        },
    )

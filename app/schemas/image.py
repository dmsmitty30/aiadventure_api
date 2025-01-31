from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ImageResponse(BaseModel):
    presigned_url: str
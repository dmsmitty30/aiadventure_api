from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ImageResponse(BaseModel):
    presigned_url: str

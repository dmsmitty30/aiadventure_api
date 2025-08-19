from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class APIKeyCreate(BaseModel):
    name: str
    expires_in_days: Optional[int] = None
    scopes: List[str] = ["read", "write"]


class APIKeyResponse(BaseModel):
    key_id: str
    name: str
    api_key: str  # Only shown once on creation
    expires_at: Optional[datetime]
    scopes: List[str]
    created_at: datetime


class APIKeyList(BaseModel):
    api_keys: List[dict]  # Will contain key info without the actual key


class APIKeyUpdate(BaseModel):
    name: Optional[str] = None
    scopes: Optional[List[str]] = None
    is_active: Optional[bool] = None

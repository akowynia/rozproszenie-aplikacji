from datetime import datetime
from typing import Optional
from pydantic import BaseModel, AnyHttpUrl


class ShortenRequest(BaseModel):
    url: AnyHttpUrl
    ttl_seconds: Optional[int] = None


class ShortenResponse(BaseModel):
    short_url: AnyHttpUrl
    short_code: str
    original_url: AnyHttpUrl
    expires_at: Optional[datetime]


class InfoResponse(BaseModel):
    short_code: str
    original_url: AnyHttpUrl
    created_at: datetime
    expires_at: Optional[datetime]
    is_expired: bool

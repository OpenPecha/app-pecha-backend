from typing import Optional
from pydantic import BaseModel

class ShareRequest(BaseModel):
    segment_id: Optional[str] = None
    language: Optional[str] = None
    url: str
    text_color: Optional[str] = None
    bg_color: Optional[str] = None
    tags: Optional[str] = None

class ShortUrlResponse(BaseModel):
    shortUrl: str
from typing import Optional
from pydantic import BaseModel

class ShareRequest(BaseModel):
    segment_id: Optional[str] = None
    language: Optional[str] = None
    url: str

class ShortUrlResponse(BaseModel):
    shortUrl: str
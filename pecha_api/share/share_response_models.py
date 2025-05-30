from typing import Optional
from pydantic import BaseModel
from .share_enums import (
    TextColor,
    BgColor
)

class ShareRequest(BaseModel):
    segment_id: Optional[str] = None
    language: Optional[str] = None
    url: str
    text_color: Optional[TextColor] = None
    bg_color: Optional[BgColor] = None
    tags: Optional[str] = None

class ShortUrlResponse(BaseModel):
    shortUrl: str
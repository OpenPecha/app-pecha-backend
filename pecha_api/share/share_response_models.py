from typing import Optional
from pydantic import BaseModel
from .share_enums import (
    TextColor,
    BgColor
)

class ShareRequest(BaseModel):
    logo: bool = False
    segment_id: Optional[str] = None
    language: Optional[str] = None
    url: str
    text_color: Optional[TextColor] = TextColor.DEFAULT
    bg_color: Optional[BgColor] = BgColor.DEFAULT
    tags: Optional[str] = None

class ShortUrlResponse(BaseModel):
    shortUrl: str
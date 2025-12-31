from pydantic import BaseModel
from typing import Optional, List


class TextGroupPayload(BaseModel):
  
    pecha_text_id: Optional[str] = None
    title: str | None = None
    language: Optional[str] = None
    isPublished: bool = False
    group_id: Optional[str] = None
    published_by: Optional[str] = None
    type: str
    categories: Optional[List[str]] = None
    views: Optional[int] = 0
    source_link: Optional[str] = None
    ranking: Optional[int] = None
    license: Optional[str] = None



from pydantic import BaseModel
from typing import Optional, List


class Title(BaseModel):
    bo: Optional[str] = None
    en: Optional[str] = None
    bophono: Optional[str] = None


class CatalogedTextsDetailsResponse(BaseModel):
    instance_id: str
    instance_type: str
    text_id: str
    language: str
    title: Title
    relationship: str


class CatalogedTexts(BaseModel):
    text_id: str
    title: Title
    language: str
    status: bool


class CatalogedTextsResponse(BaseModel):
    texts: List[CatalogedTexts]

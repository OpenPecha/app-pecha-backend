from pydantic import BaseModel
from typing import Optional

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

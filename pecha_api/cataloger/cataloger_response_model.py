from pydantic import BaseModel
from typing import Optional, List

class Title(BaseModel):
    bo: Optional[str] = None
    en: Optional[str] = None
    bophono: Optional[str] = None
    zh: Optional[str] = None
    
class Metadata(BaseModel):
    text_id:str
    title:Title
    language:str

class Relation(BaseModel):
    relation_type:str
    status:bool
    metadata:Metadata

class CatalogedTextsDetailsResponse(BaseModel):
    title:Title
    category_id: str
    status: bool
    relations:List[Relation]

class ExternalPechaTextResponse(BaseModel):
    title:Title
    category_id: str

class ExternalPechaInstanceRelatedResponse(BaseModel):
    title:Title
    text_id: str
    language: str
    relation_type:str
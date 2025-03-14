from typing import List

from pydantic import BaseModel
from .texts_models import Mapping

class TextModel(BaseModel):
    id: str
    title: str
    summary: str
    language: str
    source: str
    parent_id: str

class TextResponse(BaseModel):
    source: TextModel
    versions: List[TextModel]

class CreateTextRequest(BaseModel):
    titles: Dict[str, str]
    language: str
    is_published: bool
    created_date: str
    updated_date: str
    published_date: str
    published_by: str
    type: str
    categories: List[str]

class CreateSegmentRequest(BaseModel):
    content: str
    mapping: List[Mapping]
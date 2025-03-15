from typing import List, Dict

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
    titles: str
    language: str
    published_by: str
    type: str
    categories: List[str]

class CreateSegmentRequest(BaseModel):
    text_id: str
    content: str
    mapping: List[Mapping]
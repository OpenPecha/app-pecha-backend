from typing import List

from pydantic import BaseModel


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
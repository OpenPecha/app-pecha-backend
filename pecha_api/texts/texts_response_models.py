from typing import List, Optional

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

class Segment(BaseModel):
    segment_id: str
    segment_number: int

class Section(BaseModel):
    id: str
    title: str
    section_number: int
    parent_id: Optional[str] = None
    segments: List[Segment]
    sections: List["Section"]
    created_date: str
    updated_date: str
    published_date: str

class TableOfContentResponse(BaseModel):
    id : str
    text_id: str
    segments: List[Section]

class RootText(BaseModel):
    id: str
    title: str
    language: str
    type: str
    has_child: bool

class TextVersion(BaseModel):
    id: str
    title: str
    parent_id: str
    priority: int
    language: str
    type: str
    is_published: bool
    created_date: str
    updated_date: str
    published_date: str
    published_by: str

class TextVersionResponse(BaseModel):
    text: RootText
    versions: List[TextVersion]
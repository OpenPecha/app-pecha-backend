
from typing import List, Optional

from typing import Dict

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


class Text(BaseModel):
    id : str
    title: str
    language : str
    type : str
    is_published : bool
    created_date: str
    updated_date: str
    published_date: str
    published_by: str

class Category(BaseModel):
    id : str
    title: str
    description : str
    slug: str
    has_child: bool

class TextsCategoryResponse(BaseModel):
    category: Category
    texts : List[Text]
    total: int
    skip: int
    limit: int


from typing import List, Optional, Dict, Union

from pecha_api.terms.terms_response_models import TermsModel

from pydantic import BaseModel
from .segments.segments_models import Mapping

class CreateTextRequest(BaseModel):
    title: str
    language: str
    parent_id: Optional[str] = None
    published_by: str
    type: str
    categories: List[str]

class TextModel(BaseModel):
    id: str
    title: str
    language: str
    type: str
    is_published: bool
    created_date: str
    updated_date: str
    published_date: str
    published_by: str
    categories: List[str]
    parent_id: Optional[str] = None

class RootText(BaseModel):
    id: str
    title: str
    language: str
    type: str
    is_published: bool
    created_date: str
    updated_date: str
    published_date: str
    published_by: str
    categories: List[str]
    parent_id: Optional[str] = None


# Text TOC Response Models
class Translation(BaseModel):
    text_id: str
    language: str
    content: str

class TextSegment(BaseModel):
    segment_id: str
    segment_number: Optional[int] = None
    content: Optional[str] = None
    translation: Optional[Translation] = None

class CreateTableOfContentTextSegment(BaseModel):
    segment_id: str
    segment_number: int

class Section(BaseModel):
    id: str
    title: str
    section_number: int
    parent_id: Optional[str] = None
    segments: List[Union[TextSegment, CreateTableOfContentTextSegment]] = []
    sections: Optional[List["Section"]] = None
    created_date: str
    updated_date: str
    published_date: str

class TableOfContent(BaseModel):
    id: str
    text_id: str
    segments: List[Section]

class TableOfContentResponse(BaseModel):
    text_detail: TextModel
    contents: List[TableOfContent]

class TextDetailsRequest(BaseModel):
    content_id: str
    version_id: Optional[str] = None
    skip: int
    limit: int

class CreateTableOfContentRequest(BaseModel):
    text_id: str
    segments: List[Section]

# Text Version Response Models

class TextVersion(BaseModel):
    id: str
    title: str
    parent_id: str
    priority: Optional[int] = None
    language: str
    type: str
    is_published: bool
    created_date: str
    updated_date: str
    published_date: str
    published_by: str

class TextVersionResponse(BaseModel):
    text: TextModel
    versions: List[TextVersion]

# Texts Category Response Models
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

class TextsCategoryResponse(BaseModel):
    term: TermsModel
    texts : List[Text]
    total: int
    skip: int
    limit: int

# Texts Info Response Models
class RelatedTexts(BaseModel):
    id: str
    title: str
    count: int

class TextInfos(BaseModel):
    text_id: str
    about_text: str
    translations: int
    related_texts: List[RelatedTexts]
    sheets: int
    web_pages: int
    short_url: str

class TextInfosResponse(BaseModel):
    text_infos: TextInfos
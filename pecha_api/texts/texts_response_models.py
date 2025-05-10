from typing import List, Optional, Dict, Union
from uuid import UUID

from pecha_api.terms.terms_response_models import TermsModel

from pydantic import BaseModel

class CreateTextRequest(BaseModel):
    title: str
    language: str
    parent_id: Optional[str] = None
    group_id: str
    published_by: str
    type: str
    categories: List[str]

class TextModel(BaseModel):
    id: str
    title: str
    language: str
    type: str
    group_id: Optional[str] = None
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

class DetailTextSegment(BaseModel):
    segment_id: str
    segment_number: Optional[int] = None
    content: Optional[str] = None
    translation: Optional[Translation] = None

class DetailSection(BaseModel):
    id: str
    title: str
    section_number: int
    parent_id: Optional[str] = None
    segments: List[DetailTextSegment] = []
    sections: Optional[List["DetailSection"]] = None
    created_date: str 
    updated_date: str
    published_date: str 

class DetailTableOfContent(BaseModel):
    id: str
    text_id: str
    sections: List[DetailSection]

class DetailTextMapping(BaseModel):
    segment_id: Optional[str] = None
    section_id: Optional[str] = None

class DetailTableOfContentResponse(BaseModel):
    text_detail: TextModel
    mapping: DetailTextMapping
    content: DetailTableOfContent
    skip: int
    current_section: int
    limit: int
    total: int

class TextSegment(BaseModel):
    segment_id: str
    segment_number: int

class Section(BaseModel):
    id: str
    title: str
    section_number: int
    parent_id: Optional[str] = None
    segments: List[TextSegment] = []
    sections: Optional[List["Section"]] = None
    created_date: str 
    updated_date: str
    published_date: str 

class TableOfContent(BaseModel):
    id: Optional[str] = None
    text_id: str
    sections: List[Section]

class TableOfContentResponse(BaseModel):
    text_detail: TextModel
    contents: List[TableOfContent]

class TextDetailsRequest(BaseModel):
    content_id: Optional[str] = None
    version_id: Optional[str] = None
    segment_id: Optional[str] = None
    section_id: Optional[str] = None
    skip: int = 0
    limit: int = 1

# Text Version Response Models

class TextVersion(BaseModel):
    id: str
    title: str
    parent_id: Optional[str] = None
    priority: Optional[int] = None
    language: str
    type: str
    group_id: Optional[str] = None 
    table_of_contents: List[str] = []
    is_published: bool
    created_date: str
    updated_date: str
    published_date: str
    published_by: str

class TextVersionResponse(BaseModel):
    text: Optional[TextModel] = None
    versions: Optional[List[TextVersion]] = None

# Texts Category Response Models
class Text(BaseModel):
    id : str
    title: str
    language : str
    type : str
    group_id: Optional[str] = None
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
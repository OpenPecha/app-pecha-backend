from pydantic import BaseModel
from typing import List, Optional
from .search_enums import SearchType

class Search(BaseModel):
    text: Optional[str] = None
    type: Optional[SearchType] = None

class TextIndex(BaseModel):
    text_id: str
    language: str
    title: str
    published_date: str

class SegmentMatch(BaseModel):
    segment_id: str
    content: str

class SourceResultItem(BaseModel):
    text: TextIndex
    segment_match: List[SegmentMatch]

class SheetResultItem(BaseModel):
    sheet_title: str
    sheet_summary: str
    publisher_id: int
    sheet_id: int
    publisher_name: str
    publisher_url: str
    publisher_image: str
    publisher_position: str
    publisher_organization: str

class SearchResponse(BaseModel):
    search: Search
    sources: Optional[List[SourceResultItem]] = []
    sheets: Optional[List[SheetResultItem]] = []
    skip: int
    limit: int
    total: int

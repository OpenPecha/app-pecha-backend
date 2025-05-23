from pydantic import BaseModel
from typing import List, Optional

class Search(BaseModel):
    text: Optional[str] = None

class Text(BaseModel):
    text_id: str
    language: str
    title: str
    published_date: str

class SegmentMatch(BaseModel):
    segment_id: str
    content: str

class Source(BaseModel):
    text: Text
    segment_match: List[SegmentMatch]

class Sheet(BaseModel):
    sheet_title: str
    sheet_summary: str
    publisher_id: int
    sheet_id: int
    publisher_name: str
    publisher_url: str
    publisher_image: str
    publisher_position: str
    publisher_organization: str

class SearchSheetResponse(BaseModel):
    search: Search
    sheets: List[Sheet] = []
    skip: int
    limit: int
    total: int

class SearchSourceResponse(BaseModel):
    search: Search
    sources: List[Source] = []
    skip: int
    limit: int
    total: int

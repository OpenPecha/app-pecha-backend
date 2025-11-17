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

# Multilingual Search Models
class ExternalSegmentEntity(BaseModel):
    """Entity from external multilingual search API"""
    text: str

class ExternalSearchResult(BaseModel):
    """Individual result from external multilingual search API"""
    id: str
    distance: float  # Relevance score/distance
    entity: ExternalSegmentEntity
    segmentation_ids: Optional[List[str]] = None # External segment IDs to map

class ExternalSearchResponse(BaseModel):
    """Response from external multilingual search API"""
    query: str
    search_type: str
    results: List[ExternalSearchResult]
    count: int

class MultilingualSegmentMatch(BaseModel):
    """Enriched segment match with ranking"""
    segment_id: str
    content: str
    relevance_score: float  # Distance/ranking from external API
    pecha_segment_id: str  # External segmentation ID

class MultilingualSourceResult(BaseModel):
    """Source result with multilingual search enhancements"""
    text: TextIndex
    segment_matches: List[MultilingualSegmentMatch]

class MultilingualSearchResponse(BaseModel):
    """Response for multilingual search endpoint"""
    query: str
    search_type: str
    sources: List[MultilingualSourceResult]
    skip: int
    limit: int
    total: int

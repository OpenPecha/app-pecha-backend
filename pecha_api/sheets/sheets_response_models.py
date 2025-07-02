from __future__ import annotations

from typing import List, Union, Optional

from pydantic import BaseModel, model_validator

from pecha_api.utils import Utils

from pecha_api.texts.segments.segments_models import SegmentType

class Source(BaseModel):
    position: int
    type: SegmentType
    content: str

class CreateSheetRequest(BaseModel):
    title: str
    source: List[Source]
    is_published: bool = False

class SheetSegment(BaseModel):
    segment_id: str
    segment_number: int
    content: Optional[str] = None
    text_title: Optional[str] = None
    language: Optional[str] = None
    type: SegmentType

class SheetSection(BaseModel):
    title: Optional[str] = None
    section_number: int
    parent_id: Optional[str] = None
    segments: List[SheetSegment]


class Publisher(BaseModel):
    name: str
    username: str
    email: str
    avatar_url: Optional[str] = None

class SheetDetailDTO(BaseModel):
    id: str
    sheet_title: str
    created_date: str
    publisher: Publisher
    content: Optional[SheetSection] = None
    skip: int
    limit: int
    total: int


class SheetDTO(BaseModel):
    id: str
    title: str
    summary: str
    published_date: str
    time_passed: str
    views: str
    likes: List[str]
    publisher: Publisher
    language: Optional[str] = None

class SheetDTOResponse(BaseModel):
    sheets: List[SheetDTO]
    skip: int
    limit: int
    total: int

class SheetIdRequest(BaseModel):
    id: str

class SheetImageResponse(BaseModel):
    url: str

class SheetIdResponse(BaseModel):
    sheet_id: str
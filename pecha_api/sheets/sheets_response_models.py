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
    id: str
    title: Optional[str] = None
    section_number: int
    parent_id: Optional[str] = None
    segments: List[SheetSegment]


class Publisher(BaseModel):
    name: str
    username: str
    email: str
    avatar_url: Optional[str] = None

class SheetDTO(BaseModel):
    id: str
    sheet_title: str
    created_date: str
    publisher: Publisher
    content: SheetSection
    skip: int
    current_section: int
    limit: int
    total: int


class SheetIdRequest(BaseModel):
    id: str

class SheetImageResponse(BaseModel):
    url: str

class SheetIdResponse(BaseModel):
    sheet_id: str
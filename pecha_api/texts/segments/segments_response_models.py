from pydantic import BaseModel
from typing import List
from .segments_models import Mapping


class CreateSegment(BaseModel):
    content: str
    mapping: List[Mapping]


class CreateSegmentRequest(BaseModel):
    text_id: str
    segments: List[CreateSegment]


class MappingResponse(BaseModel):
    text_id: str
    segments: List[str]

class SegmentDTO(BaseModel):
    id: str
    text_id: str
    content: str
    mapping: List[MappingResponse]

class SegmentResponse(BaseModel):
    segments: List[SegmentDTO]

class ParentSegment(BaseModel):
    segment_id: str
    segment_number: int
    content: str

# segment translation models
class SegmentTranslation(BaseModel):
    text_id: str
    title: str
    source: str
    language: str
    content: str

class SegmentTranslationsResponse(BaseModel):
    parent_segment: ParentSegment
    translations: List[SegmentTranslation]

# segemtn commentary models
class SegmentCommentry(BaseModel):
    text_id: str
    title: str
    content: str
    language: str
    count: int

class SegmentCommentariesResponse(BaseModel):
    parent_segment: ParentSegment
    commentaries: List[SegmentCommentry]
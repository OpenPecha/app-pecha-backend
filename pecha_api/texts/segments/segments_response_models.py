from pydantic import BaseModel
from typing import List, Optional
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
    content: str

# segment translation models
class SegmentTranslation(BaseModel):
    segment_id: str
    text_id: str
    title: str
    source: str
    language: str
    content: str

class SegmentTranslationsResponse(BaseModel):
    parent_segment: ParentSegment
    translations: List[SegmentTranslation]

# segment commentary models
class SegmentCommentry(BaseModel):
    segment_id: str
    text_id: str
    title: str
    content: str
    language: str
    count: int

class SegmentCommentariesResponse(BaseModel):
    parent_segment: ParentSegment
    commentaries: List[SegmentCommentry]

# segment info models

class SegmentInfosRequest(BaseModel):
    text_id: str

class RelatedText(BaseModel):
    commentaries: Optional[int] = 0
    root_text: Optional[int] = 0

class Resources(BaseModel):
    sheets: int

class SegmentInfos(BaseModel):
    segment_id: str
    translations: Optional[int] = 0
    related_text: RelatedText
    resources: Resources

class SegmentInfosResponse(BaseModel):
    segment_infos: SegmentInfos

# segment's root mapping models

class SegmentRootMapping(BaseModel):
    segment_id: str
    text_id: str
    title: str
    content: str
    language: str

class SegmentRootMappingResponse(BaseModel):
    parent_segment: ParentSegment
    segment_root_mapping: List[SegmentRootMapping]
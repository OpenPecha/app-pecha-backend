from pydantic import BaseModel
from typing import List
from .segments_models import Mapping

class CreateSegment(BaseModel):
    content: str
    mapping: List[Mapping]

class CreateSegmentRequest(BaseModel):
    text_id: str
    segments: List[CreateSegment]

class SegmentResponse(BaseModel):
    id: str
    text_id: str
    content: str
    mapping: List[Mapping]

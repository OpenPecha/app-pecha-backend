from typing import List
from pydantic import BaseModel


class MappingsModel(BaseModel):
    parent_text_id: str
    segments: List[str]

class TextMappingRequest(BaseModel):
    text_id: str
    segment_id: str
    mappings: List[MappingsModel]
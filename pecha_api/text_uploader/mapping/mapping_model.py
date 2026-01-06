from pydantic import BaseModel
from typing import List

class TriggerMappingPayload(BaseModel):
    text_id: List[str]
    source: str
    destination: str


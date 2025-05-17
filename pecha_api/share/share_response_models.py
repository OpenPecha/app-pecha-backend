from typing import Optional
from pydantic import BaseModel

class ImageGenerationRequest(BaseModel):
    segment_id: Optional[str] = None
    language: str = "en"
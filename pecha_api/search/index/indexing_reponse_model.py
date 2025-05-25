
from pydantic import BaseModel
from typing import Optional

class ReindexResponse(BaseModel):
    status: Optional[str] = None
    message: Optional[str] = None

class ReindexRequest(BaseModel):
    recreate_indices: bool
    content_type: Optional[str] = None
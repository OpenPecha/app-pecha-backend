import uuid
from typing import Dict

from pydantic import BaseModel,Field


class Sheet(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    titles: Dict[str, str] = Field(default_factory={dict})
    summaries: Dict[str, str] = Field(default_factory={dict})
    publisher_id: str
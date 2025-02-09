import uuid
from typing import Dict

from pydantic import BaseModel, Field


class Text(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    titles: Dict[str, str] = Field(default_factory={})
    summaries: Dict[str, str] = Field(default_factory={})
    default_language: str
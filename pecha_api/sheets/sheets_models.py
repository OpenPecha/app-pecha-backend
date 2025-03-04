import uuid
from typing import Dict, List

from pydantic import BaseModel,Field


class Sheet(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    titles: Dict[str, str] = Field(default_factory={})
    summaries: Dict[str, str] = Field(default_factory={})
    date: str
    views: str
    topics: List[Dict[str, str]] = Field(default_factory=[])
    published_time: int
    publisher_id: str
    #topic_id
    #created date
    #modified date
    #published date
    #views
    #likes

    



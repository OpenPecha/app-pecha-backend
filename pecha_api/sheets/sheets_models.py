import uuid
from typing import Dict, List, Union

from beanie import PydanticObjectId
from pydantic import BaseModel,Field


class Sheet(BaseModel):
    # id: uuid.UUID = Field(default_factory=uuid.uuid4)
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    publisher_id: str
    titles: Dict[str, str] = Field(default_factory={})
    summaries: Dict[str, str] = Field(default_factory={})
    source: List[Dict[str, Union[Dict, str]]] = Field(default_factory=[])
    creation_date: str
    modified_date: str
    published_date: str
    published_time: int
    views: str
    likes: List[Dict[str, str]] = Field(default_factory=[])
    collection: List[str] = Field(default_factory=[])
    topics: List[Dict[str, str]] = Field(default_factory=[]),




from typing import List, Dict, Optional

from pydantic import BaseModel


class TopicModel(BaseModel):
    id: str
    title: str
    has_child: bool

class CreateTopicRequest(BaseModel):
    titles: Dict[str, str]
    parent_id: Optional[str]
    default_language: str

class TopicsResponse(BaseModel):
    parent: Optional[TopicModel]
    topics: List[TopicModel]
    total: int
    skip: int
    limit: int
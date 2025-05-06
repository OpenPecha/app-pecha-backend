from typing import List

from pydantic import BaseModel


class TopicModel(BaseModel):
    id: str
    title: str

class TopicsResponse(BaseModel):
    topics: List[TopicModel]
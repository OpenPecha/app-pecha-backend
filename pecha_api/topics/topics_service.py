from typing import Optional

from fastapi import Query

from config import get
from topics.topic_response_models import TopicsResponse, TopicModel
from topics.topics_repository import get_topics


def get_all_topics(language: str, search: Optional[str] = Query(None, description="Filter topics by title prefix")) -> TopicsResponse:
    topics = get_topics(search=search)
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    topic_list = [
        TopicModel(
            id=str(topic.id),
            title=topic.titles.get(language,"")
        )
        for topic in topics
    ]
    topic_response = TopicsResponse(topics=topic_list)
    return topic_response

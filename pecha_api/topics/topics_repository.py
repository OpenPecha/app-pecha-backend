import logging
from typing import Optional

from beanie import PydanticObjectId
from beanie.exceptions import CollectionWasNotInitialized

from pecha_api.constants import get_parent_id
from .topics_models import Topic
from .topics_response_models import CreateTopicRequest


async def get_topics_by_parent(
        parent_id: Optional[str],
        search: Optional[str],
        skip: int,
        limit: int) -> list[Topic]:
    try:
        topic_parent_id = get_parent_id(parent_id=parent_id)
        terms = await Topic.get_children_by_id(parent_id=topic_parent_id, search=search, skip=skip, limit=limit)
        return terms
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return []


async def get_child_count(parent_id: Optional[str]) -> int:
    topic_parent_id = get_parent_id(parent_id=parent_id)
    count = await Topic.count_children(parent_id=topic_parent_id)
    return count


async def create_topic(create_topic_request: CreateTopicRequest) -> Topic:
    topic_parent_id = get_parent_id(parent_id=create_topic_request.parent_id)
    new_topic = Topic(titles=create_topic_request.titles, parent_id=topic_parent_id,
                      default_language=create_topic_request.default_language)
    saved_topic = await new_topic.insert()
    return saved_topic


def get_term_by_id(topic_id: str):
    return Topic(titles={"en": "Topic 1", "bo": "གྲྭ་ཚན 1"},parent_id=PydanticObjectId("60d21b4667d0d8992e610c85"), default_language='en')
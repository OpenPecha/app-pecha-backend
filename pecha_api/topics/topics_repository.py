import logging
from typing import Optional

from beanie import PydanticObjectId
from beanie.exceptions import CollectionWasNotInitialized

from .topics_models import Topic
from .topics_response_models import CreateTopicRequest


async def get_topics_by_parent(parent_id:Optional[str]) -> list[Topic]:
    try:
        topic_parent_id = None
        if parent_id is not None:
            topic_parent_id = PydanticObjectId(parent_id)
        terms = await Topic.get_children_by_id(parent_id=topic_parent_id)
        return terms
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return []

async def create_topic(create_topic_request: CreateTopicRequest) -> Topic:
    topic_parent_id = None
    if create_topic_request.parent_id is not None:
        topic_parent_id = PydanticObjectId(create_topic_request.parent_id)
    new_topic= Topic(titles=create_topic_request.titles, parent_id=topic_parent_id,default_language=create_topic_request.default_language)
    saved_topic = await new_topic.insert()
    return saved_topic


def get_term_by_id(topic_id: str):
    return Topic(titles={"en": "Topic 1", "bo": "གྲྭ་ཚན 1"})
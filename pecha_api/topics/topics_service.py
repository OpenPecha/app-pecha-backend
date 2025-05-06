from typing import Optional

from starlette import status

from pecha_api.utils import Utils
from pecha_api.config import get
from pecha_api.sheets.sheets_service import get_sheets
from ..users.users_service import verify_admin_access
from .topics_response_models import TopicsResponse, TopicModel, CreateTopicRequest
from .topics_repository import get_topics_by_parent, create_topic, get_child_count, get_term_by_id, get_topic_by_id
from fastapi import HTTPException


async def get_topics(language: Optional[str], search: Optional[str], hierarchy: Optional[bool], parent_id: Optional[str], skip: int, limit: int) -> TopicsResponse:
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    total = await get_child_count(parent_id=parent_id)
    parent_topic = await get_topic(topic_id=parent_id, language=language)
    topics = await get_topics_by_parent(
        parent_id=parent_id,
        language=language,
        search=search,
        hierarchy=hierarchy,
        skip=skip,
        limit=limit
    )
    topic_list = [
        TopicModel(
            id=str(topic.id),
            title=Utils.get_value_from_dict(values=topic.titles, language=language),
            has_child=topic.has_sub_child
        )
        for topic in topics
    ]
    topic_response = TopicsResponse(parent=parent_topic,topics=topic_list, total=total, skip=skip, limit=limit)
    return topic_response

async def create_new_topic(create_topic_request: CreateTopicRequest, token: str, language: Optional[str]) -> TopicModel:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        new_topic = await create_topic(create_topic_request=create_topic_request)
        if language is None:
            language = get("DEFAULT_LANGUAGE")
        return TopicModel(
            id=str(new_topic.id),
            title=Utils.get_value_from_dict(values=new_topic.titles, language=language),
            has_child=new_topic.has_sub_child
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


async def get_topic(topic_id: str, language: str) -> Optional[TopicModel]:
    selected_topic = await get_topic_by_id(topic_id=topic_id)
    if selected_topic:
        return TopicModel(
            id=str(selected_topic.id),
            title=Utils.get_value_from_dict(values=selected_topic.titles, language=language),
            has_child=selected_topic.has_sub_child
        )
    return None


def get_sheets_by_topic(topic_id: str, language: str):
    selected_term = get_term_by_id(topic_id=topic_id)
    if selected_term:
        sheet_response = get_sheets(topic_id=selected_term.id, language=language)
        return sheet_response
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

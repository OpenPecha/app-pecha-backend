from typing import Optional

from starlette import status

from pecha_api.constants import get_value_from_dict
from pecha_api.config import get
from pecha_api.sheets.sheets_service import get_sheets
from ..users.users_service import verify_admin_access
from .topics_response_models import TopicsResponse, TopicModel, CreateTopicRequest
from .topics_repository import get_topics_by_parent, create_topic, get_child_count, get_term_by_id
from fastapi import HTTPException


async def get_topics(language: Optional[str], search: Optional[str], heirarchy: Optional[bool], parent_id: Optional[str], skip: int, limit: int) -> TopicsResponse:
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    total = await get_child_count(parent_id=parent_id)
    topics = await get_topics_by_parent(
        parent_id=parent_id,
        language=language,
        search=search,
        heirarchy=heirarchy,
        skip=skip,
        limit=limit
    )
    

    topic_list = [
        TopicModel(
            id=str(topic.id),
            title=get_value_from_dict(values=topic.titles,language=language),
            parent_id=str(topic.parent_id)
        )
        for topic in topics
    ]
    topic_response = TopicsResponse(topics=topic_list,total=total,skip=skip,limit=limit)
    return topic_response

async def create_new_topic(create_topic_request: CreateTopicRequest, token: str, language: Optional[str]) -> TopicModel:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        new_term = await create_topic(create_topic_request=create_topic_request)
        if language is None:
            language = get("DEFAULT_LANGUAGE")
        return TopicModel(
            id=str(new_term.id),
            title=get_value_from_dict(values=new_term.titles,language=language),
            parent_id=str(new_term.parent_id)
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


def get_sheets_by_topic(topic_id: str, language: str):
    selected_term = get_term_by_id(topic_id=topic_id)
    if selected_term:
        sheet_response = get_sheets(topic_id=selected_term.id, language=language)
        return sheet_response
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

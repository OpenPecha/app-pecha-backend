from typing import Optional

from fastapi import Query
from starlette import status

from pecha_api.config import get
from pecha_api.sheets.sheets_service import get_sheets
from ..users.users_service import verify_admin_access
from .topics_response_models import TopicsResponse, TopicModel, CreateTopicRequest
from .topics_repository import get_topics_by_parent, get_term_by_id, create_topic
from fastapi import HTTPException


async def get_topics(language: str,
                   parent_id: Optional[str] = Query(None, description="Filter topics by title prefix")) -> TopicsResponse:
    topics = await get_topics_by_parent(parent_id=parent_id)
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    topic_list = [
        TopicModel(
            id=str(topic.id),
            title=topic.titles.get(language, "")
        )
        for topic in topics
    ]
    topic_response = TopicsResponse(topics=topic_list)
    return topic_response

async def create_new_topic(create_topic_request: CreateTopicRequest, token: str, language: str) -> TopicModel:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        new_term = await create_topic(create_topic_request=create_topic_request)
        if language is None:
            language = get("DEFAULT_LANGUAGE")
        return TopicModel(
            id=str(new_term.id),
            title=new_term.titles[language]
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

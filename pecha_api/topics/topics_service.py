from typing import Optional

from fastapi import Query
from starlette import status

from config import get
from sheets.sheets_service import get_sheets
from topics.topic_response_models import TopicsResponse, TopicModel
from topics.topics_repository import get_topics, get_term_by_id
from fastapi import HTTPException


def get_all_topics(language: str,
                   search: Optional[str] = Query(None, description="Filter topics by title prefix")) -> TopicsResponse:
    topics = get_topics(search=search)
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


def get_sheets_by_topic(topic_id: str, language: str):
    selected_term = get_term_by_id(topic_id=topic_id)
    if selected_term:
        sheet_response = get_sheets(topic_id=selected_term.id, language=language)
        return sheet_response
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

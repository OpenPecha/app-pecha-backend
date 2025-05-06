from __future__ import annotations
from fastapi import APIRouter
from fastapi.security import HTTPBearer
from starlette import status

from .topics_service import get_all_topics, get_sheets_by_topic

oauth2_scheme = HTTPBearer()
topics_router = APIRouter(
    prefix="/topics",
    tags=["Topics"]
)


@topics_router.get("", status_code=status.HTTP_200_OK)
def read_topics(language: str | None):
    return get_all_topics(language=language)


@topics_router.get("{topic_id}/sheets", status_code=status.HTTP_200_OK)
def get_sheets_for_topic(topic_id: str, language: str | None):
    return get_sheets_by_topic(topic_id=topic_id, language=language)

from __future__ import annotations
from fastapi import APIRouter
from fastapi.security import HTTPBearer
from starlette import status

from topics.topics_service import get_all_topics

oauth2_scheme = HTTPBearer()
topics_router = APIRouter(
    prefix="/topics",
    tags=["Topics"]
)


@topics_router.get("", status_code=status.HTTP_200_OK)
def read_topics(language: str  | None):
    return get_all_topics(language=language)

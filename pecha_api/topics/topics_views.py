from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from .topics_response_models import CreateTopicRequest
from .topics_service import get_topics_by_first_letter, get_topics, get_sheets_by_topic, create_new_topic
from typing import Annotated

oauth2_scheme = HTTPBearer()
topics_router = APIRouter(
    prefix="/topics",
    tags=["Topics"]
)


@topics_router.get("", status_code=status.HTTP_200_OK)
async def read_topics(
        parent_id: Optional[str] = Query(None, description="Filter topics by title prefix"),
        language: Optional[str] = None,
        skip: int = Query(default=0, ge=0, description="Number of records to skip"),
        limit: int = Query(default=10, ge=1, le=100, description="Number of records to return")
):
    return await get_topics(
        parent_id=parent_id,
        language=language,
        skip=skip,
        limit=limit
    )

@topics_router.get("/by_first_letter", status_code=status.HTTP_200_OK)
async def read_topics_by_first_letter(
    parent_id: Optional[str] = Query(None, description="Filter topics by title prefix"),
    language: Optional[str] = None,
    first_letter: str = Query(None, description="Filter topics by first letter"),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return")
):
    return await get_topics_by_first_letter(
        parent_id=parent_id,
        language=language,
        first_letter=first_letter,
        skip=skip,
        limit=limit
    )


@topics_router.post("", status_code=status.HTTP_201_CREATED)
async def create_topic(create_topic_request: CreateTopicRequest,
                       authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
                       language: Optional[str] = None):
    return await create_new_topic(
        create_topic_request=create_topic_request,
        token=authentication_credential.credentials,
        language=language)


@topics_router.get("/{topic_id}/sheets", status_code=status.HTTP_200_OK)
async def get_sheets_for_topic(topic_id: str, language: Optional[str] = None):
    return await get_sheets_by_topic(
        topic_id=topic_id,
        language=language
    )

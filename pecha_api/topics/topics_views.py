from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from .topics_response_models import CreateTopicRequest
from .topics_service import get_topics, create_new_topic
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
        search: Optional[str] = None,
        hierarchy: bool = Query(default=True),
        skip: int = Query(default=0, ge=0, description="Number of records to skip"),
        limit: int = Query(default=10, ge=1, le=100, description="Number of records to return")
):
    return await get_topics(
        parent_id=parent_id,
        language=language,
        search=search,
        hierarchy=hierarchy,
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


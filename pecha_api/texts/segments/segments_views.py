from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import APIRouter, Depends, Query
from starlette import status

from typing import Annotated

from .segments_service import create_new_segment, get_translations_by_segment_id
from .segments_response_models import CreateSegmentRequest

oauth2_scheme = HTTPBearer()
segment_router = APIRouter(
    prefix="/segments",
    tags=["Segments"]
)


@segment_router.post("", status_code=status.HTTP_201_CREATED)
async def create_segment(
    create_segment_request: CreateSegmentRequest,
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
    ):
    return await create_new_segment(create_segment_request=create_segment_request, token=authentication_credential.credentials)


@segment_router.get("/{segment_id}/translations", status_code=status.HTTP_200_OK)
async def get_translations_for_segment(
    segment_id: str,
    skip: int = Query(default=0),
    limit: int = Query(default=10),
):
    return await get_translations_by_segment_id(
        segment_id=segment_id,
        skip=skip,
        limit=limit
    )
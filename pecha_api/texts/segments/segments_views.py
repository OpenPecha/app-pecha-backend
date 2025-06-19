from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import APIRouter, Depends
from starlette import status

from typing import Annotated

from .segments_service import (
    create_new_segment,
    get_translations_by_segment_id,
    get_commentaries_by_segment_id,
    get_segment_details_by_id, 
    get_infos_by_segment_id,
    get_root_text_mapping_by_segment_id
)
from .segments_response_models import (
    CreateSegmentRequest,
    SegmentDTO,
    SegmentResponse,
    SegmentInfoResponse,
    SegmentTranslationsResponse,
    SegmentCommentariesResponse
)

oauth2_scheme = HTTPBearer()
segment_router = APIRouter(
    prefix="/segments",
    tags=["Segments"]
)

from fastapi import Query


@segment_router.post("", status_code=status.HTTP_201_CREATED)
async def create_segment(
    create_segment_request: CreateSegmentRequest,
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
) -> SegmentResponse:
    return await create_new_segment(create_segment_request=create_segment_request, token=authentication_credential.credentials)

@segment_router.get("/{segment_id}", status_code=status.HTTP_200_OK)
async def get_segment(
    segment_id: str,
    text_details: bool = Query(default=False)
) -> SegmentDTO:
    return await get_segment_details_by_id(segment_id=segment_id, text_details=text_details)

@segment_router.get("/{segment_id}/infos", status_code=status.HTTP_200_OK)
async def get_infos_for_segment(
    segment_id: str
) -> SegmentInfoResponse:
    return await get_infos_by_segment_id(segment_id=segment_id)

@segment_router.get("/{segment_id}/root_text", status_code=status.HTTP_200_OK)
async def get_root_text_for_segment(
    segment_id: str
):
    return await get_root_text_mapping_by_segment_id(segment_id=segment_id)

@segment_router.get("/{segment_id}/translations", status_code=status.HTTP_200_OK)
async def get_translations_for_segment(
    segment_id: str
) -> SegmentTranslationsResponse:
    return await get_translations_by_segment_id(
        segment_id=segment_id
    )

@segment_router.get("/{segment_id}/commentaries", status_code=status.HTTP_200_OK)
async def get_commentaries_for_segment(
    segment_id: str
) -> SegmentCommentariesResponse:
    return await get_commentaries_by_segment_id(
        segment_id=segment_id
    )

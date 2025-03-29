from uuid import UUID

from .segments_repository import create_segment, check_segment_exists, check_all_segment_exists, get_segment_by_id
from .segments_response_models import CreateSegmentRequest, SegmentResponse
from fastapi import HTTPException
from starlette import status

from typing import List

from ..texts_service import validate_text_exits
from ...users.users_service import verify_admin_access


async def validate_segment_exists(segment_id: str):
    uuid_segment_id = UUID(segment_id)
    is_exists = await check_segment_exists(segment_id=uuid_segment_id)
    if not is_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Segment not found')
    return is_exists

async def validate_segments_exists(segment_ids: List[str]):
    uuid_segment_ids = [UUID(segment_id) for segment_id in segment_ids]
    all_exists = await check_all_segment_exists(segment_ids=uuid_segment_ids)
    if not all_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Segment not found")
    return all_exists

async def get_segment_details_by_id(segment_id: str) -> SegmentResponse:
    uuid_segment_id = UUID(segment_id)
    segment = await get_segment_by_id(segment_id=uuid_segment_id)
    if not segment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Segment not found')
    return SegmentResponse(
        id=str(segment.id),
        text_id=segment.text_id,
        content=segment.content,
        mapping=segment.mapping
    )

async def create_new_segment(create_segment_request: CreateSegmentRequest, token: str) -> List[SegmentResponse]:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        await validate_text_exits(text_id=create_segment_request.text_id)
        new_segment = await create_segment(create_segment_request=create_segment_request)
        return [
            SegmentResponse(
                id=str(segment.id),
                text_id=segment.text_id,
                content=segment.content,
                mapping=segment.mapping
            )
            for segment in new_segment
        ]
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

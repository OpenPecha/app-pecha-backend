from .segments_repository import create_segment
from .segments_response_models import CreateSegmentRequest, SegmentResponse
from ...constants import valid_text
from fastapi import HTTPException
from starlette import status

from typing import List

from ...users.users_service import verify_admin_access

async def create_new_segment(create_segment_request: CreateSegmentRequest, token: str) -> List[SegmentResponse]:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        is_valid_text = await valid_text(text_id=create_segment_request.text_id)
        if not is_valid_text:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Text not found")
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
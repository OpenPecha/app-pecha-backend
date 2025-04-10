import uuid
from typing import List, Optional

from fastapi import HTTPException
from starlette import status

from pecha_api.error_contants import ErrorConstants
from .mappings_repository import update_mapping
from .mappings_response_models import TextMappingRequest, MappingsModel
from ..segments.segments_response_models import SegmentResponse, MappingResponse
from ..segments.segments_service import validate_segments_exists, validate_segment_exists
from ..texts_utils import TextUtils
from pecha_api.users.users_service import verify_admin_access
from ..segments.segments_models import Mapping, Segment


async def update_segment_mapping(text_mapping_request: TextMappingRequest, token: str) -> SegmentResponse:
    # validate if the user is admin or not
    is_admin = verify_admin_access(token=token)
    if is_admin:
        # validate the text id
        await validate_request_info(
            text_id=text_mapping_request.text_id,
            segment_id=text_mapping_request.segment_id,
            mappings=text_mapping_request.mappings
        )
        # save the text_mapping
        mappings = [Mapping(text_id=mapping_model.parent_text_id, segments=mapping_model.segments) for mapping_model in
                    text_mapping_request.mappings]
        updated_segment: Optional[Segment] = await update_mapping(
            text_id=text_mapping_request.text_id,
            segment_id=uuid.UUID(text_mapping_request.segment_id),
            mappings=mappings
        )
        if updated_segment:
            mapping_responses: List[MappingResponse] = [
                MappingResponse(**mapping.model_dump()) for mapping in updated_segment.mapping
            ]
            return SegmentResponse(
                id=str(updated_segment.id),
                text_id=updated_segment.text_id,
                content=updated_segment.content,
                mapping=mapping_responses
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.SEGMENT_MAPPING_ERROR_MESSAGE)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.ADMIN_ERROR_MESSAGE)


async def validate_request_info(text_id: str, segment_id: str, mappings: List[MappingsModel]) -> bool:
    # validate the text id
    await TextUtils.validate_text_exists(text_id=text_id)
    # validate the segment id
    await validate_segment_exists(segment_id=segment_id)
    # validate the parent ids
    parent_text_ids = [mapping.parent_text_id for mapping in mappings]
    if text_id in parent_text_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.SAME_TEXT_MAPPING_ERROR_MESSAGE)
    await TextUtils.validate_texts_exist(text_ids=parent_text_ids)
    # validate segment ids
    segment_ids = [segment for mapping in mappings for segment in mapping.segments]
    await validate_segments_exists(segment_ids=segment_ids)
    return True


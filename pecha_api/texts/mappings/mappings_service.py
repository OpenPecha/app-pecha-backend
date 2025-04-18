import asyncio
from typing import List

from fastapi import HTTPException
from starlette import status

from pecha_api.error_contants import ErrorConstants
from .mappings_repository import update_mappings
from .mappings_response_models import TextMappingRequest, MappingsModel
from ..segments.segments_response_models import SegmentResponse, SegmentDTO, MappingResponse
from ..segments.segments_utils import SegmentUtils
from ..texts_utils import TextUtils
from pecha_api.users.users_service import verify_admin_access


async def update_segment_mapping(text_mapping_request: TextMappingRequest, token: str) -> SegmentResponse:
    # validate if the user is admin or not
    is_admin = verify_admin_access(token=token)
    if is_admin:
        # validate the text id
        await validate_mapping_request(
           text_mapping_request=text_mapping_request
        )
        updated_segments = await update_mappings(text_mappings=text_mapping_request.text_mappings)
        if updated_segments:
            # Convert all segments to SegementDTO
            segment_dtos = [
                SegmentDTO(
                    id=str(segment.id),
                    text_id=segment.text_id,
                    content=segment.content,
                    mapping=[MappingResponse(**mapping.model_dump()) for mapping in segment.mapping]
                ) for segment in updated_segments
            ]
            return SegmentResponse(segments=segment_dtos)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.SEGMENT_MAPPING_ERROR_MESSAGE)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.ADMIN_ERROR_MESSAGE)

async def validate_mapping_request(text_mapping_request: TextMappingRequest) -> bool:
    tasks = [
        asyncio.create_task(validate_request_info(
            text_id=tm.text_id,
            segment_id=tm.segment_id,
            mappings=tm.mappings
        )) for tm in text_mapping_request.text_mappings
    ]
    try:
        for completed in asyncio.as_completed(tasks):
            result = await completed
            if not result:
                # Cancel all other running tasks
                for task in tasks:
                    if not task.done():
                        task.cancel()
                return False
    except asyncio.CancelledError:
        pass

    return True

async def validate_request_info(text_id: str, segment_id: str, mappings: List[MappingsModel]) -> bool:
    # validate the text id
    await TextUtils.validate_text_exists(text_id=text_id)
    # validate the segment id
    await SegmentUtils.validate_segment_exists(segment_id=segment_id)
    # validate the parent ids
    parent_text_ids = [mapping.parent_text_id for mapping in mappings]
    if text_id in parent_text_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.SAME_TEXT_MAPPING_ERROR_MESSAGE)
    await TextUtils.validate_texts_exist(text_ids=parent_text_ids)
    # validate segment ids
    segment_ids = [segment for mapping in mappings for segment in mapping.segments]
    await SegmentUtils.validate_segments_exists(segment_ids=segment_ids)
    return True


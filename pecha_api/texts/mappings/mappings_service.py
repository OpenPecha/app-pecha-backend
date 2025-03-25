import uuid
from typing import List

from fastapi import HTTPException
from starlette import status

from texts.mappings.mappings_repository import update_mapping
from texts.mappings.mappings_response_models import TextMappingRequest, MappingsModel
from texts.segments.segments_response_models import SegmentResponse
from texts.segments.segments_service import validate_segments_exists, validate_segment_exists
from texts.texts_service import validate_text_exits, validate_texts_exits
from users.users_service import verify_admin_access
from texts.segments.segments_models import Mapping, Segment


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
        updated_segment: Segment = await update_mapping(
            text_id=text_mapping_request.text_id,
            segment_id=uuid.UUID(text_mapping_request.segment_id),
            mappings=mappings
        )
        return SegmentResponse(
            id=str(updated_segment.id),
            text_id=updated_segment.text_id,
            content=updated_segment.content,
            mapping=updated_segment.mapping
        )

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


async def validate_request_info(text_id: str, segment_id: str, mappings: List[MappingsModel]):
    # validate the text id
    await validate_text_exits(text_id=text_id)
    # validate the segment id
    await validate_segment_exists(segment_id=segment_id)
    # validate the parent ids
    parent_text_ids = [mapping.parent_text_id for mapping in mappings]
    await validate_texts_exits(text_ids=parent_text_ids)
    # validate segment ids
    segment_ids = [segment for mapping in mappings for segment in mapping.segments]
    await validate_segments_exists(segment_ids=segment_ids)


from pecha_api.error_contants import ErrorConstants
from .segments_repository import create_segment, get_segment_by_id, get_related_mapped_segments
from .segments_response_models import CreateSegmentRequest, SegmentResponse, MappingResponse, SegmentDTO, \
    SegmentInfosResponse
from fastapi import HTTPException
from starlette import status

from .segments_utils import SegmentUtils
from ..texts_utils import TextUtils

from typing import List

from .segments_response_models import SegmentTranslationsResponse, ParentSegment, SegmentCommentariesResponse, \
    RelatedText, Resources, SegmentInfos
from ...users.users_service import verify_admin_access


async def get_segment_details_by_id(segment_id: str) -> SegmentDTO:
    segment = await get_segment_by_id(segment_id=segment_id)
    if not segment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
    mapping_responses: List[MappingResponse] = [
        MappingResponse(**mapping.model_dump()) for mapping in segment.mapping
    ]
    return SegmentDTO(
        id=str(segment.id),
        text_id=segment.text_id,
        content=segment.content,
        mapping=mapping_responses
    )

async def create_new_segment(create_segment_request: CreateSegmentRequest, token: str) -> SegmentResponse:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        await TextUtils.validate_text_exists(text_id=create_segment_request.text_id)
        new_segment = await create_segment(create_segment_request=create_segment_request)
        segments =  [
            SegmentDTO(
                id=str(segment.id),
                text_id=segment.text_id,
                content=segment.content,
                mapping= [MappingResponse(**mapping.model_dump()) for mapping in segment.mapping]
            )
            for segment in new_segment
        ]
        return SegmentResponse(segments=segments)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.ADMIN_ERROR_MESSAGE)

async def get_translations_by_segment_id(segment_id: str) -> SegmentTranslationsResponse:
    """
    Get translations for a given segment ID.
    """
    is_valid_segment = await SegmentUtils.validate_segment_exists(segment_id=segment_id)
    if not is_valid_segment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
    parent_segment = await get_segment_by_id(segment_id=segment_id)
    mapped_segments = await get_related_mapped_segments(parent_segment_id=segment_id)
    translations = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(segments=mapped_segments, type="version")
    return SegmentTranslationsResponse(
        parent_segment=ParentSegment(
            segment_id=str(parent_segment.id),
            content=parent_segment.content
        ),
        translations=translations
    )

async def get_commentaries_by_segment_id(
        segment_id: str
) -> SegmentCommentariesResponse:
    """"
       Get commentaries for a given segment ID.
    """
    is_valid_segment = await SegmentUtils.validate_segment_exists(segment_id=segment_id)
    if not is_valid_segment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
    parent_segment = await get_segment_by_id(segment_id=segment_id)
    mapped_segments = await get_related_mapped_segments(parent_segment_id=segment_id)
    commentaries = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(segments=mapped_segments, type="commentary")
    return SegmentCommentariesResponse(
        parent_segment=ParentSegment(
            segment_id=segment_id,
            content=parent_segment.content
        ),
        commentaries=commentaries
    )

async def get_infos_by_segment_id(segment_id: str) -> SegmentInfosResponse:
    is_valid_segment = await SegmentUtils.validate_segment_exists(segment_id=segment_id)
    if not is_valid_segment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
    mapped_segments = await get_related_mapped_segments(parent_segment_id=segment_id)
    counts = await SegmentUtils.get_count_of_each_commentary_and_version(mapped_segments)
    return SegmentInfosResponse(
        segment_infos= SegmentInfos(
            segment_id=segment_id,
            translations=counts["version"],
            related_text=RelatedText(
                commentaries=counts["commentary"]
            ),
            resources=Resources(
                sheets=0
            )
        )
    ) 
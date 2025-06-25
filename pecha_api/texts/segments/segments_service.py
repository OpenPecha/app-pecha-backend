from pecha_api.error_contants import ErrorConstants

from .segments_repository import (
    create_segment,
    get_segment_by_id, 
    get_related_mapped_segments,
    get_segments_by_text_id,
    delete_segments_by_text_id
)

from .segments_response_models import (
    CreateSegmentRequest, 
    SegmentResponse, 
    MappingResponse, 
    SegmentDTO, 
    SegmentInfoResponse,
    SegmentRootMappingResponse
)

from fastapi import HTTPException
from starlette import status

from .segments_utils import SegmentUtils
from ..texts_utils import TextUtils

from typing import List

from .segments_response_models import (
    SegmentTranslationsResponse, 
    ParentSegment, 
    SegmentCommentariesResponse,
    RelatedText, 
    Resources, 
    SegmentInfo, 
    SegmentRootMappingResponse
)

from ...users.users_service import validate_user_exists


async def get_segment_details_by_id(segment_id: str, text_details: bool = False) -> SegmentDTO:
    segment = await get_segment_by_id(segment_id=segment_id)
    if not segment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
    mapping_responses: List[MappingResponse] = [
        MappingResponse(**mapping.model_dump()) for mapping in segment.mapping
    ]
    text = None
    if text_details:
        text = await TextUtils.get_text_details_by_id(text_id=segment.text_id)
    return SegmentDTO(
        id=str(segment.id),
        text_id=segment.text_id,
        content=segment.content,
        mapping=mapping_responses,
        type=segment.type,
        text=text
    )

async def create_new_segment(create_segment_request: CreateSegmentRequest, token: str) -> SegmentResponse:
    is_valid_user = validate_user_exists(token=token)
    if is_valid_user:
        await TextUtils.validate_text_exists(text_id=create_segment_request.text_id)
        new_segment = await create_segment(create_segment_request=create_segment_request)
        segments =  [
            SegmentDTO(
                id=str(segment.id),
                text_id=segment.text_id,
                content=segment.content,
                mapping= [MappingResponse(**mapping.model_dump()) for mapping in segment.mapping],
                type=segment.type
            )
            for segment in new_segment
        ]
        return SegmentResponse(segments=segments)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)

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

async def get_infos_by_segment_id(segment_id: str) -> SegmentInfoResponse:
    is_valid_segment = await SegmentUtils.validate_segment_exists(segment_id=segment_id)
    if not is_valid_segment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
    mapped_segments = await get_related_mapped_segments(parent_segment_id=segment_id)
    counts = await SegmentUtils.get_count_of_each_commentary_and_version(mapped_segments)
    segment_root_mapping_count = await SegmentUtils.get_root_mapping_count(segment_id=segment_id)
    return SegmentInfoResponse(
        segment_info= SegmentInfo(
            segment_id=segment_id,
            translations=counts["version"],
            related_text=RelatedText(
                commentaries=counts["commentary"],
                root_text=segment_root_mapping_count
            ),
            resources=Resources(
                sheets=0
            )
        )
    ) 

async def get_root_text_mapping_by_segment_id(segment_id: str) -> SegmentRootMappingResponse:
    is_valid_segment = await SegmentUtils.validate_segment_exists(segment_id=segment_id)
    if not is_valid_segment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
    segment = await get_segment_by_id(segment_id=segment_id)
    segment_root_mapping = await SegmentUtils.get_segment_root_mapping_details(segment=segment)
    return SegmentRootMappingResponse(
        parent_segment=ParentSegment(
            segment_id=segment_id,
            content=segment.content
        ),
        segment_root_mapping=segment_root_mapping
    )
    
async def fetch_segments_by_text_id(text_id: str) -> List[SegmentDTO]:
    segments = await get_segments_by_text_id(text_id=text_id)
    return segments

async def remove_segments_by_text_id(text_id: str):
    is_valid_text = await TextUtils.validate_text_exists(text_id=text_id)
    if not is_valid_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    return await delete_segments_by_text_id(text_id=text_id)
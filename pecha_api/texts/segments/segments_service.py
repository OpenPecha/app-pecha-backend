from uuid import UUID

from pecha_api.error_contants import ErrorConstants
from .segments_repository import create_segment, check_segment_exists, check_all_segment_exists, get_segment_by_id
from .segments_response_models import CreateSegmentRequest, SegmentResponse, MappingResponse
from fastapi import HTTPException
from starlette import status

from typing import List

from .segments_repository import get_translations, get_commentaries

from .segments_response_models import SegmentTranslationsResponse, ParentSegment, SegmentCommentariesResponse
from ..texts_service import validate_text_exits
from ...users.users_service import verify_admin_access


async def validate_segment_exists(segment_id: str):
    uuid_segment_id = UUID(segment_id)
    is_exists = await check_segment_exists(segment_id=uuid_segment_id)
    if not is_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
    return is_exists

async def validate_segments_exists(segment_ids: List[str]):
    uuid_segment_ids = [UUID(segment_id) for segment_id in segment_ids]
    all_exists = await check_all_segment_exists(segment_ids=uuid_segment_ids)
    if not all_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
    return all_exists

async def get_segment_by_segment_id(segment_id: str) -> SegmentResponse:
    segment_details = await get_segment_by_id(segment_id=segment_id)
    if not segment_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
    return SegmentResponse(
        id=str(segment_details.id),
        text_id=segment_details.text_id,
        content=segment_details.content,
        mapping=segment_details.mapping
    )

async def get_segment_details_by_id(segment_id: str) -> SegmentResponse:
    segment = await get_segment_by_id(segment_id=segment_id)
    if not segment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
    mapping_responses: List[MappingResponse] = [
        MappingResponse(**mapping.model_dump()) for mapping in segment.mapping
    ]
    return SegmentResponse(
        id=str(segment.id),
        text_id=segment.text_id,
        content=segment.content,
        mapping=mapping_responses
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
                mapping= [MappingResponse(**mapping.model_dump()) for mapping in segment.mapping]
            )
            for segment in new_segment
        ]
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.ADMIN_ERROR_MESSAGE)

async def get_translations_by_segment_id(
        segment_id: str
) -> SegmentTranslationsResponse:
    """
    Get translations for a given segment ID.
    """
    segment = await get_segment_by_id(segment_id=segment_id)
    if not segment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
    translations = await get_translations(segment_id=segment_id)
    return SegmentTranslationsResponse(
        parent_segment=ParentSegment(
            segment_id=segment_id,
            segment_number=1,
            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།"
        ),
        translations=translations
    )

async def get_commentaries_by_segment_id(
        segment_id: str
) -> SegmentCommentariesResponse:
    """"
       Get commentaries for a given segment ID.
    """
    segment = await get_segment_by_id(segment_id=segment_id)
    if not segment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
    commentaries = await get_commentaries(segment_id=segment_id)
    return SegmentCommentariesResponse(
        parent_segment=ParentSegment(
            segment_id=segment_id,
            segment_number=1,
            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།"
        ),
        commentaries=commentaries
    )
from typing import Dict, List
from uuid import UUID

from fastapi import HTTPException
from starlette import status

from pecha_api.error_contants import ErrorConstants
from .segments_response_models import SegmentDTO, SegmentTranslation, SegmentCommentry
from .segments_repository import check_segment_exists, check_all_segment_exists
from ..texts_utils import TextUtils

class SegmentUtils:
    """
    Utility class for segment-related operations.
    """
    
    @staticmethod
    async def validate_segment_exists(segment_id: str):
        uuid_segment_id = UUID(segment_id)
        is_exists = await check_segment_exists(segment_id=uuid_segment_id)
        if not is_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
        return is_exists
    
    @staticmethod
    async def validate_segments_exists(segment_ids: List[str]):
        uuid_segment_ids = [UUID(segment_id) for segment_id in segment_ids]
        all_exists = await check_all_segment_exists(segment_ids=uuid_segment_ids)
        if not all_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
        return all_exists
        
    @staticmethod
    async def get_count_of_each_commentary_and_version(segments: List[SegmentDTO]) -> Dict[str, int]:
        count = {
            "commentary": 0,
            "version": 0
        }
        text_ids = [segment.text_id for segment in segments]
        text_details = await TextUtils.get_text_details_by_ids(text_ids=text_ids)
        text_details_dict = {text_detail.id: text_detail for text_detail in text_details}
        for segment in segments:
            text_detail = text_details_dict.get(segment.text_id)
            if text_detail.type == "commentary":
                count["commentary"] += 1
            elif text_detail.type == "version":
                count["version"] += 1
        return count

    @staticmethod
    async def filter_segment_mapping_by_type(segments: List[SegmentDTO], type: str) -> List[SegmentDTO]:
        text_ids = [segment.text_id for segment in segments]
        text_details = await TextUtils.get_text_details_by_ids(text_ids=text_ids)
        text_details_dict = {text_detail.id: text_detail for text_detail in text_details}
        filtered_segments = []
        for segment in segments:
            text_detail = text_details_dict.get(segment.text_id)
            if text_detail.type == "version" and type == "version":
                filtered_segments.append(
                    SegmentTranslation(
                        text_id=segment.text_id,
                        title=text_detail.title,
                        source=text_detail.published_by,
                        language=text_detail.language,
                        content=segment.content
                    )
                )
            elif text_detail.type == "commentary" and type == "commentary":
                filtered_segments.append(
                    SegmentCommentry(
                        text_id=segment.text_id,
                        title=text_detail.title,
                        content=segment.content,
                        language=text_detail.language,
                        count=1
                    )
                )
        return filtered_segments
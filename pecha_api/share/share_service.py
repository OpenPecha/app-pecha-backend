from fastapi import HTTPException
from pecha_api.error_contants import ErrorConstants

from ..texts.segments.segments_service import get_segment_details_by_id
from ..texts.segments.segments_utils import SegmentUtils
from starlette import status
from starlette.responses import StreamingResponse

from .share_response_models import (
    ImageGenerationRequest
)

async def generate_image(image_generation_request: ImageGenerationRequest):
    segment_id = image_generation_request.segment_id
    if segment_id is not None:
        is_valid_segment = await SegmentUtils.validate_segment_exists(segment_id=segment_id)
        if not is_valid_segment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
        segment = await get_segment_details_by_id(segment_id=segment_id)

        cleaned_content = ShareUtils.clean_html(segment.content)
        image_bytes = ShareUtils.create_image_bytes(cleaned_content)
        
        return StreamingResponse(image_bytes, media_type="image/png")
        

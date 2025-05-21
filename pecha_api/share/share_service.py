from fastapi import HTTPException
from pecha_api.error_contants import ErrorConstants
import subprocess

from ..texts.segments.segments_service import get_segment_details_by_id
from ..texts.segments.segments_utils import SegmentUtils
from starlette import status
from starlette.responses import StreamingResponse
from .share_utils import ShareUtils
from ..texts.texts_utils import TextUtils

async def generate_image(segment_id: str, language: str):
    if segment_id is not None and segment_id != "":
        is_valid_segment = await SegmentUtils.validate_segment_exists(segment_id=segment_id)
        if not is_valid_segment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
        segment = await get_segment_details_by_id(segment_id=segment_id)

        text_id = segment.text_id
        text_detail = await TextUtils.get_text_detail_by_id(text_id=text_id)

        segment_text = segment.content
        reference_text = text_detail.title

        language = text_detail.language


        subprocess.run(["python3", "pecha_api/share/pecha_text_image.py"], check=True)
        
        return StreamingResponse(image_bytes, media_type="image/png")
    else:
        image_bytes = ShareUtils.create_image_bytes("PECHA", language=language)

        return StreamingResponse(image_bytes, media_type="image/png")
        

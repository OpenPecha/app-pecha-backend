import logging
from fastapi import HTTPException
from starlette import status
import io
from pecha_api.error_contants import ErrorConstants
from ..texts.segments.segments_utils import SegmentUtils
from starlette.responses import StreamingResponse
from ..texts.texts_utils import TextUtils
from .pecha_text_image_generator import generate_text_image
from ..texts.segments.segments_service import get_segment_details_by_id

async def generate_image(segment_id: str, language: str):
    try:
        is_valid_segment = await SegmentUtils.validate_segment_exists(segment_id=segment_id)
        if not is_valid_segment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
        segment = await get_segment_details_by_id(segment_id=segment_id)

        text_id = segment.text_id
        text_detail = await TextUtils.get_text_detail_by_id(text_id=text_id)

        segment_text = segment.content
        reference_text = text_detail.title
        language = text_detail.language

        generate_text_image(text=segment_text, ref_str=reference_text, lang=language, version_lang=language, logo_path="pecha_api/share/static/img/pecha-logo.png")
        
    except Exception as e:
        logging.error(e)
        generate_text_image(text=None, ref_str=None, lang=None, version_lang=None, logo_path="pecha_api/share/static/img/pecha-logo.png")
        
    image_path = "pecha_api/share/static/img/output.png"
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")

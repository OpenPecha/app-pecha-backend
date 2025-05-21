from fastapi import HTTPException
from pecha_api.error_contants import ErrorConstants
import subprocess
import io
import os

from ..texts.segments.segments_service import get_segment_details_by_id
from ..texts.segments.segments_utils import SegmentUtils
from starlette import status
from starlette.responses import StreamingResponse
from .share_utils import ShareUtils
from ..texts.texts_utils import TextUtils
from .pecha_text_image import create_synthetic_data

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

        env = os.environ.copy()
        env["SEGMENT_TEXT"] = segment_text
        env["REFERENCE_TEXT"] = reference_text
        env["LANGUAGE"] = language

        create_synthetic_data(segment_text, reference_text, language, language, logo_path="pecha_api/share/static/img/pecha-logo.png")

    
        # subprocess.run(
        #     # add /usr/local/bin/python3 if using MAC_OS
        #     ["/usr/bin/python3", "pecha_api/share/pecha_text_image.py"],
        #     env=env,
        #     check=True
        # )
        
        image_path = "pecha_api/share/static/img/output.png"
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()

        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")

    else:
        image_bytes = ShareUtils.create_image_bytes("PECHA", language=language)

        return StreamingResponse(image_bytes, media_type="image/png")
        

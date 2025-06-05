import logging
import httpx
from fastapi import HTTPException, Response
from starlette import status
from http import HTTPStatus
import io
from pecha_api.error_contants import ErrorConstants
from pecha_api.texts.segments.segments_utils import SegmentUtils
from starlette.responses import StreamingResponse
from pecha_api.texts.texts_utils import TextUtils
from .pecha_text_image_generator import generate_segment_image
from pecha_api.texts.segments.segments_service import get_segment_details_by_id
from pecha_api.config import get

from pecha_api.share.share_response_models import (
    ShareRequest,
    ShortUrlResponse
)
from .short_url_service import _get_short_url_

from pecha_api.error_contants import ErrorConstants

LOGO_PATH = "pecha_api/share/static/img/pecha-logo.png"
IMAGE_PATH = "pecha_api/share/static/img/output.png"
MEDIA_TYPE = "image/png"
DEFAULT_OG_DESCRIPTION = "PECHA"

async def get_generated_image(segment_id: str):
    try:    
        image_path = IMAGE_PATH
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()

        return StreamingResponse(io.BytesIO(image_bytes), media_type=MEDIA_TYPE)
    
    except HTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=ErrorConstants.IMAGE_NOT_FOUND_MESSAGE
        )



async def generate_short_url(share_request: ShareRequest) -> ShortUrlResponse:

    og_description = ""
    if share_request.logo:
        og_description = DEFAULT_OG_DESCRIPTION
        generate_segment_image(
            text=None, 
            ref_str=None, 
            lang=None, 
            text_color=share_request.text_color, 
            bg_color=share_request.bg_color, 
            logo_path=LOGO_PATH
        )

    else:
        await SegmentUtils.validate_segment_exists(segment_id=share_request.segment_id)

        segment = await get_segment_details_by_id(segment_id=share_request.segment_id)

        text_id = segment.text_id
        text_detail = await TextUtils.get_text_detail_by_id(text_id=text_id)

        og_description = text_detail.title

        segment_text = segment.content
        reference_text = text_detail.title
        language = text_detail.language

        generate_segment_image(
            text=segment_text, 
            ref_str=reference_text, 
            lang=language, 
            text_color=share_request.text_color, 
            bg_color=share_request.bg_color, 
            logo_path=LOGO_PATH
        )
        
    
    payload = _generate_short_url_payload_(share_request=share_request, og_description=og_description)
    
    short_url: ShortUrlResponse = await _get_short_url_(payload=payload)

    return short_url


def _generate_short_url_payload_(share_request: ShareRequest, og_description: str) -> dict:

    pecha_backend_endpoint = get("PECHA_BACKEND_ENDPOINT")
    image_url = f"{pecha_backend_endpoint}/share/image?segment_id={share_request.segment_id}&language={share_request.language}&logo={share_request.logo}"
    payload = {
        "url": share_request.url,
        "og_title": DEFAULT_OG_DESCRIPTION,
        "og_description": og_description,
        "og_image": image_url,
        "tags": share_request.tags
    }
    return payload



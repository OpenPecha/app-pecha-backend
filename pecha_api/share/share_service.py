from fastapi import HTTPException
import io
from pecha_api.error_contants import ErrorConstants
from pecha_api.texts.segments.segments_utils import SegmentUtils
from starlette.responses import StreamingResponse
from pecha_api.texts.texts_utils import TextUtils
from .pecha_text_image_generator import generate_segment_image
from pecha_api.texts.segments.segments_service import get_segment_details_by_id
from pecha_api.config import get
import anyio

from pecha_api.share.share_response_models import (
    ShareRequest,
    ShortUrlResponse
)

from pecha_api.short_url.short_url_service import get_short_url

from pecha_api.error_contants import ErrorConstants

LOGO_PATH = "pecha_api/share/static/img/pecha-logo.png"
IMAGE_PATH = "pecha_api/share/static/img/output.png"
MEDIA_TYPE = "image/png"
DEFAULT_OG_TITLE = "PECHA"
DEFAULT_OG_DESCRIPTION = "PECHA"
PECHA_FRONTEND_ENDPOINT = "https://pecha-frontend-12552055234-4f99e0e.onrender.com/texts/text-details"

async def get_generated_image():
    try:    
        image_path = IMAGE_PATH
        async with await anyio.open_file(image_path, "rb") as file:
            image_bytes = await file.read()

        return StreamingResponse(io.BytesIO(image_bytes), media_type=MEDIA_TYPE)
    
    except HTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=ErrorConstants.IMAGE_NOT_FOUND_MESSAGE
        )

async def generate_short_url(share_request: ShareRequest) -> ShortUrlResponse:

    og_description = DEFAULT_OG_DESCRIPTION
    if share_request.logo:
        _generate_logo_image_(share_request=share_request)

    else:
        await _generate_segment_content_image_(share_request=share_request)
        
    payload = _generate_short_url_payload_(share_request=share_request, og_description=og_description)
    
    short_url: ShortUrlResponse = await get_short_url(payload=payload)

    return short_url



def _generate_logo_image_(share_request: ShareRequest):
    generate_segment_image(
        text_color=share_request.text_color, 
        bg_color=share_request.bg_color, 
        logo_path=LOGO_PATH
    )

async def _generate_segment_content_image_(share_request: ShareRequest):

    await SegmentUtils.validate_segment_exists(segment_id=share_request.segment_id)

    segment = await get_segment_details_by_id(segment_id=share_request.segment_id)

    text_id = segment.text_id
    text_detail = await TextUtils.get_text_detail_by_id(text_id=text_id)

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


def _generate_short_url_payload_(share_request: ShareRequest, og_description: str) -> dict:

    if share_request.url is None:
        share_request.url = _generate_url_(
            segment_id=share_request.segment_id,
            content_id=share_request.content_id,
            text_id=share_request.text_id,
            content_index=share_request.content_index,
        )

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

def _generate_url_(
        segment_id: str,
        content_id: str,
        text_id: str,
        content_index: int
) -> str:
    return f"{PECHA_FRONTEND_ENDPOINT}?segment_id={segment_id}&content_id={content_id}&text_id={text_id}&content_index={content_index}"

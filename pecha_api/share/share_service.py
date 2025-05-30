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
from .pecha_text_image_generator import generate_text_image
from pecha_api.texts.segments.segments_service import get_segment_details_by_id
from pecha_api.config import get

from pecha_api.share.share_response_models import (
    ShareRequest,
    ShortUrlResponse
)

async def get_generated_image(segment_id: str):
    try:    
        image_path = "pecha_api/share/static/img/output.png"
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()

        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")
    except Exception as e:
        logging.error(e)
        return StreamingResponse(io.BytesIO(), media_type="image/png")



async def get_short_url(share_request: ShareRequest) -> ShortUrlResponse:

    og_description = ""
    try:
        is_valid_segment = await SegmentUtils.validate_segment_exists(segment_id=share_request.segment_id)
        if not is_valid_segment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
        segment = await get_segment_details_by_id(segment_id=share_request.segment_id)

        text_id = segment.text_id
        text_detail = await TextUtils.get_text_detail_by_id(text_id=text_id)

        og_description = text_detail.title

        segment_text = segment.content
        reference_text = text_detail.title
        language = text_detail.language

        generate_text_image(text=segment_text, ref_str=reference_text, lang=language, text_color=share_request.text_color, bg_color=share_request.bg_color, logo_path="pecha_api/share/static/img/pecha-logo.png")
        
    except Exception as e:
        logging.error(e)
        og_description = "PECHA"
        generate_text_image(text=None, ref_str=None, lang=None, text_color=share_request.text_color, bg_color=share_request.bg_color, logo_path="pecha_api/share/static/img/pecha-logo.png")


    short_url_endpoint = get("SHORT_URL_GENERATION_ENDPOINT")
    pecha_backend_endpoint = get("PECHA_BACKEND_ENDPOINT")
    url = f"{short_url_endpoint}/shorten"
    image_url = f"{pecha_backend_endpoint}/share/image?segment_id={share_request.segment_id}&language={share_request.language}"
    payload = {
        "url": share_request.url,
        "og_title": "PECHA",
        "og_description": og_description,
        "og_image": image_url,
        "tags": share_request.tags
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code == HTTPStatus.CREATED:
            response = response.json()
            short_url = response["short_url"]
            return ShortUrlResponse(
                shortUrl=short_url
            )
        else:
            # Pass through the exact response from the server
            return Response(content=response.content, status_code=response.status_code, media_type=response.headers.get('content-type', 'application/json'))
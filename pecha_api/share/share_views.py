from fastapi import APIRouter, Depends, Query
from starlette import status
from typing import Optional

from .share_response_models import (
    ShareRequest,
    ShortUrlResponse
)

from .share_service import (
    get_generated_image,
    get_short_url
)

share_router = APIRouter(
    prefix="/share",
    tags=["Share"]
)

@share_router.get("/image", status_code=status.HTTP_200_OK)
async def get_image(
    segment_id: Optional[str] = Query(default=None)
):
    return await get_generated_image(segment_id=segment_id)

@share_router.post("", status_code=status.HTTP_200_OK)
async def share(share_request: ShareRequest) -> ShortUrlResponse:
    return await get_short_url(share_request=share_request)
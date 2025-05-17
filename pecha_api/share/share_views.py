from fastapi import APIRouter, Depends, Query
from starlette import status
from typing import Optional

from .share_response_models import (
    ImageGenerationRequest
)

from .share_service import (
    generate_image
)

share_router = APIRouter(
    prefix="/share",
    tags=["Share"]
)

@share_router.get("/image/", status_code=status.HTTP_200_OK)
async def image_generation(
    segment_id: Optional[str] = Query(default=None),
    language: Optional[str] = Query(default="en")
):
    return await generate_image(segment_id=segment_id, language=language)
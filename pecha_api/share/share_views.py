from fastapi import APIRouter, Depends, Query
from starlette import status

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

@share_router.post("/image/", status_code=status.HTTP_200_OK)
async def image_generation(
    image_generation_request: ImageGenerationRequest
):
    return await generate_image(image_generation_request=image_generation_request)
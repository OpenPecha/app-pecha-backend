from fastapi import APIRouter
from fastapi.security import HTTPBearer
from starlette import status

from .texts_service import get_text_by_term, create_new_text, create_new_segment
from .texts_response_models import CreateTextRequest, CreateSegmentRequest

oauth2_scheme = HTTPBearer()
text_router = APIRouter(
    prefix="/texts",
    tags=["Texts"]
)


@text_router.get("", status_code=status.HTTP_200_OK)
def get_text(language: str | None):
    return get_text_by_term(language=language)

@text_router.post("", status_code=status.HTTP_201_CREATED)
async def create_text(create_text_request: CreateTextRequest):
    return await create_new_text(create_text_request=create_text_request)

@text_router.post("/{text_id}/segment", status_code=status.HTTP_201_CREATED)
async def create_segment(text_id: str, create_segment_request: CreateSegmentRequest):
    return await create_new_segment(text_id=text_id, create_segment_request=create_segment_request)



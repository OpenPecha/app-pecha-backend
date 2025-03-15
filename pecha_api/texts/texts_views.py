from fastapi import APIRouter, Query
from typing import Optional
from fastapi.security import HTTPBearer
from starlette import status


from .texts_service import create_new_text, create_new_segment, get_text_by_term_or_category
from .texts_response_models import CreateTextRequest, CreateSegmentRequest

oauth2_scheme = HTTPBearer()
text_router = APIRouter(
    prefix="/texts",
    tags=["Texts"]
)


@text_router.get("", status_code=status.HTTP_200_OK)
def get_text(
    category: Optional[str]= Query(default=None),
    language: str = Query(default=None),
    skip: int= Query(default=0),
    limit: int= Query(default=10)
):
    return get_text_by_term_or_category(category=category, language=language, skip=skip, limit=limit)

@text_router.post("", status_code=status.HTTP_201_CREATED)
async def create_text(create_text_request: CreateTextRequest):
    return await create_new_text(create_text_request=create_text_request)

@text_router.post("/segment", status_code=status.HTTP_201_CREATED)
async def create_segment(create_segment_request: CreateSegmentRequest):
    return await create_new_segment(create_segment_request=create_segment_request)






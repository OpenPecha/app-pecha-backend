from fastapi import APIRouter, Query
from typing import Optional
from fastapi.security import HTTPBearer
from starlette import status

from .texts_service import get_text_by_term, get_text_by_category

oauth2_scheme = HTTPBearer()
text_router = APIRouter(
    prefix="/texts",
    tags=["Texts"]
)


@text_router.get("", status_code=status.HTTP_200_OK)
def get_text(language: str | None):
    return get_text_by_term(language=language)

@text_router.get("/category", status_code=status.HTTP_200_OK)
async def get_text(
    category: str= Query(default=None),
    language: str= Query(default=None),
    skip: int= Query(default=0),
    limit: int= Query(default=10)
):
    return await get_text_by_category(category=category, language=language, skip=skip, limit=limit)
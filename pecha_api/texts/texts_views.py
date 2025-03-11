from fastapi import APIRouter, Query
from fastapi.security import HTTPBearer
from starlette import status

from .texts_service import get_text_by_term, get_contents_by_text_id, get_version_by_text_id

oauth2_scheme = HTTPBearer()
text_router = APIRouter(
    prefix="/texts",
    tags=["Texts"]
)


@text_router.get("", status_code=status.HTTP_200_OK)
def get_text(language: str | None):
    return get_text_by_term(language=language)

@text_router.get("/{text_id}/contents", status_code=status.HTTP_200_OK)
async def get_contents(
    text_id: str,
    skip: int = Query(default=0),
    limit: int = Query(default=10)
):
    return await get_contents_by_text_id(text_id=text_id, skip=skip, limit=limit)

@text_router.get("{text_id}/versions", status_code=status.HTTP_200_OK)
async def get_versions(
    text_id: str,
    skip: int = Query(default=0),
    limit: int= Query(default=10)
):
    return await get_version_by_text_id(text_id=text_id, skip=skip, limit=limit)
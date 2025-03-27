from fastapi import APIRouter, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from typing import Optional, Annotated

from .texts_service import get_contents_by_text_id, get_versions_by_text_id, create_new_text, get_text_by_term_or_category
from .texts_service import get_infos_by_text_id, get_texts_details_by_text_id
from .texts_response_models import CreateTextRequest, TextDetailsRequest

oauth2_scheme = HTTPBearer()
text_router = APIRouter(
    prefix="/texts",
    tags=["Texts"]
)


@text_router.get("", status_code=status.HTTP_200_OK)
async def get_text(
    text_id: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    language: str = Query(default=None),
    skip: int = Query(default=0),
    limit: int = Query(default=10)
):
    return await get_text_by_term_or_category(text_id=text_id, category=category, language=language, skip=skip, limit=limit)


@text_router.post("", status_code=status.HTTP_201_CREATED)
async def create_text(
    create_text_request: CreateTextRequest,
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
    ):
    return await create_new_text(
        create_text_request=create_text_request,
        token=authentication_credential.credentials
        )


@text_router.get("/{text_id}/contents", status_code=status.HTTP_200_OK)
async def get_contents(
        text_id: str,
        skip: int = Query(default=0),
        limit: int = Query(default=10)
):
    return await get_contents_by_text_id(text_id=text_id, skip=skip, limit=limit)


@text_router.post("/{text_id}/detals", status_code=status.HTTP_200_OK)
async def get_contents_with_details(
        text_id: str,
        text_details_request: TextDetailsRequest,
        skip: int = Query(default=0),
        limit: int = Query(default=100)
):
    return await get_texts_details_by_text_id(text_id=text_id, text_details_request=text_details_request, skip=skip, limit=limit)

@text_router.get("/{text_id}/versions", status_code=status.HTTP_200_OK)
async def get_versions(
        text_id: str,
        skip: int = Query(default=0),
        limit: int = Query(default=10)
):
    return await get_versions_by_text_id(text_id=text_id, skip=skip, limit=limit)

@text_router.get("/{text_id}/infos", status_code=status.HTTP_200_OK)
async def get_text_infos(
        text_id: str,
        language: str = Query(default=None),
        skip: int = Query(default=0),
        limit: int = Query(default=10)
):
    return await get_infos_by_text_id(text_id=text_id, language=language, skip=skip, limit=limit)


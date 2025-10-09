from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from pecha_api.plans.authors.plan_authors_response_models import AuthorInfoResponse, AuthorsResponse, AuthorInfoRequest
from pecha_api.plans.authors.plan_authors_service import get_selected_author_details, update_author_info
from pecha_api.plans.plans_response_models import PlansResponse
from pecha_api.plans.authors.plan_authors_service import get_plans_by_author,get_authors,get_author_details

oauth2_scheme = HTTPBearer()
author_router = APIRouter(
    prefix="/authors",
    tags=["Authors Profile"]
)

@author_router.get("", status_code=status.HTTP_200_OK)
async def get_all_authors()  -> AuthorsResponse:
    return await get_authors()

@author_router.get("/info", status_code=status.HTTP_200_OK)
async def get_author_information(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)])  -> AuthorInfoResponse:
    return await get_author_details(token=authentication_credential.credentials)

@author_router.post("/info", status_code=status.HTTP_201_CREATED)
async def update_author_information(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
                            author_info_request: AuthorInfoRequest):
    return await update_author_info(token=authentication_credential.credentials, author_info_request=author_info_request)

@author_router.get("/{author_id}", status_code=status.HTTP_200_OK)
async def get_author_information(author_id: UUID)  -> AuthorInfoResponse:
    return await get_selected_author_details(author_id=author_id)

@author_router.get("/{author_id}/plans", status_code=status.HTTP_200_OK)
async def get_plans_for_selected_author(author_id: UUID)  -> PlansResponse:
    return await get_plans_by_author(author_id=author_id)
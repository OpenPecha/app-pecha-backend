from uuid import UUID

from fastapi import APIRouter
from fastapi.security import HTTPBearer
from starlette import status

from pecha_api.plans.authors.plan_authors_response_models import AuthorInfoResponse,AuthorsResponse
from pecha_api.plans.authors.plan_authors_service import get_selected_author_details
from pecha_api.plans.plans_response_models import PlansResponse
from pecha_api.plans.authors.plan_authors_service import get_plans_by_author,get_authors

oauth2_scheme = HTTPBearer()
author_router = APIRouter(
    prefix="/authors",
    tags=["Authors Profile"]
)

@author_router.get("", status_code=status.HTTP_200_OK)
async def get_all_authors()  -> AuthorsResponse:
    return await get_authors()

@author_router.get("/{author_id}", status_code=status.HTTP_200_OK)
async def get_author_information(author_id: UUID)  -> AuthorInfoResponse:
    return await get_selected_author_details(author_id=author_id)

@author_router.get("/{author_id}/plans", status_code=status.HTTP_200_OK)
async def get_plans_for_selected_author(author_id: UUID)  -> PlansResponse:
    return await get_plans_by_author(author_id=author_id)
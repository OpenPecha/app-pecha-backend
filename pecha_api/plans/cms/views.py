from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import APIRouter, Depends,Query
from typing import Optional
from uuid import UUID
from starlette import status
from typing import Annotated

from pecha_api.plans.plans_response_models import PlansResponse, PlanDTO, CreatePlanRequest, PlanWithDays, UpdatePlanRequest, \
    PlanStatusUpdate
from pecha_api.plans.cms.service import get_filtered_plans, create_new_plan, get_details_plan, update_plan_details, \
    delete_selected_plan, update_selected_plan_status
from pecha_api.plans.plans_enums import SortBy, SortOrder

oauth2_scheme = HTTPBearer()
# Create router for CMS plan endpoints
cms_plans_router = APIRouter(
    prefix="/cms/plans",
    tags=["CMS Plans"]
)


@cms_plans_router.get("", status_code=status.HTTP_200_OK, response_model=PlansResponse)
async def get_plans(
        authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
        search: Optional[str] = Query(default=None, description="Search by plan title"),
        sort_by: str = Query(default=SortBy.TOTAL_DAYS),
        sort_order: str = Query(default=SortOrder.ASC),
        skip: int = Query(default=0),
        limit: int = Query(default=10)
):
    return await get_filtered_plans(
        token=authentication_credential.credentials,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )


@cms_plans_router.post("", status_code=status.HTTP_201_CREATED, response_model=PlanDTO)
async def create_plan(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
                      create_plan_request: CreatePlanRequest):
    return create_new_plan(
        token=authentication_credential.credentials,
        create_plan_request=create_plan_request
    )


@cms_plans_router.get("/{plan_id}", status_code=status.HTTP_200_OK, response_model=PlanWithDays)
async def get_plan_details(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
                           plan_id: UUID):
    return await get_details_plan(
        token=authentication_credential.credentials,
        plan_id=plan_id
    )


@cms_plans_router.put("/{plan_id}", status_code=status.HTTP_200_OK, response_model=PlanDTO)
async def update_plan(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
                      plan_id: UUID, update_plan_request: UpdatePlanRequest = None):
    return await update_plan_details(
        token=authentication_credential.credentials,
        plan_id=plan_id,
        update_plan_request=update_plan_request
    )


@cms_plans_router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
                      plan_id: UUID):
    return await delete_selected_plan(
        token=authentication_credential.credentials,
        plan_id=plan_id
    )


@cms_plans_router.patch("/{plan_id}/status", response_model=PlanDTO)
async def update_plan_status(
        authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
        plan_id: UUID,
        plan_status_update: PlanStatusUpdate = None
):
    return await update_selected_plan_status(
        token=authentication_credential.credentials,
        plan_id=plan_id,
        plan_status_update=plan_status_update
    )

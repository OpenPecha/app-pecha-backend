from fastapi import APIRouter, Query, Depends
from typing import Optional
from uuid import UUID
from starlette import status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated

from pecha_api.plans.plans_response_models import PlansResponse
from pecha_api.plans.users.models import UserPlanEnrollRequest, UserPlanProgress
from pecha_api.plans.users.service import (
    get_user_enrolled_plans,
    enroll_user_in_plan,
    get_user_plan_progress
)


oauth2_scheme = HTTPBearer()

# Create router for user progress endpoints
user_progress_router = APIRouter(
    prefix="/users/me",
    tags=["User Progress"]
)


@user_progress_router.get("/plans", status_code=status.HTTP_200_OK, response_model=PlansResponse)
async def get_user_plans(
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
    status_filter: Optional[str] = Query(None, description="Filter by plan status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50)
):
    """Get user's enrolled plans"""
    return await get_user_enrolled_plans(
        token=authentication_credential.credentials,
        status_filter=status_filter,
        skip=skip,
        limit=limit
    )


@user_progress_router.post("/plans", status_code=status.HTTP_201_CREATED, response_model=PlansResponse)
async def enroll_in_plan(
    enroll_request: UserPlanEnrollRequest,
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]
):
    """Enroll in a plan"""
    return await enroll_user_in_plan(
        token=authentication_credential.credentials,
        enroll_request=enroll_request
    )


@user_progress_router.get("/plans/{plan_id}", status_code=status.HTTP_200_OK, response_model=UserPlanProgress)
async def get_user_plan_progress_details(
    plan_id: UUID,
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]
):
    """Get user's progress for specific plan"""
    return await get_user_plan_progress(
        token=authentication_credential.credentials,
        plan_id=plan_id
    )

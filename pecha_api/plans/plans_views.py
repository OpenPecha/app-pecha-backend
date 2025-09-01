from fastapi import APIRouter, Query, Path
from typing import Optional
from uuid import UUID
from starlette import status

from plans.plans_response_models import PlansResponse, PlanDTO, CreatePlanRequest, PlanWithDays, UpdatePlanRequest, \
    PlanStatusUpdate
from plans.plans_service import get_filtered_plans, create_new_plan, get_details_plan, update_plan_details, \
    delete_selected_plan, update_selected_plan_status

oauth2_scheme = HTTPBearer()
# Create router for plan endpoints
plans_router = APIRouter(
    prefix="/cms/plans",
    tags=["Plans"]
)


@plans_router.get("", status_code=status.HTTP_200_OK, response_model=PlansResponse)
async def get_plans(
        search: Optional[str] = Query(None, description="Search by plan title"),
        sort_by: str = Query("title", enum=["title", "total_days", "status"]),
        sort_order: str = Query("asc", enum=["asc", "desc"]),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=50)
):
    return await get_filtered_plans(
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )


@plans_router.post("", status_code=status.HTTP_201_CREATED, response_model=PlanDTO)
async def create_plan(create_plan_request: CreatePlanRequest):
    return create_new_plan(create_plan_request=create_plan_request)


@plans_router.get("/{plan_id}", status_code=status.HTTP_200_OK, response_model=PlanWithDays)
async def get_plan_details(plan_id: UUID):
    return get_details_plan(plan_id=plan_id)


@plans_router.put("/{plan_id}", status_code=status.HTTP_200_OK, response_model=PlanDTO)
async def update_plan(plan_id: UUID, update_plan_request: UpdatePlanRequest = None):
    return update_plan_details(
        plan_id=plan_id,
        update_plan_request=update_plan_request
    )


@plans_router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(plan_id: UUID):
    return delete_selected_plan(plan_id=plan_id)


@plans_router.patch("/{plan_id}/status", response_model=PlanDTO)
async def update_plan_status(
        plan_id: UUID = Path(...),
        plan_status_update: PlanStatusUpdate = None
):
    return update_selected_plan_status(
        plan_id=plan_id,
        plan_status_update=plan_status_update
    )

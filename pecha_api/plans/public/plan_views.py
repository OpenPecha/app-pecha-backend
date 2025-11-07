from fastapi import APIRouter, Query
from typing import Optional
from uuid import UUID
from starlette import status

from pecha_api.plans.plans_response_models import PlansResponse, PlanDTO, PlanDayDTO
from pecha_api.plans.public.plan_models import PlanDaysResponse
from pecha_api.plans.public.plan_service import (
    get_published_plans, 
    get_published_plan, 
    get_plan_days,
    get_plan_day_details
)

public_plans_router = APIRouter(
    prefix="/plans",
    tags=["Public Plans"]
)


@public_plans_router.get("", status_code=status.HTTP_200_OK, response_model=PlansResponse)
async def get_plans(
    search: Optional[str] = Query(None, description="Search by plan title"),
    language: str = Query("en", description="Filter by language code (e.g., 'bo', 'en', 'zh'). Defaults to 'en'."),
    sort_by: str = Query("title", enum=["title", "total_days", "subscription_count"]),
    sort_order: str = Query("asc", enum=["asc", "desc"]),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50)
):
    return await get_published_plans(search=search, language=language, sort_by=sort_by, sort_order=sort_order, skip=skip, limit=limit)


@public_plans_router.get("/{plan_id}", status_code=status.HTTP_200_OK, response_model=PlanDTO)
async def get_plan_details(plan_id: UUID):
    return await get_published_plan(plan_id=plan_id)


@public_plans_router.get("/{plan_id}/days", status_code=status.HTTP_200_OK, response_model=PlanDaysResponse)
async def get_plan_days_list(plan_id: UUID):
    return await get_plan_days(plan_id=plan_id)


@public_plans_router.get("/{plan_id}/days/{day_number}", status_code=status.HTTP_200_OK, response_model=PlanDayDTO)
async def get_plan_day_content(plan_id: UUID, day_number: int):
    return await get_plan_day_details(plan_id=plan_id, day_number=day_number)

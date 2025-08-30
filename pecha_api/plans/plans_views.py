from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pecha_api.plans.plan_service import get_plan_list
from pecha_api.plans.plan_response_model import PlanResponse
from typing import Optional
from fastapi import APIRouter, Depends, Query

plan_router = APIRouter(
    prefix="/plan",
    tags=["Plan"],
)


@plan_router.get("", status_code=status.HTTP_202_ACCEPTED)
def plan_list(
    difficulty_level: Optional[str] = Query(default=None),
    tags: Optional[list[str]] = Query(default=None),
    featured: Optional[bool] = Query(default=None),
    skip: int = Query(default=0),
    limit: int = Query(default=10),
) -> PlanResponse:
    try:
        return get_plan_list(difficulty_level, tags, featured, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

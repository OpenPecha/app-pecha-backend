from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException
from starlette import status

from pecha_api.error_contants import ErrorConstants
from pecha_api.plans.items.plan_items_repository import get_days_by_plan_id, get_plan_day_with_tasks_and_subtasks
from pecha_api.plans.plans_enums import PlanStatus
from pecha_api.plans.plans_response_models import PlansResponse, PlanDTO
from pecha_api.plans.public.plan_response_models import PlanDayDTO
from pecha_api.plans.shared.utils import load_plans_from_json, convert_plan_model_to_dto
from pecha_api.plans.public.plan_response_models import PlanDaysResponse, PlanDayBasic, SubTaskDTO, TaskDTO
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_models import PlanSubTask
from pecha_api.users.users_service import validate_and_extract_user_details
from pecha_api.db.database import SessionLocal
from pecha_api.plans.cms.cms_plans_repository import get_plan_by_id


async def get_published_plans(
    search: Optional[str] = None, 
    language: Optional[str] = None,
    sort_by: str = "title", 
    sort_order: str = "asc", 
    skip: int = 0, 
    limit: int = 20
) -> PlansResponse:
    """Get published plans for public consumption (no authentication required)"""
    
    # Load plans from JSON file
    plan_listing = load_plans_from_json()
    
    # Filter only published plans and convert to DTOs
    published_plans = [
        convert_plan_model_to_dto(p) 
        for p in plan_listing.plans 
        if p.status == "PUBLISHED"
    ]
    
    # Apply search filter
    if search:
        published_plans = [p for p in published_plans if search.lower() in p.title.lower()]
    
    # Apply language filter
    if language:
        published_plans = [p for p in published_plans if p.language.lower() == language.lower()]
    
    # Sort plans
    reverse = sort_order == "desc"
    if sort_by == "title":
        published_plans.sort(key=lambda x: x.title, reverse=reverse)
    elif sort_by == "total_days":
        published_plans.sort(key=lambda x: x.total_days, reverse=reverse)
    elif sort_by == "subscription_count":
        published_plans.sort(key=lambda x: x.subscription_count, reverse=reverse)
    
    # Apply pagination
    total = len(published_plans)
    paginated_plans = published_plans[skip:skip + limit]
    
    return PlansResponse(
        plans=paginated_plans,
        skip=skip,
        limit=limit,
        total=total
    )


async def get_published_plan_details(plan_id: UUID) -> PlanDTO:
    """Get published plan details for public consumption (no authentication required)"""
    
    # Load plans from JSON file
    plan_listing = load_plans_from_json()
    
    # Find plan by ID and ensure it's published
    plan_model = next(
        (p for p in plan_listing.plans if p.id == str(plan_id) and p.status == "PUBLISHED"), 
        None
    )
    
    if not plan_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorConstants.PLAN_NOT_FOUND
        )
    
    return PlanDTO(
        id=UUID(plan_model.id),
        title=plan_model.title,
        description=plan_model.description,
        image_url=plan_model.image_url,
        total_days=plan_model.total_days,
        language=plan_model.language,
        status=PlanStatus(plan_model.status),
        subscription_count=plan_model.subscription_count
    )


async def get_plan_days(token: str, plan_id: UUID) -> PlanDaysResponse:
    """Get all days for a specific plan"""
    
    validate_and_extract_user_details(token=token)
    with SessionLocal() as db:
        plan_model = get_plan_by_id(db=db, plan_id=plan_id)
        if not plan_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorConstants.PLAN_NOT_FOUND
            )
        plan_days=get_days_by_plan_id(db=db, plan_id=plan_id)
        days_basic =[]
        for day_model in plan_days:
            day_basic = PlanDayBasic(
                id=str(day_model.id),
                day_number=day_model.day_number,
            )
            days_basic.append(day_basic)
        return PlanDaysResponse(days=days_basic)

def _get_task_subtasks_dto(subtasks: List[PlanSubTask]) -> List[SubTaskDTO]:

    subtasks_dto = [SubTaskDTO(
            id=subtask.id,
            content_type=subtask.content_type,
            content=subtask.content,
            display_order=subtask.display_order,
        )
        for subtask in subtasks
    ]
    
    return subtasks_dto

async def get_plan_day_details(token: str, plan_id: UUID, day_number: int) -> PlanDayDTO:
    """Get specific day's content with tasks"""
    
    validate_and_extract_user_details(token=token)
    with SessionLocal() as db:
        plan_item = get_plan_day_with_tasks_and_subtasks(db=db, plan_id=plan_id, day_number=day_number)
        plan_day_dto: PlanDayDTO = PlanDayDTO(
            id=plan_item.id,
            day_number=plan_item.day_number,
            tasks=[
                TaskDTO(
                    id=task.id,
                    title=task.title,
                    estimated_time=task.estimated_time,
                    display_order=task.display_order,
                    subtasks=_get_task_subtasks_dto(task.sub_tasks)
                )
                for task in plan_item.tasks
            ]
        )   
        return plan_day_dto

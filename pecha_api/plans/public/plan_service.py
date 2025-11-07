import logging
from uuid import UUID
from typing import Optional
from starlette import status
from pecha_api.config import get
from fastapi import HTTPException
from pecha_api.db.database import SessionLocal
from pecha_api.error_contants import ErrorConstants
from pecha_api.plans.public.plan_response_models import PlansResponse, PlanDTO, PlanDayDTO, AuthorDTO
from pecha_api.plans.public.plan_models import PlanDaysResponse, PlanDayBasic
from pecha_api.plans.users.plan_users_models import UserPlanProgress
from pecha_api.plans.items.plan_items_models import PlanItem
from pecha_api.uploads.S3_utils import generate_presigned_access_url
from pecha_api.plans.public.plan_repository import (get_published_plans_from_db, get_published_plans_count, get_published_plan_by_id)

logger = logging.getLogger(__name__)


async def get_published_plans(
    search: Optional[str] = None, 
    language: str = "en", 
    sort_by: str = "title", 
    sort_order: str = "asc", 
    skip: int = 0, 
    limit: int = 20
    ) -> PlansResponse:
    
    try:
        with SessionLocal() as db:
            plan_aggregates = get_published_plans_from_db(db=db, skip=skip, limit=limit, search=search, language=language, sort_by=sort_by, sort_order=sort_order)
            
            plan_dtos = []
            for plan_aggregate in plan_aggregates:
                plan = plan_aggregate.plan
                
                plan_image_url = generate_presigned_access_url(bucket_name=get("AWS_BUCKET_NAME"), s3_key=plan.image_url)
                
                plan_dto = PlanDTO(
                    id=plan.id,
                    title=plan.title,
                    description=plan.description,
                    language=plan.language.value if hasattr(plan.language, 'value') else plan.language,
                    difficulty_level=plan.difficulty_level,
                    image_url=plan_image_url,
                    total_days=plan_aggregate.total_days,
                    tags=plan.tags if plan.tags else []
                )
                plan_dtos.append(plan_dto)
            
            total = get_published_plans_count(db=db, search=search, language=language)
            
            return PlansResponse(plans=plan_dtos, skip=skip, limit=limit, total=total)
    
    except Exception as e:
        logger.error(f"Error fetching published plans: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch published plans: {str(e)}"
        )


async def get_published_plan(plan_id: UUID) -> PlanDTO:

    try:
        with SessionLocal() as db:
            plan = get_published_plan_by_id(db=db, plan_id=plan_id)
            
            if not plan:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.PLAN_NOT_FOUND)
            
            plan_image_url = generate_presigned_access_url(
                bucket_name=get("AWS_BUCKET_NAME"), 
                s3_key=plan.image_url
            )
            
            author_dto = None
            if plan.author:
                author_avatar_url = generate_presigned_access_url(
                    bucket_name=get("AWS_BUCKET_NAME"), 
                    s3_key=plan.author.image_url
                )
                author_dto = AuthorDTO(id=plan.author.id, firstname=plan.author.first_name, lastname=plan.author.last_name, image_url=author_avatar_url, image_key=plan.author.image_url)
            
            
            total_days = db.query(PlanItem).filter(PlanItem.plan_id == plan_id).count()  

            return PlanDTO(
                id=plan.id,
                title=plan.title,
                description=plan.description,
                language=plan.language.value if hasattr(plan.language, 'value') else plan.language,
                difficulty_level=plan.difficulty_level,
                image_url=plan_image_url,  
                total_days=total_days,
                tags=plan.tags if plan.tags else [],
                author=author_dto
            )
    
    except Exception as e:
        logger.error(f"Error fetching published plan details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch published plan details: {str(e)}"
        )


async def get_plan_days(plan_id: UUID) -> PlanDaysResponse:
    """Get all days for a specific plan"""
    
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
    
    # Convert days to basic day info (without tasks for listing)
    days_basic = []
    for day_model in plan_model.days:
        day_basic = PlanDayBasic(
            id=day_model.id,
            day_number=day_model.day_number,
            title=day_model.title
        )
        days_basic.append(day_basic)
    
    return PlanDaysResponse(days=days_basic)


async def get_plan_day_details(plan_id: UUID, day_number: int) -> PlanDayDTO:
    """Get specific day's content with tasks"""
    
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
    
    # Find the specific day
    day_model = next(
        (d for d in plan_model.days if d.day_number == day_number),
        None
    )
    
    if not day_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Day not found"
        )
    
    # Convert day model to DTO with all tasks
    return convert_day_model_to_dto(day_model)

from typing import Optional, List

from sqlalchemy.orm.attributes import create_proxied_attribute
from starlette import status
from pecha_api.plans.plans_models import Plan
from pecha_api.plans.items.plan_items_models import PlanItem
from pecha_api.db.database import SessionLocal
from pecha_api.plans.plans_repository import save_plan
from pecha_api.plans.items.plan_items_repository import save_plan_item
from pecha_api.plans.users.user_plan_progress_repository import get_plan_progress
from pecha_api.error_contants import ErrorConstants
from pecha_api.plans.authors.plan_author_service import validate_and_extract_author_details
from pecha_api.plans.plans_enums import LanguageCode, PlanStatus, ContentType
from pecha_api.plans.plans_response_models import PlansResponse, PlanDTO, CreatePlanRequest, TaskDTO, PlanDayDTO, PlanWithDays, \
    UpdatePlanRequest, PlanStatusUpdate
from pecha_api.plans.plans_repository import get_plans
from pecha_api.db.database import SessionLocal
import asyncio
from uuid import uuid4, UUID
from fastapi import HTTPException
DUMMY_PLANS = [
    PlanDTO(
        id=uuid4(),
        title="Introduction to Buddhist Meditation",
        description="A 7-day beginner's guide to Buddhist meditation practices",
        image_url="https://example.com/meditation.jpg",
        total_days=7,
        status=PlanStatus.PUBLISHED,
        subscription_count=150
    ),
    PlanDTO(
        id=uuid4(),
        title="The Four Noble Truths Study",
        description="Deep dive into the foundational teachings of Buddhism",
        image_url="https://example.com/four-truths.jpg",
        total_days=14,
        status=PlanStatus.PUBLISHED,
        subscription_count=89
    ),
    PlanDTO(
        id=uuid4(),
        title="Mindfulness in Daily Life",
        description="Practical applications of mindfulness for modern living",
        image_url="https://example.com/mindfulness.jpg",
        total_days=21,
        status=PlanStatus.DRAFT,
        subscription_count=0
    )
]
DUMMY_TASKS = [
    TaskDTO(
        id=uuid4(),
        title="Morning Breathing Exercise",
        description="Start your day with focused breathing",
        content_type=ContentType.TEXT,
        content="Sit comfortably and focus on your breath for 10 minutes...",
        estimated_time=15
    ),
    TaskDTO(
        id=uuid4(),
        title="Listen to Dharma Talk",
        description="Audio teaching on compassion",
        content_type=ContentType.AUDIO,
        content="https://example.com/dharma-talk-1.mp3",
        estimated_time=30
    )
]

DUMMY_DAYS = [
    PlanDayDTO(
        id=uuid4(),
        day_number=1,
        title="Day 1: Beginning the Journey",
        tasks=DUMMY_TASKS
    ),
    PlanDayDTO(
        id=uuid4(),
        day_number=2,
        title="Day 2: Deepening Practice",
        tasks=[DUMMY_TASKS[0]]
    )
]


async def get_filtered_plans(token: str, search: Optional[str], sort_by: str, sort_order: str, skip: int, limit: int) -> PlansResponse:
    # Validate token and author context (authorization can be extended later)
    validate_and_extract_author_details(token=token)
    total = 0
    rows = []
    with SessionLocal() as db_session:
        rows = get_plans(
            db=db_session,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit,
        )

    plans: List[PlanDTO] = []
    total = len(rows)
    for plan_model in rows:
        plans.append(
            PlanDTO(
                id=plan_model.id,
                title=plan_model.title,
                description=plan_model.description,
                image_url=plan_model.image_url,
                total_days=0,
                status=PlanStatus(plan_model.status.value),
                subscription_count=0,
            )
        )

    return PlansResponse(plans=plans, skip=skip, limit=limit, total=total)


def create_new_plan(token: str, create_plan_request: CreatePlanRequest) -> PlanDTO:

    current_author = validate_and_extract_author_details(token=token)
    new_plan_model = Plan(
        title=create_plan_request.title,
        description=create_plan_request.description,
        image_url=create_plan_request.image_url,
        author_id=current_author.id,
        difficulty_level=create_plan_request.difficulty_level,
        tags=create_plan_request.tags or [],
        status=PlanStatus.DRAFT.value,
        featured=False,
        language=LanguageCode(create_plan_request.language or LanguageCode.EN.value),
        created_by=current_author.email
    )
    plan = None
    # Save to database
    with SessionLocal() as db_session:
        saved_plan = save_plan(db=db_session, plan=new_plan_model)

        new_item_model = PlanItem(
            plan_id=saved_plan.id,
            day_number=create_plan_request.total_days,
            created_by=current_author.email
        )
        
        saved_plan_item = save_plan_item(db=db_session, plan_item=new_item_model)
        plan_progress = get_plan_progress(db=db_session, plan_id=saved_plan.id)
        total_subscription_count = len(plan_progress)
        
        return PlanDTO(
            id=saved_plan.id,
            title=saved_plan.title,
            description=saved_plan.description,
            image_url=saved_plan.image_url,
            total_days=saved_plan_item.day_number,
            status=PlanStatus(saved_plan.status.value),
            subscription_count=total_subscription_count
        )

async def get_details_plan(token:str,plan_id: UUID) -> PlanWithDays:
    #  current_author = validate_and_extract_author_details(token=token)
    """Get plan details with days listing"""
    # Find plan by ID
    plan = next((p for p in DUMMY_PLANS if p.id == plan_id), None)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=ErrorConstants.PLAN_NOT_FOUND)
    return PlanWithDays(
        id=plan.id,
        title=plan.title,
        description=plan.description,
        days=DUMMY_DAYS
    )
async def update_plan_details(token:str,plan_id: UUID, update_plan_request: UpdatePlanRequest) -> PlanDTO:
    """Update plan metadata"""
    # Find plan by ID
    #   current_author = validate_and_extract_author_details(token=token)
    plan = next((p for p in DUMMY_PLANS if p.id == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Update fields if provided
    if update_plan_request.title is not None:
        plan.title = update_plan_request.title
    if update_plan_request.description is not None:
        plan.description = update_plan_request.description
    if update_plan_request.total_days is not None:
        plan.total_days = update_plan_request.total_days
    if update_plan_request.image_url is not None:
        plan.image_url = update_plan_request.image_url
    return plan

async def update_selected_plan_status(token:str,plan_id: UUID, plan_status_update: PlanStatusUpdate) -> PlanDTO:
    """Update plan status"""
    # Find plan by ID
   # current_author = validate_and_extract_author_details(token=token)
    plan = next((p for p in DUMMY_PLANS if p.id == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Validate status transition
    if plan_status_update.status == PlanStatus.PUBLISHED:
        # In real implementation, check if plan has at least one day with content
        if plan.total_days == 0:
            raise HTTPException(
                status_code=400,
                detail="Plan must have at least one day with content to be published"
            )

    plan.status = plan_status_update.status
    return plan

async def delete_selected_plan(token:str,plan_id: UUID):
    """Delete plan"""
    # Find and remove plan
    #  current_author = validate_and_extract_author_details(token=token)
    global DUMMY_PLANS
    DUMMY_PLANS = [p for p in DUMMY_PLANS if p.id != plan_id]
    # In real implementation, check if plan exists and handle foreign key constraints
    return

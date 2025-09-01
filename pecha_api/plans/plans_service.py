from typing import Optional

from starlette import status

from error_contants import ErrorConstants
from plans.plans_enums import PlanStatus, ContentType
from plans.plans_response_models import PlansResponse, PlanDTO, CreatePlanRequest, TaskDTO, PlanDayDTO, PlanWithDays, \
    UpdatePlanRequest, PlanStatusUpdate
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


def get_filtered_plans(search: Optional[str], sort_by: str, sort_order: str, skip: int, limit: int) -> PlansResponse:
    # Dummy data for development
    filtered_plans = DUMMY_PLANS
    if search:
        filtered_plans = [p for p in DUMMY_PLANS if search.lower() in p.title.lower()]

    # Sort plans
    reverse = sort_order == "desc"
    if sort_by == "title":
        filtered_plans.sort(key=lambda x: x.title, reverse=reverse)
    elif sort_by == "total_days":
        filtered_plans.sort(key=lambda x: x.total_days, reverse=reverse)
    elif sort_by == "status":
        filtered_plans.sort(key=lambda x: x.status.value, reverse=reverse)

    # Apply pagination
    total = len(filtered_plans)
    paginated_plans = filtered_plans[skip:skip + limit]
    return PlansResponse(
        plans=paginated_plans,
        skip=skip,
        limit=limit,
        total=total
    )


def create_new_plan(create_plan_request: CreatePlanRequest) -> PlanDTO:
    """Create a new plan"""
    new_plan = PlanDTO(
        id=uuid4(),
        title=create_plan_request.title,
        description=create_plan_request.description,
        image_url=create_plan_request.image_url,
        total_days=create_plan_request.total_days,
        status=PlanStatus.DRAFT,
        subscription_count=0
    )

    # In real implementation, save to database
    DUMMY_PLANS.append(new_plan)
    return new_plan

def get_details_plan(plan_id: UUID) -> PlanWithDays:
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
def update_plan_details(plan_id: UUID, update_plan_request: UpdatePlanRequest) -> PlanDTO:
    """Update plan metadata"""
    # Find plan by ID
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

def update_selected_plan_status(plan_id: UUID, plan_status_update: PlanStatusUpdate) -> PlanDTO:
    """Update plan status"""
    # Find plan by ID
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

def delete_selected_plan(plan_id: UUID):
    """Delete plan"""
    # Find and remove plan
    global DUMMY_PLANS
    DUMMY_PLANS = [p for p in DUMMY_PLANS if p.id != plan_id]
    # In real implementation, check if plan exists and handle foreign key constraints
    return

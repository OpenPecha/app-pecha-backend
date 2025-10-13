import py_compile
from typing import Optional, List, Dict

from starlette import status
from pecha_api.plans.plans_models import Plan
from pecha_api.plans.items.plan_items_models import PlanItem
from pecha_api.plans.cms.cms_plans_repository import save_plan, get_plan_by_id
from pecha_api.plans.items.plan_items_repository import save_plan_items
from pecha_api.plans.users.plan_users_progress_repository import get_plan_progress

from pecha_api.plans.authors.plan_authors_service import validate_and_extract_author_details
from pecha_api.plans.plans_enums import LanguageCode, PlanStatus, ContentType
from pecha_api.plans.plans_response_models import PlansResponse, PlanDTO, CreatePlanRequest, TaskDTO, PlanDayDTO, \
    PlanWithDays, \
    UpdatePlanRequest, PlanStatusUpdate, PlansRepositoryResponse, PlanWithAggregates, SubTaskDTO
    
from pecha_api.plans.cms.cms_plans_repository import get_plans
from pecha_api.plans.items.plan_items_repository import get_plan_items_by_plan_id, get_plan_day_with_tasks_and_subtasks
from pecha_api.plans.tasks.plan_tasks_repository import get_tasks_by_item_ids
from pecha_api.plans.tasks.plan_tasks_models import PlanTask
from sqlalchemy.orm import Session

from pecha_api.db.database import SessionLocal
from pecha_api.config import get
from pecha_api.uploads.S3_utils import generate_presigned_access_url
from uuid import uuid4, UUID
from fastapi import HTTPException
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST, PLAN_NOT_FOUND

DUMMY_PLANS = [
    PlanDTO(
        id=uuid4(),
        title="Introduction to Buddhist Meditation",
        description="A 7-day beginner's guide to Buddhist meditation practices",
        language="en",
        image_url="https://example.com/meditation.jpg",
        total_days=7,
        status=PlanStatus.PUBLISHED,
        subscription_count=150
    ),
    PlanDTO(
        id=uuid4(),
        title="The Four Noble Truths Study",
        description="Deep dive into the foundational teachings of Buddhism",
        language="en",
        image_url="https://example.com/four-truths.jpg",
        total_days=14,
        status=PlanStatus.PUBLISHED,
        subscription_count=89
    ),
    PlanDTO(
        id=uuid4(),
        title="Mindfulness in Daily Life",
        description="Practical applications of mindfulness for modern living",
        language="en",
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
        estimated_time=15,
        display_order=1
    ),
    TaskDTO(
        id=uuid4(),
        title="Listen to Dharma Talk",
        estimated_time=30,
        display_order=2
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
    with SessionLocal() as db_session:
        plan_repository_response : PlansRepositoryResponse = get_plans(
            db=db_session,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit,
        )

    plans: List[PlanDTO] = []

    for plan_info in plan_repository_response.plan_info:
        plan_info: PlanWithAggregates
        selected_plan = plan_info.plan

        plans.append(
            PlanDTO(
                id=selected_plan.id,
                title=selected_plan.title,
                description=selected_plan.description,
                language=selected_plan.language.value if selected_plan.language and hasattr(selected_plan.language, 'value') else (selected_plan.language or 'EN'),
                image_url= generate_presigned_access_url(bucket_name=get("AWS_BUCKET_NAME"), s3_key=selected_plan.image_url),
                total_days=int(plan_info.total_days or 0),
                status=PlanStatus(selected_plan.status.value),
                subscription_count=int(plan_info.subscription_count or 0),
            )
        )

    return PlansResponse(plans=plans, skip=skip, limit=limit, total=plan_repository_response.total)


def create_new_plan(token: str, create_plan_request: CreatePlanRequest) -> PlanDTO:

    current_author = validate_and_extract_author_details(token=token)

    language = create_plan_request.language.upper() if create_plan_request.language else get("SITE_LANGUAGE").upper()

    new_plan_model = Plan(
        title=create_plan_request.title,
        description=create_plan_request.description,
        image_url=create_plan_request.image_url,
        author_id=current_author.id,
        difficulty_level=create_plan_request.difficulty_level,
        tags=create_plan_request.tags or [],
        status=PlanStatus.DRAFT,
        featured=False,
        language=LanguageCode(language),
        created_by=current_author.email
    )

    # Save to database
    with SessionLocal() as db_session:
        saved_plan = save_plan(db=db_session, plan=new_plan_model)

        new_item_models = [
            PlanItem(
                plan_id=saved_plan.id,
                day_number=day,
                created_by=current_author.email
            )
            for day in range(1, create_plan_request.total_days + 1)
        ]

        saved_items = save_plan_items(db=db_session, plan_items=new_item_models)
        plan_progress = get_plan_progress(db=db_session, plan_id=saved_plan.id)

        total_subscription_count = len(plan_progress)
        total_days = len(saved_items)

        return PlanDTO(
            id=saved_plan.id,
            title=saved_plan.title,
            description=saved_plan.description,
            language=saved_plan.language.value if hasattr(saved_plan.language, 'value') else saved_plan.language,
            image_url=saved_plan.image_url,
            total_days=total_days,
            status=saved_plan.status,
            subscription_count=total_subscription_count
        )

async def get_details_plan(token:str,plan_id: UUID) -> PlanWithDays:
    validate_and_extract_author_details(token=token)
    with SessionLocal() as db_session:
        return _get_plan_details(db_session, plan_id)


def _get_plan_details(db: Session, plan_id: UUID) -> PlanWithDays:
    # Fetch base plan
    plan: Plan = get_plan_by_id(db=db, plan_id=plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseError(error=BAD_REQUEST, 
            message=PLAN_NOT_FOUND).model_dump()
        )

    # Fetch items (days)
    items = get_plan_items_by_plan_id(db=db, plan_id=plan.id)
    plan_item_ids = [item.id for item in items]

    # Fetch tasks for all items in one query
    tasks = get_tasks_by_item_ids(db=db, plan_item_ids=plan_item_ids)
    tasks_by_item: Dict[UUID, List[PlanTask]] = {}
    for task in tasks:
        tasks_by_item.setdefault(task.plan_item_id, []).append(task)

    # Map to DTOs
    day_dtos: List[PlanDayDTO] = [
        PlanDayDTO(
            id=item.id,
            day_number=item.day_number,
            tasks=[
                TaskDTO(
                    id=task.id,
                    title=task.title,
                    estimated_time=task.estimated_time,
                    display_order=task.display_order,
                )
                for task in tasks_by_item.get(item.id, [])
            ],
        )
        for item in items
    ]

    return PlanWithDays(
        id=plan.id,
        title=plan.title,
        description=plan.description or "",
        language=plan.language or "EN",
        image_url=generate_presigned_access_url(bucket_name=get("AWS_BUCKET_NAME"), s3_key=plan.image_url),
        total_days=len(items),
        difficulty_level=plan.difficulty_level,
        tags=plan.tags or [],
        days=day_dtos,
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

async def get_plan_day_details(token:str,plan_id: UUID, day_number: int) -> PlanDayDTO:
    validate_and_extract_author_details(token=token)
    with SessionLocal() as db:
        plan_item: PlanItem = get_plan_day_with_tasks_and_subtasks(db=db, plan_id=plan_id, day_number=day_number)
        plan_day_dto: PlanDayDTO = PlanDayDTO(
            id=plan_item.id,
            day_number=plan_item.day_number,
            tasks=[
                TaskDTO(
                    id=task.id,
                    title=task.title,
                    estimated_time=task.estimated_time,
                    display_order=task.display_order,
                    subtasks=[
                        SubTaskDTO(
                            id=subtask.id,
                            content_type=subtask.content_type,
                            content=subtask.content,
                            display_order=subtask.display_order,
                        )
                        for subtask in task.sub_tasks
                    ]
                )
                for task in plan_item.tasks
            ]
        )   
        return plan_day_dto
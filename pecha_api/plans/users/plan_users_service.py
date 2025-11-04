from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from starlette import status

from pecha_api.error_contants import ErrorConstants
from pecha_api.plans.plans_enums import UserPlanStatusEnum
from pecha_api.plans.plans_response_models import PlansResponse
from pecha_api.plans.shared.utils import load_plans_from_json, convert_plan_model_to_dto
from pecha_api.plans.users.plan_users_model import UserPlanProgress
from pecha_api.plans.users.plan_users_response_models import UserPlanEnrollRequest
from pecha_api.users.users_service import validate_and_extract_user_details
from pecha_api.db.database import SessionLocal
from pecha_api.plans.cms.cms_plans_repository import get_plan_by_id
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST, PLAN_NOT_FOUND, ALREADY_ENROLLED_IN_PLAN
from pecha_api.plans.users.plan_users_progress_repository import get_plan_progress_by_user_id_and_plan_id, save_plan_progress

# Mock user progress data - in real implementation this would be from database
MOCK_USER_PROGRESS = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "plan_id": "1e0cc3752-382b-4c11-b39c-192ed62123bd",
        "started_at": "2024-01-15T10:00:00Z",
        "streak_count": 5,
        "longest_streak": 10,
        "status": "active",
        "is_completed": False,
        "completed_at": None,
        "created_at": "2024-01-15T10:00:00Z"
    }
]


async def get_user_enrolled_plans(
    token: str,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> PlansResponse:
    """Get user's enrolled plans with optional status filtering"""
    current_user = validate_and_extract_user_details(token=token)
    # Load plans from JSON file
    plan_listing = load_plans_from_json()
    
    # Filter user's progress records
    user_progress_records = [
        p for p in MOCK_USER_PROGRESS 
        if p["user_id"] == str(current_user.id)
    ]
    
    # Apply status filter if provided
    if status_filter:
        user_progress_records = [
            p for p in user_progress_records 
            if p["status"] == status_filter
        ]
    
    # Get plan details for enrolled plans
    enrolled_plans = []
    for progress in user_progress_records:
        plan_model = next(
            (p for p in plan_listing.plans if p.id == progress["plan_id"]),
            None
        )
        if plan_model:
            plan_dto = convert_plan_model_to_dto(plan_model)
            enrolled_plans.append(plan_dto)
    
    # Apply pagination
    total = len(enrolled_plans)
    paginated_plans = enrolled_plans[skip:skip + limit]
    
    return PlansResponse(
        plans=paginated_plans,
        skip=skip,
        limit=limit,
        total=total
    )


def enroll_user_in_plan(token: str, enroll_request: UserPlanEnrollRequest) -> None:
    """Enroll user in a plan"""
    current_user = validate_and_extract_user_details(token=token)
    with SessionLocal() as db:
        plan_model = get_plan_by_id(db=db, plan_id=enroll_request.plan_id)
        if not plan_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ResponseError(error=BAD_REQUEST, message=PLAN_NOT_FOUND).model_dump()
            )
        existing_enrollment = get_plan_progress_by_user_id_and_plan_id(db=db, user_id=current_user.id, plan_id=enroll_request.plan_id)
        if existing_enrollment:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ResponseError(error=BAD_REQUEST, message=ALREADY_ENROLLED_IN_PLAN).model_dump()
            )

        new_progress = UserPlanProgress(
            user_id=current_user.id,
            plan_id=plan_model.id,
            streak_count=0,
            longest_streak=0,
            status='NOT_STARTED',
            created_at=datetime.now(timezone.utc), 
            is_completed=False,
        )
        save_plan_progress(db=db, plan_progress=new_progress)
    


async def get_user_plan_progress(token: str, plan_id: UUID) -> UserPlanProgress:
    """Get user's progress for a specific plan"""
    current_user = validate_and_extract_user_details(token=token)
    # Find user's progress record
    progress_record = next(
        (p for p in MOCK_USER_PROGRESS 
         if p["user_id"] == str(current_user.id) and p["plan_id"] == str(plan_id)),
        None
    )
    
    if not progress_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not enrolled in this plan"
        )
    
    # Load plan details
    plan_listing = load_plans_from_json()
    plan_model = next(
        (p for p in plan_listing.plans if p.id == str(plan_id)),
        None
    )
    
    if not plan_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorConstants.PLAN_NOT_FOUND
        )
    
    # Convert to response model
    plan_dto = convert_plan_model_to_dto(plan_model)
    
    return UserPlanProgress(
        id=UUID(progress_record["id"]),
        user_id=UUID(progress_record["user_id"]),
        plan_id=UUID(progress_record["plan_id"]),
        plan=plan_dto.model_dump(),
        started_at=datetime.fromisoformat(progress_record["started_at"].replace("Z", "+00:00")),
        streak_count=progress_record["streak_count"],
        longest_streak=progress_record["longest_streak"],
        status=progress_record["status"],
        is_completed=progress_record["is_completed"],
        completed_at=datetime.fromisoformat(progress_record["completed_at"].replace("Z", "+00:00")) if progress_record["completed_at"] else None,
        created_at=datetime.fromisoformat(progress_record["created_at"].replace("Z", "+00:00"))
    )

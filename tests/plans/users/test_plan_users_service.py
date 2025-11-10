import uuid
import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from fastapi import HTTPException

from pecha_api.plans.users.plan_users_response_models import UserPlanEnrollRequest
from pecha_api.plans.users.plan_users_service import enroll_user_in_plan, complete_sub_task_service
from pecha_api.plans.response_message import (
    BAD_REQUEST,
    PLAN_NOT_FOUND,
    ALREADY_ENROLLED_IN_PLAN,
    SUB_TASK_NOT_FOUND,
)


def _mock_session_with_db():
    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock
    return db_mock, session_cm


def test_enroll_user_in_plan_success():
    user_id = uuid.uuid4()
    plan_id = uuid.uuid4()

    enroll_request = UserPlanEnrollRequest(plan_id=plan_id)

    db_mock, session_cm = _mock_session_with_db()

    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ) as mock_validate, patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_plan_by_id",
        return_value=SimpleNamespace(id=plan_id),
    ) as mock_get_plan, patch(
        "pecha_api.plans.users.plan_users_service.get_plan_progress_by_user_id_and_plan_id",
        return_value=None,
    ) as mock_get_progress, patch(
        "pecha_api.plans.users.plan_users_service.UserPlanProgress",
    ) as MockUserPlanProgress, patch(
        "pecha_api.plans.users.plan_users_service.save_plan_progress",
    ) as mock_save:
        constructed = SimpleNamespace(user_id=user_id, plan_id=plan_id)
        MockUserPlanProgress.return_value = constructed

        result = enroll_user_in_plan(token="token123", enroll_request=enroll_request)

        assert result is None

        mock_validate.assert_called_once_with(token="token123")
        mock_get_plan.assert_called_once_with(db=db_mock, plan_id=plan_id)
        mock_get_progress.assert_called_once_with(db=db_mock, user_id=user_id, plan_id=plan_id)

        # ensure model constructed with expected args
        ctor_kwargs = MockUserPlanProgress.call_args.kwargs
        assert ctor_kwargs["user_id"] == user_id
        assert ctor_kwargs["plan_id"] == plan_id
        assert ctor_kwargs["streak_count"] == 0
        assert ctor_kwargs["longest_streak"] == 0
        assert "status" in ctor_kwargs  # enum value NOT_STARTED
        assert ctor_kwargs["is_completed"] is False
        assert "created_at" in ctor_kwargs

        mock_save.assert_called_once()
        assert mock_save.call_args.kwargs["db"] is db_mock
        assert mock_save.call_args.kwargs["plan_progress"] is constructed


def test_enroll_user_in_plan_plan_not_found_raises_404():
    user_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    enroll_request = UserPlanEnrollRequest(plan_id=plan_id)

    _, session_cm = _mock_session_with_db()

    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_plan_by_id",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc_info:
            enroll_user_in_plan(token="tkn", enroll_request=enroll_request)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["error"] == BAD_REQUEST
        assert exc_info.value.detail["message"] == PLAN_NOT_FOUND


def test_enroll_user_in_plan_already_enrolled_raises_409():
    user_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    enroll_request = UserPlanEnrollRequest(plan_id=plan_id)

    db_mock, session_cm = _mock_session_with_db()

    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_plan_by_id",
        return_value=SimpleNamespace(id=plan_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_plan_progress_by_user_id_and_plan_id",
        return_value=SimpleNamespace(id=uuid.uuid4()),
    ):
        with pytest.raises(HTTPException) as exc_info:
            enroll_user_in_plan(token="tkn", enroll_request=enroll_request)

        assert exc_info.value.status_code == 409
        assert exc_info.value.detail["error"] == BAD_REQUEST
        assert exc_info.value.detail["message"] == ALREADY_ENROLLED_IN_PLAN


def test_complete_sub_task_service_success():
    user_id = uuid.uuid4()
    sub_task_id = uuid.uuid4()

    db_mock, session_cm = _mock_session_with_db()

    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ) as mock_validate, patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_sub_task_by_subtask_id",
        return_value=SimpleNamespace(id=sub_task_id),
    ) as mock_get_sub_task, patch(
        "pecha_api.plans.users.plan_users_service.UserSubTaskCompletion",
    ) as MockUserSubTaskCompletion, patch(
        "pecha_api.plans.users.plan_users_service.save_user_sub_task_completions",
    ) as mock_save:
        constructed = SimpleNamespace(user_id=user_id, sub_task_id=sub_task_id)
        MockUserSubTaskCompletion.return_value = constructed

        result = complete_sub_task_service(token="token123", id=sub_task_id)

        assert result is None

        mock_validate.assert_called_once_with(token="token123")
        mock_get_sub_task.assert_called_once_with(db=db_mock, id=sub_task_id)

        ctor_kwargs = MockUserSubTaskCompletion.call_args.kwargs
        assert ctor_kwargs["user_id"] == user_id
        assert ctor_kwargs["sub_task_id"] == sub_task_id

        mock_save.assert_called_once()
        assert mock_save.call_args.kwargs["db"] is db_mock
        assert mock_save.call_args.kwargs["user_sub_task_completions"] is constructed


def test_complete_sub_task_service_sub_task_not_found_raises_404():
    user_id = uuid.uuid4()
    sub_task_id = uuid.uuid4()

    _, session_cm = _mock_session_with_db()

    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_sub_task_by_subtask_id",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc_info:
            complete_sub_task_service(token="token123", id=sub_task_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["error"] == BAD_REQUEST
        assert exc_info.value.detail["message"] == SUB_TASK_NOT_FOUND


@pytest.mark.asyncio
async def test_get_user_enrolled_plans_success():
    from pecha_api.plans.users.plan_users_service import get_user_enrolled_plans
    from pecha_api.plans.plans_enums import LanguageCode, DifficultyLevel
    from datetime import datetime, timezone
    
    user_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    
    mock_user = SimpleNamespace(id=user_id)
    
    mock_progress = SimpleNamespace(
        user_id=user_id,
        plan_id=plan_id,
        started_at=datetime.now(timezone.utc),
        streak_count=5,
        longest_streak=10,
        status="ACTIVE",
        is_completed=False
    )
    
    mock_plan = SimpleNamespace(
        id=plan_id,
        title="Test Plan",
        description="Test Description",
        language=LanguageCode.EN,
        difficulty_level=DifficultyLevel.BEGINNER,
        image_url="images/plan_images/test.jpg",
        tags=["meditation", "mindfulness"]
    )
    
    db_mock, session_cm = _mock_session_with_db()
    
    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=mock_user,
    ) as mock_validate, patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_enrolled_plans_with_details",
        return_value=([(mock_progress, mock_plan, 30)], 1),
    ) as mock_get_plans, patch(
        "pecha_api.plans.users.plan_users_service.get",
        return_value="test-bucket",
    ), patch(
        "pecha_api.plans.users.plan_users_service.generate_presigned_access_url",
        return_value="https://s3.amazonaws.com/presigned-url",
    ) as mock_presigned:
        result = await get_user_enrolled_plans(
            token="token123",
            status_filter=None,
            skip=0,
            limit=20
        )
        
        mock_validate.assert_called_once_with(token="token123")
        mock_get_plans.assert_called_once()
        call_kwargs = mock_get_plans.call_args.kwargs
        assert call_kwargs["db"] is db_mock
        assert call_kwargs["user_id"] == user_id
        assert call_kwargs["status"] is None
        assert call_kwargs["skip"] == 0
        assert call_kwargs["limit"] == 20
        
        assert result.skip == 0
        assert result.limit == 20
        assert result.total == 1
        assert len(result.plans) == 1
        
        plan_dto = result.plans[0]
        assert plan_dto.id == plan_id
        assert plan_dto.title == "Test Plan"
        assert plan_dto.description == "Test Description"
        assert plan_dto.language == "EN"
        assert plan_dto.difficulty_level == "BEGINNER"
        assert plan_dto.image_url == "https://s3.amazonaws.com/presigned-url"
        assert plan_dto.total_days == 30
        assert plan_dto.tags == ["meditation", "mindfulness"]
        
        mock_presigned.assert_called_once_with(
            bucket_name="test-bucket",
            s3_key="images/plan_images/test.jpg"
        )


@pytest.mark.asyncio
async def test_get_user_enrolled_plans_with_status_filter():
    from pecha_api.plans.users.plan_users_service import get_user_enrolled_plans
    
    user_id = uuid.uuid4()
    mock_user = SimpleNamespace(id=user_id)
    
    db_mock, session_cm = _mock_session_with_db()
    
    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=mock_user,
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_enrolled_plans_with_details",
        return_value=([], 0),
    ) as mock_get_plans, patch(
        "pecha_api.plans.users.plan_users_service.get",
        return_value="test-bucket",
    ):
        result = await get_user_enrolled_plans(
            token="token123",
            status_filter="active",
            skip=0,
            limit=20
        )
        
        mock_get_plans.assert_called_once()
        call_kwargs = mock_get_plans.call_args.kwargs
        assert call_kwargs["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_get_user_enrolled_plans_with_pagination():
    from pecha_api.plans.users.plan_users_service import get_user_enrolled_plans
    
    user_id = uuid.uuid4()
    mock_user = SimpleNamespace(id=user_id)
    
    db_mock, session_cm = _mock_session_with_db()
    
    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=mock_user,
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_enrolled_plans_with_details",
        return_value=([], 50),
    ) as mock_get_plans, patch(
        "pecha_api.plans.users.plan_users_service.get",
        return_value="test-bucket",
    ):
        result = await get_user_enrolled_plans(
            token="token123",
            status_filter=None,
            skip=10,
            limit=10
        )
        
        mock_get_plans.assert_called_once()
        call_kwargs = mock_get_plans.call_args.kwargs
        assert call_kwargs["skip"] == 10
        assert call_kwargs["limit"] == 10
        
        assert result.skip == 10
        assert result.limit == 10
        assert result.total == 50


@pytest.mark.asyncio
async def test_get_user_enrolled_plans_empty_result():
    from pecha_api.plans.users.plan_users_service import get_user_enrolled_plans
    
    user_id = uuid.uuid4()
    mock_user = SimpleNamespace(id=user_id)
    
    db_mock, session_cm = _mock_session_with_db()
    
    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=mock_user,
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_enrolled_plans_with_details",
        return_value=([], 0),
    ), patch(
        "pecha_api.plans.users.plan_users_service.get",
        return_value="test-bucket",
    ):
        result = await get_user_enrolled_plans(
            token="token123",
            status_filter=None,
            skip=0,
            limit=20
        )
        
        assert result.plans == []
        assert result.skip == 0
        assert result.limit == 20
        assert result.total == 0


@pytest.mark.asyncio
async def test_get_user_enrolled_plans_without_image():
    from pecha_api.plans.users.plan_users_service import get_user_enrolled_plans
    from pecha_api.plans.plans_enums import LanguageCode, DifficultyLevel
    from datetime import datetime, timezone
    
    user_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    
    mock_user = SimpleNamespace(id=user_id)
    
    mock_progress = SimpleNamespace(
        user_id=user_id,
        plan_id=plan_id,
        started_at=datetime.now(timezone.utc),
        streak_count=0,
        longest_streak=0,
        status="NOT_STARTED",
        is_completed=False
    )
    
    mock_plan = SimpleNamespace(
        id=plan_id,
        title="Plan Without Image",
        description="Description",
        language=LanguageCode.BO,
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        image_url=None,
        tags=[]
    )
    
    db_mock, session_cm = _mock_session_with_db()
    
    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=mock_user,
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_enrolled_plans_with_details",
        return_value=([(mock_progress, mock_plan, 7)], 1),
    ), patch(
        "pecha_api.plans.users.plan_users_service.get",
        return_value="test-bucket",
    ), patch(
        "pecha_api.plans.users.plan_users_service.generate_presigned_access_url",
    ) as mock_presigned:
        result = await get_user_enrolled_plans(
            token="token123",
            status_filter=None,
            skip=0,
            limit=20
        )
        
        assert len(result.plans) == 1
        plan_dto = result.plans[0]
        assert plan_dto.image_url == ""
        
        mock_presigned.assert_not_called()


@pytest.mark.asyncio
async def test_get_user_enrolled_plans_presigned_url_error():
    from pecha_api.plans.users.plan_users_service import get_user_enrolled_plans
    from pecha_api.plans.plans_enums import LanguageCode, DifficultyLevel
    from datetime import datetime, timezone
    
    user_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    
    mock_user = SimpleNamespace(id=user_id)
    
    mock_progress = SimpleNamespace(
        user_id=user_id,
        plan_id=plan_id,
        started_at=datetime.now(timezone.utc),
        streak_count=0,
        longest_streak=0,
        status="ACTIVE",
        is_completed=False
    )
    
    mock_plan = SimpleNamespace(
        id=plan_id,
        title="Test Plan",
        description="Test Description",
        language=LanguageCode.EN,
        difficulty_level=DifficultyLevel.BEGINNER,
        image_url="images/plan_images/test.jpg",
        tags=[]
    )
    
    db_mock, session_cm = _mock_session_with_db()
    
    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=mock_user,
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_enrolled_plans_with_details",
        return_value=([(mock_progress, mock_plan, 30)], 1),
    ), patch(
        "pecha_api.plans.users.plan_users_service.get",
        return_value="test-bucket",
    ), patch(
        "pecha_api.plans.users.plan_users_service.generate_presigned_access_url",
        side_effect=Exception("S3 error"),
    ):
        result = await get_user_enrolled_plans(
            token="token123",
            status_filter=None,
            skip=0,
            limit=20
        )
        
        assert len(result.plans) == 1
        plan_dto = result.plans[0]
        assert plan_dto.image_url == ""


@pytest.mark.asyncio
async def test_get_user_enrolled_plans_multiple_plans():
    from pecha_api.plans.users.plan_users_service import get_user_enrolled_plans
    from pecha_api.plans.plans_enums import LanguageCode, DifficultyLevel
    from datetime import datetime, timezone
    
    user_id = uuid.uuid4()
    plan_id_1 = uuid.uuid4()
    plan_id_2 = uuid.uuid4()
    plan_id_3 = uuid.uuid4()
    
    mock_user = SimpleNamespace(id=user_id)
    
    mock_progress_1 = SimpleNamespace(
        user_id=user_id,
        plan_id=plan_id_1,
        started_at=datetime.now(timezone.utc),
        streak_count=5,
        longest_streak=10,
        status="ACTIVE",
        is_completed=False
    )
    
    mock_plan_1 = SimpleNamespace(
        id=plan_id_1,
        title="Meditation Plan",
        description="Daily meditation",
        language=LanguageCode.EN,
        difficulty_level=DifficultyLevel.BEGINNER,
        image_url="images/plan1.jpg",
        tags=["meditation"]
    )
    
    mock_progress_2 = SimpleNamespace(
        user_id=user_id,
        plan_id=plan_id_2,
        started_at=datetime.now(timezone.utc),
        streak_count=15,
        longest_streak=20,
        status="ACTIVE",
        is_completed=False
    )
    
    mock_plan_2 = SimpleNamespace(
        id=plan_id_2,
        title="Advanced Dharma",
        description="Advanced teachings",
        language=LanguageCode.BO,
        difficulty_level=DifficultyLevel.ADVANCED,
        image_url="images/plan2.jpg",
        tags=["dharma", "philosophy"]
    )
    
    mock_progress_3 = SimpleNamespace(
        user_id=user_id,
        plan_id=plan_id_3,
        started_at=datetime.now(timezone.utc),
        streak_count=0,
        longest_streak=0,
        status="COMPLETED",
        is_completed=True
    )
    
    mock_plan_3 = SimpleNamespace(
        id=plan_id_3,
        title="Beginner's Guide",
        description="Introduction",
        language=LanguageCode.EN,
        difficulty_level=DifficultyLevel.BEGINNER,
        image_url=None,
        tags=["basics"]
    )
    
    db_mock, session_cm = _mock_session_with_db()
    
    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=mock_user,
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_enrolled_plans_with_details",
        return_value=(
            [
                (mock_progress_1, mock_plan_1, 21),
                (mock_progress_2, mock_plan_2, 90),
                (mock_progress_3, mock_plan_3, 7)
            ],
            3
        ),
    ), patch(
        "pecha_api.plans.users.plan_users_service.get",
        return_value="test-bucket",
    ), patch(
        "pecha_api.plans.users.plan_users_service.generate_presigned_access_url",
        return_value="https://s3.amazonaws.com/presigned-url",
    ):
        result = await get_user_enrolled_plans(
            token="token123",
            status_filter=None,
            skip=0,
            limit=20
        )
        
        assert len(result.plans) == 3
        assert result.total == 3
        
        assert result.plans[0].title == "Meditation Plan"
        assert result.plans[0].language == "EN"
        assert result.plans[0].total_days == 21
        
        assert result.plans[1].title == "Advanced Dharma"
        assert result.plans[1].language == "BO"
        assert result.plans[1].difficulty_level == "ADVANCED"
        assert result.plans[1].total_days == 90
        
        assert result.plans[2].title == "Beginner's Guide"
        assert result.plans[2].image_url == ""
        assert result.plans[2].total_days == 7


@pytest.mark.asyncio
async def test_get_user_enrolled_plans_invalid_token():
    from pecha_api.plans.users.plan_users_service import get_user_enrolled_plans
    
    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        side_effect=HTTPException(status_code=401, detail={"error": "Unauthorized", "message": "Invalid token"}),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_user_enrolled_plans(
                token="invalid_token",
                status_filter=None,
                skip=0,
                limit=20
            )
        
        assert exc_info.value.status_code == 401
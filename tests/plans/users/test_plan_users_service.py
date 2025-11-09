import uuid
import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from fastapi import HTTPException

from pecha_api.plans.users.plan_users_response_models import UserPlanEnrollRequest
from pecha_api.plans.users.plan_users_service import (
    enroll_user_in_plan,
    complete_sub_task_service,
    complete_task_service,
    get_user_enrolled_plans,
    get_user_plan_progress,
    get_user_plan_day_details_service,
    delete_task_service,
)
from pecha_api.plans.response_message import (
    BAD_REQUEST,
    PLAN_NOT_FOUND,
    ALREADY_ENROLLED_IN_PLAN,
    SUB_TASK_NOT_FOUND,
    TASK_NOT_FOUND,
)
from pecha_api.plans.plans_response_models import PlanDTO
from pecha_api.plans.plans_enums import DifficultyLevel, PlanStatus
from pecha_api.error_contants import ErrorConstants
from pecha_api.plans.plans_enums import ContentType


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
async def test_get_user_enrolled_plans_success_with_filter_and_pagination():
    user_id = uuid.uuid4()
    plan_id_1 = uuid.uuid4()
    plan_id_2 = uuid.uuid4()

    dto1 = PlanDTO(
        id=plan_id_1,
        title="Plan 1",
        description="Desc",
        language="en",
        total_days=10,
        status=PlanStatus.PUBLISHED,
        subscription_count=1,
        difficulty_level=DifficultyLevel.BEGINNER,
        tags=[],
    )
    dto2 = PlanDTO(
        id=plan_id_2,
        title="Plan 2",
        description="Desc",
        language="en",
        total_days=5,
        status=PlanStatus.PUBLISHED,
        subscription_count=2,
        difficulty_level=DifficultyLevel.BEGINNER,
        tags=[],
    )

    mock_progress = [
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user_id),
            "plan_id": str(plan_id_1),
            "started_at": "2024-01-15T10:00:00Z",
            "streak_count": 1,
            "longest_streak": 1,
            "status": "active",
            "is_completed": False,
            "completed_at": None,
            "created_at": "2024-01-15T10:00:00Z",
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user_id),
            "plan_id": str(plan_id_2),
            "started_at": "2024-01-15T10:00:00Z",
            "streak_count": 1,
            "longest_streak": 1,
            "status": "paused",
            "is_completed": False,
            "completed_at": None,
            "created_at": "2024-01-15T10:00:00Z",
        },
    ]

    # paginate to only first item after filtering to active
    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.MOCK_USER_PROGRESS",
        new=mock_progress,
    ), patch(
        "pecha_api.plans.users.plan_users_service.load_plans_from_json",
        return_value=SimpleNamespace(plans=[SimpleNamespace(id=str(plan_id_1)), SimpleNamespace(id=str(plan_id_2))]),
    ), patch(
        "pecha_api.plans.users.plan_users_service.convert_plan_model_to_dto",
        side_effect=[dto1, dto2],
    ):
        result = await get_user_enrolled_plans(token="tok", status_filter="active", skip=0, limit=1)

        assert result.skip == 0
        assert result.limit == 1
        assert result.total == 1  # only 1 active
        assert len(result.plans) == 1
        assert result.plans[0].id == plan_id_1


@pytest.mark.asyncio
async def test_get_user_plan_progress_success():
    user_id = uuid.uuid4()
    plan_id = uuid.uuid4()

    dto = PlanDTO(
        id=plan_id,
        title="Plan X",
        description="desc",
        language="en",
        total_days=30,
        status=PlanStatus.PUBLISHED,
        subscription_count=0,
        difficulty_level=DifficultyLevel.BEGINNER,
        tags=[],
    )

    mock_progress = [
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user_id),
            "plan_id": str(plan_id),
            "started_at": "2024-01-15T10:00:00Z",
            "streak_count": 2,
            "longest_streak": 3,
            "status": "active",
            "is_completed": False,
            "completed_at": None,
            "created_at": "2024-01-15T10:00:00Z",
        }
    ]

    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.MOCK_USER_PROGRESS",
        new=mock_progress,
    ), patch(
        "pecha_api.plans.users.plan_users_service.load_plans_from_json",
        return_value=SimpleNamespace(plans=[SimpleNamespace(id=str(plan_id))]),
    ), patch(
        "pecha_api.plans.users.plan_users_service.convert_plan_model_to_dto",
        return_value=dto,
    ), patch(
        "pecha_api.plans.users.plan_users_service.UserPlanProgress",
    ) as MockUserPlanProgress:
        constructed = SimpleNamespace(
            id=uuid.uuid4(),
            user_id=user_id,
            plan_id=plan_id,
            plan=dto.model_dump(),
            status="active",
        )
        MockUserPlanProgress.return_value = constructed

        result = await get_user_plan_progress(token="tok", plan_id=plan_id)

        # Ensure constructor called with expected kwargs (including plan)
        ctor_kwargs = MockUserPlanProgress.call_args.kwargs
        assert ctor_kwargs["user_id"] == user_id
        assert ctor_kwargs["plan_id"] == plan_id
        assert ctor_kwargs["plan"]["id"] == plan_id
        assert ctor_kwargs["status"] == "active"

        # And the function returns the constructed object
        assert result is constructed


@pytest.mark.asyncio
async def test_get_user_plan_progress_not_enrolled_raises_404():
    user_id = uuid.uuid4()
    plan_id = uuid.uuid4()

    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.MOCK_USER_PROGRESS",
        new=[],
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_user_plan_progress(token="tok", plan_id=plan_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not enrolled in this plan"


def _mock_session_with_db_and_task_flow():
    db_mock, session_cm = _mock_session_with_db()
    return db_mock, session_cm


def test_complete_task_service_success():
    user_id = uuid.uuid4()
    task_id = uuid.uuid4()

    db_mock, session_cm = _mock_session_with_db_and_task_flow()

    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_task_by_id",
        return_value=SimpleNamespace(id=task_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.UserTaskCompletion",
    ) as MockUserTaskCompletion, patch(
        "pecha_api.plans.users.plan_users_service.save_user_task_completion",
    ) as mock_save, patch(
        "pecha_api.plans.users.plan_users_service.complete_all_subtasks_completions",
    ) as mock_complete_all_subtasks, patch(
        "pecha_api.plans.users.plan_users_service.check_day_completion",
    ) as mock_check_day_completion:
        constructed = SimpleNamespace(user_id=user_id, task_id=task_id)
        MockUserTaskCompletion.return_value = constructed

        result = complete_task_service(token="tok", task_id=task_id)

        assert result is None
        mock_save.assert_called_once()
        assert mock_save.call_args.kwargs["db"] is db_mock
        assert mock_save.call_args.kwargs["user_task_completion"] is constructed

        mock_complete_all_subtasks.assert_called_once()
        assert mock_complete_all_subtasks.call_args.kwargs["db"] is db_mock
        assert mock_complete_all_subtasks.call_args.kwargs["user_id"] == user_id
        assert mock_complete_all_subtasks.call_args.kwargs["task_id"] == task_id

        mock_check_day_completion.assert_called_once()
        assert mock_check_day_completion.call_args.kwargs["db"] is db_mock
        assert mock_check_day_completion.call_args.kwargs["user_id"] == user_id
        # task object identity isn't critical here; ensure it carries the id
        assert getattr(mock_check_day_completion.call_args.kwargs["task"], "id", None) == task_id


def test_complete_task_service_task_not_found_raises_404():
    user_id = uuid.uuid4()
    task_id = uuid.uuid4()

    _, session_cm = _mock_session_with_db_and_task_flow()

    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_task_by_id",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc_info:
            complete_task_service(token="tok", task_id=task_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["error"] == BAD_REQUEST
        assert exc_info.value.detail["message"] == TASK_NOT_FOUND


def test_complete_all_subtasks_completions_creates_missing_only():
    from pecha_api.plans.users.plan_users_service import complete_all_subtasks_completions

    user_id = uuid.uuid4()
    task_id = uuid.uuid4()

    sub_a, sub_b, sub_c = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

    db_mock = MagicMock()

    with patch(
        "pecha_api.plans.users.plan_users_service.get_sub_tasks_by_task_id",
        return_value=[SimpleNamespace(id=sub_a), SimpleNamespace(id=sub_b), SimpleNamespace(id=sub_c)],
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_subtask_completions_by_user_id_and_sub_task_ids",
        return_value=[SimpleNamespace(sub_task_id=sub_a), SimpleNamespace(sub_task_id=sub_c)],
    ), patch(
        "pecha_api.plans.users.plan_users_service.UserSubTaskCompletion",
        side_effect=lambda user_id, sub_task_id: SimpleNamespace(user_id=user_id, sub_task_id=sub_task_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.save_user_sub_task_completions_bulk",
    ) as mock_bulk:
        complete_all_subtasks_completions(db=db_mock, user_id=user_id, task_id=task_id)

        assert mock_bulk.call_count == 1
        created_list = mock_bulk.call_args.kwargs["user_sub_task_completions"]
        assert len(created_list) == 1
        assert created_list[0].user_id == user_id
        assert created_list[0].sub_task_id == sub_b


def test_complete_all_subtasks_completions_no_new_items_calls_bulk_with_empty():
    from pecha_api.plans.users.plan_users_service import complete_all_subtasks_completions

    user_id = uuid.uuid4()
    task_id = uuid.uuid4()

    sub_a, sub_b = uuid.uuid4(), uuid.uuid4()

    db_mock = MagicMock()

    with patch(
        "pecha_api.plans.users.plan_users_service.get_sub_tasks_by_task_id",
        return_value=[SimpleNamespace(id=sub_a), SimpleNamespace(id=sub_b)],
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_subtask_completions_by_user_id_and_sub_task_ids",
        return_value=[SimpleNamespace(sub_task_id=sub_a), SimpleNamespace(sub_task_id=sub_b)],
    ), patch(
        "pecha_api.plans.users.plan_users_service.UserSubTaskCompletion",
        side_effect=lambda user_id, sub_task_id: SimpleNamespace(user_id=user_id, sub_task_id=sub_task_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.save_user_sub_task_completions_bulk",
    ) as mock_bulk:
        complete_all_subtasks_completions(db=db_mock, user_id=user_id, task_id=task_id)

        created_list = mock_bulk.call_args.kwargs["user_sub_task_completions"]
        assert created_list == []


def test_check_day_completion_marks_day_complete_when_all_done():
    from pecha_api.plans.users.plan_users_service import check_day_completion

    user_id = uuid.uuid4()
    day_id = uuid.uuid4()

    t1, t2 = uuid.uuid4(), uuid.uuid4()
    task_obj = SimpleNamespace(plan_item_id=day_id, id=uuid.uuid4())

    db_mock = MagicMock()

    with patch(
        "pecha_api.plans.users.plan_users_service.get_tasks_by_plan_item_id",
        return_value=[SimpleNamespace(id=t1), SimpleNamespace(id=t2)],
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_task_completions_by_user_id_and_task_ids",
        return_value=[SimpleNamespace(task_id=t1), SimpleNamespace(task_id=t2)],
    ), patch(
        "pecha_api.plans.users.plan_users_service.UserDayCompletion",
        side_effect=lambda user_id, day_id: SimpleNamespace(user_id=user_id, day_id=day_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.save_user_day_completion",
    ) as mock_save:
        check_day_completion(db=db_mock, user_id=user_id, task=task_obj)

        assert mock_save.call_count == 1
        udc = mock_save.call_args.kwargs["user_day_completion"]
        assert udc.user_id == user_id
        assert udc.day_id == day_id


def test_check_day_completion_does_nothing_when_remaining_tasks():
    from pecha_api.plans.users.plan_users_service import check_day_completion

    user_id = uuid.uuid4()
    day_id = uuid.uuid4()

    t1, t2 = uuid.uuid4(), uuid.uuid4()
    task_obj = SimpleNamespace(plan_item_id=day_id, id=uuid.uuid4())

    db_mock = MagicMock()

    with patch(
        "pecha_api.plans.users.plan_users_service.get_tasks_by_plan_item_id",
        return_value=[SimpleNamespace(id=t1), SimpleNamespace(id=t2)],
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_task_completions_by_user_id_and_task_ids",
        return_value=[SimpleNamespace(task_id=t1)],
    ), patch(
        "pecha_api.plans.users.plan_users_service.save_user_day_completion",
    ) as mock_save:
        check_day_completion(db=db_mock, user_id=user_id, task=task_obj)

        mock_save.assert_not_called()


def test_delete_task_service_success():
    user_id = uuid.uuid4()
    task_id = uuid.uuid4()
    day_id = uuid.uuid4()

    db_mock, session_cm = _mock_session_with_db()

    sub_a, sub_b = uuid.uuid4(), uuid.uuid4()

    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_task_by_id",
        return_value=SimpleNamespace(id=task_id, plan_item_id=day_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.delete_user_task_completion",
    ) as mock_delete_task, patch(
        "pecha_api.plans.users.plan_users_service.delete_user_day_completion",
    ) as mock_delete_day, patch(
        "pecha_api.plans.users.plan_users_service.get_sub_tasks_by_task_id",
        return_value=[SimpleNamespace(id=sub_a), SimpleNamespace(id=sub_b)],
    ) as mock_get_subtasks, patch(
        "pecha_api.plans.users.plan_users_service.delete_user_subtask_completion",
    ) as mock_delete_subtasks:
        # execute
        result = delete_task_service(token="tok", task_id=task_id)

        # assertions
        assert result is None
        mock_delete_task.assert_called_once()
        assert mock_delete_task.call_args.kwargs["db"] is db_mock
        assert mock_delete_task.call_args.kwargs["user_id"] == user_id
        assert mock_delete_task.call_args.kwargs["task_id"] == task_id

        mock_delete_day.assert_called_once()
        assert mock_delete_day.call_args.kwargs["db"] is db_mock
        assert mock_delete_day.call_args.kwargs["user_id"] == user_id
        assert mock_delete_day.call_args.kwargs["day_id"] == day_id

        mock_get_subtasks.assert_called_once_with(db=db_mock, task_id=task_id)
        mock_delete_subtasks.assert_called_once()
        assert mock_delete_subtasks.call_args.kwargs["db"] is db_mock
        assert mock_delete_subtasks.call_args.kwargs["user_id"] == user_id
        assert set(mock_delete_subtasks.call_args.kwargs["sub_task_ids"]) == {sub_a, sub_b}


def test_delete_task_service_task_not_found_raises_404():
    user_id = uuid.uuid4()
    task_id = uuid.uuid4()

    _, session_cm = _mock_session_with_db()

    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_task_by_id",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc_info:
            delete_task_service(token="tok", task_id=task_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["error"] == BAD_REQUEST
        assert exc_info.value.detail["message"] == TASK_NOT_FOUND


@pytest.mark.asyncio
async def test_get_user_plan_progress_plan_not_found():
    user_id = uuid.uuid4()
    plan_id = uuid.uuid4()

    mock_progress = [
        {
            "id": str(uuid.uuid4()),
            "user_id": str(user_id),
            "plan_id": str(plan_id),
            "started_at": "2024-01-15T10:00:00Z",
            "streak_count": 1,
            "longest_streak": 1,
            "status": "active",
            "is_completed": False,
            "completed_at": None,
            "created_at": "2024-01-15T10:00:00Z",
        }
    ]

    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.MOCK_USER_PROGRESS",
        new=mock_progress,
    ), patch(
        "pecha_api.plans.users.plan_users_service.load_plans_from_json",
        return_value=SimpleNamespace(plans=[]),  # plan missing
    ):
        from pecha_api.plans.users.plan_users_service import get_user_plan_progress

        with pytest.raises(HTTPException) as exc_info:
            await get_user_plan_progress(token="tok", plan_id=plan_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.PLAN_NOT_FOUND


def test_get_user_plan_day_details_service_success():
    user_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    day_id = uuid.uuid4()

    task1_id = uuid.uuid4()
    task2_id = uuid.uuid4()
    sub1_id = uuid.uuid4()
    sub2_id = uuid.uuid4()

    plan_item = SimpleNamespace(
        id=day_id,
        day_number=3,
        tasks=[
            SimpleNamespace(
                id=task1_id,
                title="Task 1",
                estimated_time=10,
                display_order=1,
                sub_tasks=[
                    SimpleNamespace(id=sub1_id, content_type=ContentType.TEXT, content="A", display_order=1),
                ],
            ),
            SimpleNamespace(
                id=task2_id,
                title="Task 2",
                estimated_time=5,
                display_order=2,
                sub_tasks=[
                    SimpleNamespace(id=sub2_id, content_type=ContentType.AUDIO, content="B", display_order=1),
                ],
            ),
        ],
    )

    db_mock, session_cm = _mock_session_with_db()

    with patch(
        "pecha_api.plans.users.plan_users_service.validate_and_extract_user_details",
        return_value=SimpleNamespace(id=user_id),
    ), patch(
        "pecha_api.plans.users.plan_users_service.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_plan_day_with_tasks_and_subtasks",
        return_value=plan_item,
    ), patch(
        "pecha_api.plans.users.plan_users_service.is_day_completed",
        return_value=True,
    ) as mock_day_completed, patch(
        "pecha_api.plans.users.plan_users_service.get_user_task_completions_by_user_id_and_task_ids",
        return_value=[SimpleNamespace(task_id=task1_id)],
    ) as mock_task_completions, patch(
        "pecha_api.plans.users.plan_users_service.get_user_subtask_completions_by_user_id_and_sub_task_ids",
        return_value=[SimpleNamespace(sub_task_id=sub1_id)],
    ) as mock_subtask_completions:
        result = get_user_plan_day_details_service(token="tok", plan_id=plan_id, day_number=3)

        # Top-level day details
        assert result.id == day_id
        assert result.day_number == 3
        assert result.is_completed is True

        # Tasks mapping and completion flags
        assert len(result.tasks) == 2
        assert result.tasks[0].id == task1_id
        assert result.tasks[0].title == "Task 1"
        assert result.tasks[0].display_order == 1
        assert result.tasks[0].is_completed is True
        assert result.tasks[1].is_completed is False

        # Sub-tasks mapping and completion flags
        assert len(result.tasks[0].sub_tasks) == 1
        assert result.tasks[0].sub_tasks[0].id == sub1_id
        assert result.tasks[0].sub_tasks[0].is_completed is True

        assert len(result.tasks[1].sub_tasks) == 1
        assert result.tasks[1].sub_tasks[0].id == sub2_id
        assert result.tasks[1].sub_tasks[0].is_completed is False

        # Verify helper invocations
        mock_day_completed.assert_called_once_with(db=db_mock, user_id=user_id, day_id=day_id)
        mock_task_completions.assert_called_once()
        assert mock_task_completions.call_args.kwargs["db"] is db_mock
        assert mock_task_completions.call_args.kwargs["user_id"] == user_id
        assert set(mock_task_completions.call_args.kwargs["task_ids"]) == {task1_id, task2_id}
        mock_subtask_completions.assert_called_once()
        assert mock_subtask_completions.call_args.kwargs["db"] is db_mock
        assert mock_subtask_completions.call_args.kwargs["user_id"] == user_id
        assert set(mock_subtask_completions.call_args.kwargs["sub_task_ids"]) == {sub1_id, sub2_id}


def test_is_completion_helpers_boolean_gateways():
    from pecha_api.plans.users.plan_users_service import (
        is_task_completed,
        is_day_completed,
        is_sub_task_completed,
    )

    user_id = uuid.uuid4()
    day_id = uuid.uuid4()
    task_id = uuid.uuid4()
    sub_task_id = uuid.uuid4()

    db_mock = MagicMock()

    # True cases
    with patch(
        "pecha_api.plans.users.plan_users_service.get_user_task_completion_by_user_id_and_task_id",
        return_value=SimpleNamespace(id=uuid.uuid4()),
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_day_completion_by_user_id_and_day_id",
        return_value=SimpleNamespace(id=uuid.uuid4()),
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_subtask_completion_by_user_id_and_sub_task_id",
        return_value=SimpleNamespace(id=uuid.uuid4()),
    ):
        assert is_task_completed(db=db_mock, task_id=task_id, user_id=user_id) is True
        assert is_day_completed(db=db_mock, user_id=user_id, day_id=day_id) is True
        assert is_sub_task_completed(db=db_mock, user_id=user_id, sub_task_id=sub_task_id) is True

    # False cases
    with patch(
        "pecha_api.plans.users.plan_users_service.get_user_task_completion_by_user_id_and_task_id",
        return_value=None,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_day_completion_by_user_id_and_day_id",
        return_value=None,
    ), patch(
        "pecha_api.plans.users.plan_users_service.get_user_subtask_completion_by_user_id_and_sub_task_id",
        return_value=None,
    ):
        assert is_task_completed(db=db_mock, task_id=task_id, user_id=user_id) is False
        assert is_day_completed(db=db_mock, user_id=user_id, day_id=day_id) is False
        assert is_sub_task_completed(db=db_mock, user_id=user_id, sub_task_id=sub_task_id) is False
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
        "pecha_api.plans.users.plan_users_service.get_sub_task_by_id",
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
        "pecha_api.plans.users.plan_users_service.get_sub_task_by_id",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc_info:
            complete_sub_task_service(token="token123", id=sub_task_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["error"] == BAD_REQUEST
        assert exc_info.value.detail["message"] == SUB_TASK_NOT_FOUND
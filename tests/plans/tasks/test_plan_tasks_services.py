import uuid
import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from pecha_api.plans.plans_enums import ContentType
from pecha_api.plans.response_message import BAD_REQUEST, TASK_SAME_DAY_NOT_ALLOWED
from pecha_api.plans.tasks.plan_tasks_response_model import (
    CreateTaskRequest,
    TaskDTO,
    UpdateTaskDayRequest,
    UpdatedTaskDayResponse,
)
from pecha_api.plans.tasks.plan_tasks_services import create_new_task, change_task_day_service


@pytest.mark.asyncio
async def test_create_new_task_builds_and_saves_with_incremented_display_order():
    request = CreateTaskRequest(
        title="Read intro",
        description="Do reading",
        content_type=ContentType.TEXT,
        content="Intro content",
        estimated_time=15,
    )

    plan_id = uuid.uuid4()
    day_id = uuid.uuid4()

    # Mock DB session as context manager
    db_mock = MagicMock()

    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    plan_item = SimpleNamespace(id=uuid.uuid4())

    saved = SimpleNamespace(
        id=uuid.uuid4(),
        title=request.title,
        content_type=request.content_type,
        content=request.content,
        display_order=6,  # max(5) + 1
        estimated_time=request.estimated_time,
    )

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        return_value=SimpleNamespace(email="author@example.com"),
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ) as mock_session, patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_plan_item",
        return_value=plan_item,
    ) as mock_get_item, patch(
        "pecha_api.plans.tasks.plan_tasks_services._get_max_display_order",
        return_value=5,
    ) as mock_get_max, patch(
        "pecha_api.plans.tasks.plan_tasks_services.save_task",
        return_value=saved,
    ) as mock_save:
        resp = await create_new_task(
            token="token123",
            create_task_request=request,
            plan_id=plan_id,
            day_id=day_id,
        )

        # validate and author extraction
        assert mock_validate.call_count == 1
        assert mock_validate.call_args.kwargs == {"token": "token123"}

        # session used and plan item fetched
        assert mock_session.call_count == 1
        assert mock_get_item.call_count == 1
        assert mock_get_item.call_args.kwargs == {"db": db_mock, "plan_id": plan_id, "day_id": day_id}

        # display order calculation used helper
        assert mock_get_max.call_count == 1
        assert mock_get_max.call_args.kwargs == {"plan_item_id": plan_item.id}

        # save called with constructed task
        assert mock_save.call_count == 1
        save_kwargs = mock_save.call_args.kwargs
        assert save_kwargs["db"] is db_mock
        new_task = save_kwargs["new_task"]
        assert new_task.plan_item_id == plan_item.id
        assert new_task.title == request.title
        assert new_task.content_type == request.content_type
        assert new_task.content == request.content
        assert new_task.display_order == 6
        assert new_task.estimated_time == request.estimated_time
        assert new_task.created_by == "author@example.com"

        # response mapping
        expected = TaskDTO(
            id=saved.id,
            title=saved.title,
            content_type=saved.content_type,
            content=saved.content,
            display_order=saved.display_order,
            estimated_time=saved.estimated_time,
        )
        assert resp == expected


@pytest.mark.asyncio
async def test_change_task_day_service_success():
    token = "tok"
    task_id = uuid.uuid4()
    target_day_id = uuid.uuid4()

    request = UpdateTaskDayRequest(target_day_id=target_day_id)

    # Mock DB session as context manager
    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    targeted_day = SimpleNamespace(id=uuid.uuid4())  # different id to avoid same-day error
    updated_task = SimpleNamespace(
        id=task_id,
        plan_item_id=target_day_id,
        display_order=3,
        estimated_time=None,
        title="Updated Task",
    )

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        return_value=SimpleNamespace(email="author@example.com"),
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ) as mock_session, patch(
        "pecha_api.plans.tasks.plan_tasks_services._get_max_display_order",
        return_value=2,
    ) as mock_get_max, patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_plan_item_by_id",
        return_value=targeted_day,
    ) as mock_get_day, patch(
        "pecha_api.plans.tasks.plan_tasks_services.update_task_day",
        return_value=updated_task,
    ) as mock_update:
        resp = await change_task_day_service(
            token=token,
            task_id=task_id,
            update_task_request=request,
        )

        assert mock_validate.call_count == 1
        assert mock_validate.call_args.kwargs == {"token": token}

        assert mock_session.call_count == 1
        assert mock_get_max.call_count == 1
        assert mock_get_max.call_args.kwargs == {"plan_item_id": target_day_id}

        assert mock_get_day.call_count == 1
        assert mock_get_day.call_args.kwargs == {"db": db_mock, "day_id": target_day_id}

        assert mock_update.call_count == 1
        assert mock_update.call_args.kwargs == {
            "db": db_mock,
            "task_id": task_id,
            "target_day_id": target_day_id,
            "display_order": 3,
        }

        expected = UpdatedTaskDayResponse(
            task_id=task_id,
            day_id=target_day_id,
            display_order=3,
            estimated_time=None,
            title="Updated Task",
        )
        assert resp == expected


@pytest.mark.asyncio
async def test_change_task_day_service_same_day_error():
    token = "tok"
    task_id = uuid.uuid4()
    target_day_id = uuid.uuid4()

    request = UpdateTaskDayRequest(target_day_id=target_day_id)

    # Mock DB session as context manager
    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    targeted_day = SimpleNamespace(id=target_day_id)  # same id triggers error

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        return_value=SimpleNamespace(email="author@example.com"),
    ), patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.tasks.plan_tasks_services._get_max_display_order",
        return_value=2,
    ), patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_plan_item_by_id",
        return_value=targeted_day,
    ):
        with pytest.raises(Exception) as exc:
            await change_task_day_service(
                token=token,
                task_id=task_id,
                update_task_request=request,
            )

        # Expect HTTPException with specific detail
        from fastapi import HTTPException  # local import to avoid global dependency

        assert isinstance(exc.value, HTTPException)
        assert exc.value.status_code == 404
        assert exc.value.detail["error"] == BAD_REQUEST
        assert exc.value.detail["message"] == TASK_SAME_DAY_NOT_ALLOWED


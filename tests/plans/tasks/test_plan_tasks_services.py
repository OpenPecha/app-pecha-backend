import uuid
import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO
from pecha_api.plans.tasks.plan_tasks_services import create_new_task, delete_task_by_id


@pytest.mark.asyncio
async def test_create_new_task_builds_and_saves_with_incremented_display_order():
    request = CreateTaskRequest(
        title="Read intro",
        description="Do reading",
        estimated_time=15,
    )

    plan_id = uuid.uuid4()
    day_id = uuid.uuid4()

    # Mock DB session as context manager
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.scalar.return_value = 5  # existing max order

    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    plan_item = SimpleNamespace(id=uuid.uuid4())

    saved = SimpleNamespace(
        id=uuid.uuid4(),
        title=request.title,
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
        "pecha_api.plans.tasks.plan_tasks_services.PlanTask",
    ) as MockPlanTask, patch(
        "pecha_api.plans.tasks.plan_tasks_services.save_task",
        return_value=saved,
    ) as mock_save:
        # Return a prebuilt task instance from the mocked constructor
        constructed_task = SimpleNamespace(
            plan_item_id=plan_item.id,
            title=request.title,
            display_order=6,
            estimated_time=request.estimated_time,
            created_by="author@example.com",
        )
        MockPlanTask.return_value = constructed_task
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

        # display order calculation was attempted
        assert db_mock.query.call_count == 1

        # constructor called with expected arguments
        ctor_kwargs = MockPlanTask.call_args.kwargs
        assert ctor_kwargs == {
            "plan_item_id": plan_item.id,
            "title": request.title,
            "display_order": 6,
            "estimated_time": request.estimated_time,
            "created_by": "author@example.com",
        }

        # save called with constructed task instance
        assert mock_save.call_count == 1
        save_kwargs = mock_save.call_args.kwargs
        assert save_kwargs["db"] is db_mock
        new_task = save_kwargs["new_task"]
        assert new_task is constructed_task

        # response mapping
        expected = TaskDTO(
            id=saved.id,
            title=saved.title,
            display_order=saved.display_order,
            estimated_time=saved.estimated_time,
        )
        assert resp == expected


@pytest.mark.asyncio
async def test_delete_task_by_id_success():
    """Test successful task deletion when user is the task creator."""
    task_id = uuid.uuid4()
    token = "valid_token_123"
    author_email = "author@example.com"

    mock_author = SimpleNamespace(email=author_email)

    mock_task = SimpleNamespace(
        id=task_id,
        title="Test Task",
        created_by=author_email,
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        return_value=mock_author,
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ) as mock_session, patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
        return_value=mock_task,
    ) as mock_get_task, patch(
        "pecha_api.plans.tasks.plan_tasks_services.delete_task",
    ) as mock_delete:
        await delete_task_by_id(task_id=task_id, token=token)

        assert mock_validate.call_count == 1
        assert mock_validate.call_args.kwargs == {"token": token}

        assert mock_session.call_count == 1
        assert mock_get_task.call_count == 1
        assert mock_get_task.call_args.kwargs == {"db": db_mock, "task_id": task_id}

        assert mock_delete.call_count == 1
        assert mock_delete.call_args.kwargs == {"db": db_mock, "task_id": task_id}


@pytest.mark.asyncio
async def test_delete_task_by_id_unauthorized():
    """Test task deletion fails when user is not the task creator."""
    task_id = uuid.uuid4()
    token = "valid_token_123"
    author_email = "author@example.com"
    different_author_email = "different@example.com"

    mock_author = SimpleNamespace(email=author_email)

    mock_task = SimpleNamespace(
        id=task_id,
        title="Test Task",
        created_by=different_author_email,
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        return_value=mock_author,
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
        return_value=mock_task,
    ) as mock_get_task, patch(
        "pecha_api.plans.tasks.plan_tasks_services.delete_task",
    ) as mock_delete:
        with pytest.raises(HTTPException) as exc_info:
            await delete_task_by_id(task_id=task_id, token=token)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error"] == "Forbidden"
        assert exc_info.value.detail["message"] == "You are not authorized to delete this task"

        assert mock_validate.call_count == 1
        assert mock_get_task.call_count == 1
        assert mock_delete.call_count == 0


@pytest.mark.asyncio
async def test_delete_task_by_id_task_not_found():
    """Test task deletion fails when task doesn't exist."""
    task_id = uuid.uuid4()
    token = "valid_token_123"
    author_email = "author@example.com"

    mock_author = SimpleNamespace(email=author_email)

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        return_value=mock_author,
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
        side_effect=HTTPException(status_code=404, detail={"error": "BAD_REQUEST", "message": "Task not found"}),
    ) as mock_get_task, patch(
        "pecha_api.plans.tasks.plan_tasks_services.delete_task",
    ) as mock_delete:
        with pytest.raises(HTTPException) as exc_info:
            await delete_task_by_id(task_id=task_id, token=token)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail["message"].lower()

        assert mock_validate.call_count == 1
        assert mock_get_task.call_count == 1

        assert mock_delete.call_count == 0


@pytest.mark.asyncio
async def test_delete_task_by_id_invalid_token():
    """Test task deletion fails with invalid authentication token."""
    task_id = uuid.uuid4()
    token = "invalid_token"

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        side_effect=HTTPException(status_code=401, detail={"error": "UNAUTHORIZED", "message": "Invalid token"}),
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
    ) as mock_session, patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
    ) as mock_get_task, patch(
        "pecha_api.plans.tasks.plan_tasks_services.delete_task",
    ) as mock_delete:
        with pytest.raises(HTTPException) as exc_info:
            await delete_task_by_id(task_id=task_id, token=token)

        assert exc_info.value.status_code == 401

        assert mock_validate.call_count == 1
        assert mock_session.call_count == 0
        assert mock_get_task.call_count == 0
        assert mock_delete.call_count == 0


@pytest.mark.asyncio
async def test_delete_task_by_id_database_error():
    """Test task deletion handles database errors gracefully."""
    task_id = uuid.uuid4()
    token = "valid_token_123"
    author_email = "author@example.com"

    mock_author = SimpleNamespace(email=author_email)

    mock_task = SimpleNamespace(
        id=task_id,
        title="Test Task",
        created_by=author_email,
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        return_value=mock_author,
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
        return_value=mock_task,
    ) as mock_get_task, patch(
        "pecha_api.plans.tasks.plan_tasks_services.delete_task",
        side_effect=HTTPException(status_code=400, detail={"error": "BAD_REQUEST", "message": "Database error"}),
    ) as mock_delete:
        with pytest.raises(HTTPException) as exc_info:
            await delete_task_by_id(task_id=task_id, token=token)

        assert exc_info.value.status_code == 400

        assert mock_validate.call_count == 1
        assert mock_get_task.call_count == 1
        assert mock_delete.call_count == 1
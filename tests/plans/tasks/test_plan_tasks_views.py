import uuid
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException

from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO
from pecha_api.plans.tasks.plan_tasks_views import create_task, delete_task


class _Creds:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_create_task_success():
    request = CreateTaskRequest(
        title="Read intro",
        description="Do reading",
        estimated_time=15,
    )

    task_id = uuid.uuid4()
    expected = TaskDTO(
        id=task_id,
        title=request.title,
        display_order=1,
        estimated_time=request.estimated_time,
    )

    creds = _Creds(token="token123")
    plan_id = uuid.uuid4()
    day_id = uuid.uuid4()

    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.create_new_task",
        return_value=expected,
        new_callable=AsyncMock,
    ) as mock_create:
        resp = await create_task(
            authentication_credential=creds,
            create_task_request=request,
            plan_id=plan_id,
            day_id=day_id,
        )

        assert mock_create.call_count == 1
        assert mock_create.call_args.kwargs == {
            "token": "token123",
            "create_task_request": request,
            "plan_id": plan_id,
            "day_id": day_id,
        }

        assert resp == expected


@pytest.mark.asyncio
async def test_delete_task_success():
    """Test successful task deletion with valid authentication and authorization."""
    task_id = uuid.uuid4()
    creds = _Creds(token="valid_token_123")

    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.delete_task_by_id",
        new_callable=AsyncMock,
    ) as mock_delete:
        result = await delete_task(
            task_id=task_id,
            authentication_credential=creds,
        )
        assert mock_delete.call_count == 1
        assert mock_delete.call_args.kwargs == {
            "task_id": task_id,
            "token": "valid_token_123",
        }

        assert result is None


@pytest.mark.asyncio
async def test_delete_task_unauthorized():
    """Test task deletion fails when user is not the task creator."""
    task_id = uuid.uuid4()
    creds = _Creds(token="unauthorized_token")

    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.delete_task_by_id",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=403, detail={"error": "BAD_REQUEST", "message": "You are not authorized to delete this task"}),
    ) as mock_delete:
        with pytest.raises(HTTPException) as exc_info:
            await delete_task(
                task_id=task_id,
                authentication_credential=creds,
            )

        assert exc_info.value.status_code == 403
        assert "not authorized" in exc_info.value.detail["message"]

        assert mock_delete.call_count == 1


@pytest.mark.asyncio
async def test_delete_task_not_found():
    """Test task deletion fails when task doesn't exist."""
    task_id = uuid.uuid4()
    creds = _Creds(token="valid_token")

    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.delete_task_by_id",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": "Task not found"}),
    ) as mock_delete:
        with pytest.raises(HTTPException) as exc_info:
            await delete_task(
                task_id=task_id,
                authentication_credential=creds,
            )

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail["message"].lower()

        assert mock_delete.call_count == 1


@pytest.mark.asyncio
async def test_delete_task_invalid_token():
    """Test task deletion fails with invalid authentication token."""
    task_id = uuid.uuid4()
    creds = _Creds(token="invalid_token")

    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.delete_task_by_id",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=401, detail={"error": "UNAUTHORIZED", "message": "Invalid authentication token"}),
    ) as mock_delete:
        with pytest.raises(HTTPException) as exc_info:
            await delete_task(
                task_id=task_id,
                authentication_credential=creds,
            )

        assert exc_info.value.status_code == 401

        assert mock_delete.call_count == 1


@pytest.mark.asyncio
async def test_delete_task_database_error():
    """Test task deletion handles database errors gracefully."""
    task_id = uuid.uuid4()
    creds = _Creds(token="valid_token")

    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.delete_task_by_id",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=500, detail={"error": "INTERNAL_ERROR", "message": "Database error occurred"}),
    ) as mock_delete:
        with pytest.raises(HTTPException) as exc_info:
            await delete_task(
                task_id=task_id,
                authentication_credential=creds,
            )

        assert exc_info.value.status_code == 500

        assert mock_delete.call_count == 1



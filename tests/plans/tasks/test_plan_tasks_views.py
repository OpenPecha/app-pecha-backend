import uuid
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO, UpdateTaskDayRequest, UpdatedTaskDayResponse, GetTaskResponse, UpdateTaskOrderRequest
from pecha_api.plans.tasks.plan_tasks_views import create_task, change_task_day, delete_task, get_task, change_task_order


class _Creds:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_create_task_success():
    plan_id = uuid.uuid4()
    day_id = uuid.uuid4()
    
    request = CreateTaskRequest(
        plan_id=plan_id,
        day_id=day_id,
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

    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.create_new_task",
        return_value=expected,
        new_callable=AsyncMock,
    ) as mock_create:
        resp = await create_task(
            authentication_credential=creds,
            create_task_request=request,
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

@pytest.mark.asyncio
async def test_change_task_day_success():
    task_id = uuid.uuid4()
    target_day_id = uuid.uuid4()

    request = UpdateTaskDayRequest(target_day_id=target_day_id)

    expected = UpdatedTaskDayResponse(
        task_id=task_id,
        title="Some Task",
        day_id=target_day_id,
        display_order=3,
        estimated_time=None,
    )

    creds = _Creds(token="token456")

    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.change_task_day_service",
        return_value=expected,
        new_callable=AsyncMock,
    ) as mock_change:
        resp = await change_task_day(
            authentication_credential=creds,
            task_id=task_id,
            update_task_request=request,
        )

        assert mock_change.call_count == 1
        assert mock_change.call_args.kwargs == {
            "token": "token456",
            "task_id": task_id,
            "update_task_request": request,
        }

        assert resp == expected


@pytest.mark.asyncio
async def test_get_task_success_with_subtasks():
    task_id = uuid.uuid4()

    creds = _Creds(token="token789")

    expected = GetTaskResponse(
        id=task_id,
        title="Sample Task",
        display_order=2,
        estimated_time=30,
        subtasks=[],
    )

    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.get_task_subtasks_service",
        return_value=expected,
        new_callable=AsyncMock,
    ) as mock_get:
        resp = await get_task(
            task_id=task_id,
            authentication_credential=creds,
        )

        assert mock_get.call_count == 1
        assert mock_get.call_args.kwargs == {
            "task_id": task_id,
            "token": "token789",
        }

        assert resp == expected


@pytest.mark.asyncio
async def test_get_task_not_found():
    task_id = uuid.uuid4()
    creds = _Creds(token="token789")

    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.get_task_subtasks_service",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": "Task not found"}),
    ) as mock_get:
        with pytest.raises(HTTPException) as exc_info:
            await get_task(
                task_id=task_id,
                authentication_credential=creds,
            )

        assert exc_info.value.status_code == 404
        assert mock_get.call_count == 1


@pytest.mark.asyncio
async def test_update_task_title_success():
    """Test successful task title update with valid authentication and authorization."""
    task_id = uuid.uuid4()
    new_title = "Updated Task Title"
    
    from pecha_api.plans.tasks.plan_tasks_response_model import UpdateTaskTitleRequest, UpdateTaskTitleResponse
    from pecha_api.plans.tasks.plan_tasks_views import update_task_title
    
    request = UpdateTaskTitleRequest(title=new_title)
    
    expected_response = UpdateTaskTitleResponse(
        task_id=task_id,
        title=new_title
    )
    
    creds = _Creds(token="token123")
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.update_task_title_service",
        return_value=expected_response,
        new_callable=AsyncMock,
    ) as mock_update:
        resp = await update_task_title(
            authentication_credential=creds,
            task_id=task_id,
            update_request=request,
        )
        
        assert mock_update.call_count == 1
        assert mock_update.call_args.kwargs == {
            "token": "token123",
            "task_id": task_id,
            "update_request": request,
        }
        assert resp.task_id == task_id
        assert resp.title == new_title


@pytest.mark.asyncio
async def test_update_task_title_unauthorized():
    """Test task title update fails when user is not the task creator."""
    task_id = uuid.uuid4()
    new_title = "Updated Task Title"
    
    from pecha_api.plans.tasks.plan_tasks_response_model import UpdateTaskTitleRequest
    from pecha_api.plans.tasks.plan_tasks_views import update_task_title
    
    request = UpdateTaskTitleRequest(title=new_title)
    creds = _Creds(token="token123")
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.update_task_title_service",
        side_effect=HTTPException(
            status_code=403,
            detail={"error": "FORBIDDEN", "message": "You are not authorized to update this task"}
        ),
        new_callable=AsyncMock,
    ) as mock_update:
        with pytest.raises(HTTPException) as exc_info:
            await update_task_title(
                authentication_credential=creds,
                task_id=task_id,
                update_request=request,
            )
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_update_task_title_task_not_found():
    """Test task title update fails when task doesn't exist."""
    task_id = uuid.uuid4()
    new_title = "Updated Task Title"
    
    from pecha_api.plans.tasks.plan_tasks_response_model import UpdateTaskTitleRequest
    from pecha_api.plans.tasks.plan_tasks_views import update_task_title
    
    request = UpdateTaskTitleRequest(title=new_title)
    creds = _Creds(token="token123")
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.update_task_title_service",
        side_effect=HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "Task not found"}
        ),
        new_callable=AsyncMock,
    ) as mock_update:
        with pytest.raises(HTTPException) as exc_info:
            await update_task_title(
                authentication_credential=creds,
                task_id=task_id,
                update_request=request,
            )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_update_task_title_invalid_token():
    """Test task title update fails with invalid authentication token."""
    task_id = uuid.uuid4()
    new_title = "Updated Task Title"
    
    from pecha_api.plans.tasks.plan_tasks_response_model import UpdateTaskTitleRequest
    from pecha_api.plans.tasks.plan_tasks_views import update_task_title
    
    request = UpdateTaskTitleRequest(title=new_title)
    creds = _Creds(token="invalid_token")
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.update_task_title_service",
        side_effect=HTTPException(
            status_code=401,
            detail={"error": "UNAUTHORIZED", "message": "Invalid authentication token"}
        ),
        new_callable=AsyncMock,
    ) as mock_update:
        with pytest.raises(HTTPException) as exc_info:
            await update_task_title(
                authentication_credential=creds,
                task_id=task_id,
                update_request=request,
            )
        
        assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_update_task_title_empty_title():
    """Test task title update with empty title string."""
    task_id = uuid.uuid4()
    
    from pecha_api.plans.tasks.plan_tasks_response_model import UpdateTaskTitleRequest
    from pecha_api.plans.tasks.plan_tasks_views import update_task_title
    
    request = UpdateTaskTitleRequest(title="")
    creds = _Creds(token="token123")
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.update_task_title_service",
        side_effect=HTTPException(
            status_code=400,
            detail={"error": "BAD_REQUEST", "message": "Title cannot be empty"}
        ),
        new_callable=AsyncMock,
    ) as mock_update:
        with pytest.raises(HTTPException) as exc_info:
            await update_task_title(
                authentication_credential=creds,
                task_id=task_id,
                update_request=request,
            )
        
        assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_update_task_title_database_error():
    """Test task title update handles database errors gracefully."""
    task_id = uuid.uuid4()
    new_title = "Updated Task Title"
    
    from pecha_api.plans.tasks.plan_tasks_response_model import UpdateTaskTitleRequest
    from pecha_api.plans.tasks.plan_tasks_views import update_task_title
    
    request = UpdateTaskTitleRequest(title=new_title)
    creds = _Creds(token="token123")
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.update_task_title_service",
        side_effect=HTTPException(
            status_code=500,
            detail={"error": "INTERNAL_SERVER_ERROR", "message": "Database error occurred"}
        ),
        new_callable=AsyncMock,
    ) as mock_update:
        with pytest.raises(HTTPException) as exc_info:
            await update_task_title(
                authentication_credential=creds,
                task_id=task_id,
                update_request=request,
            )
        
        assert exc_info.value.status_code == 500

@pytest.mark.asyncio
async def test_change_task_order_success():
    """Test successful task order change with valid authentication and authorization."""
    day_id = uuid.uuid4()
    task_id_1 = uuid.uuid4()
    task_id_2 = uuid.uuid4()
    creds = _Creds(token="valid_token_123")
    
    from pecha_api.plans.tasks.plan_tasks_response_model import TaskOrderItem
    request = UpdateTaskOrderRequest(tasks=[
        TaskOrderItem(id=task_id_1, display_order=2),
        TaskOrderItem(id=task_id_2, display_order=1),
    ])
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.change_task_order_service",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_change_order:
        result = await change_task_order(
            authentication_credential=creds,
            day_id=day_id,
            update_task_order_request=request,
        )
        
        assert mock_change_order.call_count == 1
        assert mock_change_order.call_args.kwargs == {
            "token": "valid_token_123",
            "day_id": day_id,
            "update_task_order_request": request,
        }
        
        assert result is None


@pytest.mark.asyncio
async def test_change_task_order_multiple_tasks():
    """Test reordering multiple tasks within a day."""
    day_id = uuid.uuid4()
    task_id_1 = uuid.uuid4()
    task_id_2 = uuid.uuid4()
    task_id_3 = uuid.uuid4()
    creds = _Creds(token="valid_token_123")
    
    from pecha_api.plans.tasks.plan_tasks_response_model import TaskOrderItem
    request = UpdateTaskOrderRequest(tasks=[
        TaskOrderItem(id=task_id_1, display_order=3),
        TaskOrderItem(id=task_id_2, display_order=1),
        TaskOrderItem(id=task_id_3, display_order=2),
    ])
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.change_task_order_service",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_change_order:
        result = await change_task_order(
            authentication_credential=creds,
            day_id=day_id,
            update_task_order_request=request,
        )
        
        assert result is None


@pytest.mark.asyncio
async def test_change_task_order_single_task():
    """Test reordering a single task within a day."""
    day_id = uuid.uuid4()
    task_id = uuid.uuid4()
    creds = _Creds(token="valid_token_123")
    
    from pecha_api.plans.tasks.plan_tasks_response_model import TaskOrderItem
    request = UpdateTaskOrderRequest(tasks=[
        TaskOrderItem(id=task_id, display_order=5),
    ])
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.change_task_order_service",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_change_order:
        result = await change_task_order(
            authentication_credential=creds,
            day_id=day_id,
            update_task_order_request=request,
        )
        
        assert result is None


@pytest.mark.asyncio
async def test_change_task_order_to_first_position():
    """Test moving task to first position (order 1)."""
    day_id = uuid.uuid4()
    task_id = uuid.uuid4()
    creds = _Creds(token="valid_token_123")
    
    from pecha_api.plans.tasks.plan_tasks_response_model import TaskOrderItem
    request = UpdateTaskOrderRequest(tasks=[
        TaskOrderItem(id=task_id, display_order=1),
    ])
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.change_task_order_service",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_change_order:
        result = await change_task_order(
            authentication_credential=creds,
            day_id=day_id,
            update_task_order_request=request,
        )
        
        assert result is None


@pytest.mark.asyncio
async def test_change_task_order_unauthorized():
    """Test task order change fails when user is not the task creator."""
    day_id = uuid.uuid4()
    task_id = uuid.uuid4()
    creds = _Creds(token="unauthorized_token")
    
    from pecha_api.plans.tasks.plan_tasks_response_model import TaskOrderItem
    request = UpdateTaskOrderRequest(tasks=[
        TaskOrderItem(id=task_id, display_order=3),
    ])
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.change_task_order_service",
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=403, 
            detail={"error": "FORBIDDEN", "message": "You are not authorized to change this task order"}
        ),
    ) as mock_change_order:
        with pytest.raises(HTTPException) as exc_info:
            await change_task_order(
                authentication_credential=creds,
                day_id=day_id,
                update_task_order_request=request,
            )
        
        assert exc_info.value.status_code == 403
        assert "not authorized" in exc_info.value.detail["message"]


@pytest.mark.asyncio
async def test_change_task_order_task_not_found():
    """Test task order change fails when task doesn't exist."""
    day_id = uuid.uuid4()
    task_id = uuid.uuid4()
    creds = _Creds(token="valid_token_123")
    
    from pecha_api.plans.tasks.plan_tasks_response_model import TaskOrderItem
    request = UpdateTaskOrderRequest(tasks=[
        TaskOrderItem(id=task_id, display_order=3),
    ])
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.change_task_order_service",
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=404, 
            detail={"error": "NOT_FOUND", "message": "Task not found"}
        ),
    ) as mock_change_order:
        with pytest.raises(HTTPException) as exc_info:
            await change_task_order(
                authentication_credential=creds,
                day_id=day_id,
                update_task_order_request=request,
            )
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail["message"].lower()


@pytest.mark.asyncio
async def test_change_task_order_invalid_token():
    """Test task order change fails with invalid authentication token."""
    day_id = uuid.uuid4()
    task_id = uuid.uuid4()
    creds = _Creds(token="invalid_token")
    
    from pecha_api.plans.tasks.plan_tasks_response_model import TaskOrderItem
    request = UpdateTaskOrderRequest(tasks=[
        TaskOrderItem(id=task_id, display_order=3),
    ])
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.change_task_order_service",
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=401, 
            detail={"error": "UNAUTHORIZED", "message": "Invalid authentication token"}
        ),
    ) as mock_change_order:
        with pytest.raises(HTTPException) as exc_info:
            await change_task_order(
                authentication_credential=creds,
                day_id=day_id,
                update_task_order_request=request,
            )
        
        assert exc_info.value.status_code == 401
        assert "Invalid" in exc_info.value.detail["message"]


@pytest.mark.asyncio
async def test_change_task_order_task_not_in_day():
    """Test task order change fails when task doesn't belong to the specified day."""
    day_id = uuid.uuid4()
    task_id = uuid.uuid4()
    creds = _Creds(token="valid_token_123")
    
    from pecha_api.plans.tasks.plan_tasks_response_model import TaskOrderItem
    request = UpdateTaskOrderRequest(tasks=[
        TaskOrderItem(id=task_id, display_order=3),
    ])
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.change_task_order_service",
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=400, 
            detail={"error": "BAD_REQUEST", "message": f"Task {task_id} does not belong to day {day_id}"}
        ),
    ) as mock_change_order:
        with pytest.raises(HTTPException) as exc_info:
            await change_task_order(
                authentication_credential=creds,
                day_id=day_id,
                update_task_order_request=request,
            )
        
        assert exc_info.value.status_code == 400
        assert "does not belong to day" in exc_info.value.detail["message"]


@pytest.mark.asyncio
async def test_change_task_order_database_error():
    """Test task order change handles database errors gracefully."""
    day_id = uuid.uuid4()
    task_id = uuid.uuid4()
    creds = _Creds(token="valid_token_123")
    
    from pecha_api.plans.tasks.plan_tasks_response_model import TaskOrderItem
    request = UpdateTaskOrderRequest(tasks=[
        TaskOrderItem(id=task_id, display_order=3),
    ])
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.change_task_order_service",
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=500, 
            detail={"error": "INTERNAL_SERVER_ERROR", "message": "Database error occurred"}
        ),
    ) as mock_change_order:
        with pytest.raises(HTTPException) as exc_info:
            await change_task_order(
                authentication_credential=creds,
                day_id=day_id,
                update_task_order_request=request,
            )
        
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_change_task_order_update_failed():
    """Test task order change fails when update operation fails."""
    day_id = uuid.uuid4()
    task_id = uuid.uuid4()
    creds = _Creds(token="valid_token_123")
    
    from pecha_api.plans.tasks.plan_tasks_response_model import TaskOrderItem
    request = UpdateTaskOrderRequest(tasks=[
        TaskOrderItem(id=task_id, display_order=3),
    ])
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_views.change_task_order_service",
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=400, 
            detail={"error": "BAD_REQUEST", "message": "Failed to update task order"}
        ),
    ) as mock_change_order:
        with pytest.raises(HTTPException) as exc_info:
            await change_task_order(
                authentication_credential=creds,
                day_id=day_id,
                update_task_order_request=request,
            )
        
        assert exc_info.value.status_code == 400
        assert "Failed to update" in exc_info.value.detail["message"]
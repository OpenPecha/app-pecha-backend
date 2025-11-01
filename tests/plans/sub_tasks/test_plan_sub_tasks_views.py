import uuid
import pytest
from unittest.mock import patch, AsyncMock

from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_response_model import (
    SubTaskDTO,
    SubTaskRequest,
    SubTaskRequestFields,
    SubTaskResponse,
    UpdateSubTaskRequest,
    SubTaskOrderRequest,
    SubTaskOrderResponse,
    SubtaskOrderItem,
    UpdatedSubtaskOrderItem,
)
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views import (
    create_sub_tasks,
    update_sub_task,
    change_subtask_order,
)


class _Creds:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_create_sub_tasks_success():
    task_id = uuid.uuid4()
    request = SubTaskRequest(
        task_id=task_id,
        sub_tasks=[
            SubTaskRequestFields(content_type="TEXT", content="First"),
            SubTaskRequestFields(content_type="TEXT", content="Second"),
        ]
    )

    expected = SubTaskResponse(
        sub_tasks=[
            SubTaskDTO(id=uuid.uuid4(), content_type="TEXT", content="First", display_order=1),
            SubTaskDTO(id=uuid.uuid4(), content_type="TEXT", content="Second", display_order=2),
        ]
    )

    creds = _Creds(token="token123")

    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.create_new_sub_tasks",
        return_value=expected,
        new_callable=AsyncMock,
    ) as mock_create:
        resp = await create_sub_tasks(
            authentication_credential=creds,
            create_task_request=request,
        )

        assert mock_create.call_count == 1
        assert mock_create.call_args.kwargs == {
            "token": "token123",
            "create_task_request": request,
        }

        assert resp == expected



@pytest.mark.asyncio
async def test_update_sub_task_no_content_success():
    task_id = uuid.uuid4()
    sub_task_1_id = uuid.uuid4()
    sub_task_2_id = uuid.uuid4()

    request = UpdateSubTaskRequest(
        task_id=task_id,
        sub_tasks=[
            SubTaskDTO(id=sub_task_1_id, content_type="TEXT", content="First updated", display_order=1),
            SubTaskDTO(id=sub_task_2_id, content_type="TEXT", content="Second updated", display_order=2),
        ],
    )

    creds = _Creds(token="token123")

    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.update_sub_task_by_task_id",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_update:
        resp = await update_sub_task(
            authentication_credential=creds,
            update_sub_task_request=request,
        )

        assert mock_update.call_count == 1
        assert mock_update.call_args.kwargs == {
            "token": "token123",
            "update_sub_task_request": request,
        }

        assert resp is None


@pytest.mark.asyncio
async def test_change_subtask_order_success():
    """Test successful subtask order change with multiple subtasks"""
    task_id = uuid.uuid4()
    sub_task_id_1 = uuid.uuid4()
    sub_task_id_2 = uuid.uuid4()
    sub_task_id_3 = uuid.uuid4()
    
    request = SubTaskOrderRequest(
        subtasks=[
            SubtaskOrderItem(id=sub_task_id_1, display_order=3),
            SubtaskOrderItem(id=sub_task_id_2, display_order=1),
            SubtaskOrderItem(id=sub_task_id_3, display_order=2),
        ]
    )
    
    creds = _Creds(token="token123")
    
    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.change_subtask_order_service",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_change_order:
        resp = await change_subtask_order(
            task_id=task_id,
            authentication_credential=creds,
            update_subtask_order_request=request,
        )
        
        assert mock_change_order.call_count == 1
        assert mock_change_order.call_args.kwargs == {
            "token": "token123",
            "task_id": task_id,
            "update_subtask_order": request,
        }
        
        assert resp is None


@pytest.mark.asyncio
async def test_change_subtask_order_move_up():
    """Test moving subtask from position 5 to position 2"""
    task_id = uuid.uuid4()
    sub_task_ids = [uuid.uuid4() for _ in range(5)]
    
    request = SubTaskOrderRequest(
        subtasks=[
            SubtaskOrderItem(id=sub_task_ids[0], display_order=1),
            SubtaskOrderItem(id=sub_task_ids[4], display_order=2),
            SubtaskOrderItem(id=sub_task_ids[1], display_order=3),
            SubtaskOrderItem(id=sub_task_ids[2], display_order=4),
            SubtaskOrderItem(id=sub_task_ids[3], display_order=5),
        ]
    )
    
    creds = _Creds(token="token456")
    
    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.change_subtask_order_service",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_change_order:
        resp = await change_subtask_order(
            task_id=task_id,
            authentication_credential=creds,
            update_subtask_order_request=request,
        )
        
        assert mock_change_order.call_count == 1
        assert mock_change_order.call_args.kwargs["token"] == "token456"
        assert mock_change_order.call_args.kwargs["task_id"] == task_id
        assert len(mock_change_order.call_args.kwargs["update_subtask_order"].subtasks) == 5
        assert resp is None


@pytest.mark.asyncio
async def test_change_subtask_order_move_down():
    """Test moving subtask from position 2 to position 5"""
    task_id = uuid.uuid4()
    sub_task_ids = [uuid.uuid4() for _ in range(5)]
    
    request = SubTaskOrderRequest(
        subtasks=[
            SubtaskOrderItem(id=sub_task_ids[0], display_order=1),
            SubtaskOrderItem(id=sub_task_ids[2], display_order=2),
            SubtaskOrderItem(id=sub_task_ids[3], display_order=3),
            SubtaskOrderItem(id=sub_task_ids[4], display_order=4),
            SubtaskOrderItem(id=sub_task_ids[1], display_order=5),
        ]
    )
    
    creds = _Creds(token="test_token")
    
    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.change_subtask_order_service",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_change_order:
        resp = await change_subtask_order(
            task_id=task_id,
            authentication_credential=creds,
            update_subtask_order_request=request,
        )
        
        assert mock_change_order.call_count == 1
        assert len(mock_change_order.call_args.kwargs["update_subtask_order"].subtasks) == 5
        assert resp is None


@pytest.mark.asyncio
async def test_change_subtask_order_to_first_position():
    """Test moving subtask to first position (order 1)"""
    task_id = uuid.uuid4()
    sub_task_ids = [uuid.uuid4() for _ in range(3)]
    
    request = SubTaskOrderRequest(
        subtasks=[
            SubtaskOrderItem(id=sub_task_ids[2], display_order=1),
            SubtaskOrderItem(id=sub_task_ids[0], display_order=2),
            SubtaskOrderItem(id=sub_task_ids[1], display_order=3),
        ]
    )
    
    creds = _Creds(token="auth_token")
    
    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.change_subtask_order_service",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_change_order:
        resp = await change_subtask_order(
            task_id=task_id,
            authentication_credential=creds,
            update_subtask_order_request=request,
        )
        
        assert mock_change_order.call_count == 1
        assert resp is None


@pytest.mark.asyncio
async def test_change_subtask_order_unauthorized():
    """Test subtask order change with unauthorized user (403 Forbidden)"""
    from fastapi import HTTPException
    
    task_id = uuid.uuid4()
    sub_task_id = uuid.uuid4()
    
    request = SubTaskOrderRequest(
        subtasks=[
            SubtaskOrderItem(id=sub_task_id, display_order=1),
        ]
    )
    
    creds = _Creds(token="invalid_token")
    
    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.change_subtask_order_service",
        side_effect=HTTPException(status_code=403, detail="User not authorized to change subtask order"),
        new_callable=AsyncMock,
    ) as mock_change_order:
        with pytest.raises(HTTPException) as exc_info:
            await change_subtask_order(
                task_id=task_id,
                authentication_credential=creds,
                update_subtask_order_request=request,
            )
        
        assert exc_info.value.status_code == 403
        assert "not authorized" in exc_info.value.detail.lower()
        assert mock_change_order.call_count == 1


@pytest.mark.asyncio
async def test_change_subtask_order_task_not_found():
    """Test subtask order change when task doesn't exist (404 Not Found)"""
    from fastapi import HTTPException
    
    task_id = uuid.uuid4()
    sub_task_id = uuid.uuid4()
    
    request = SubTaskOrderRequest(
        subtasks=[
            SubtaskOrderItem(id=sub_task_id, display_order=1),
        ]
    )
    
    creds = _Creds(token="valid_token")
    
    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.change_subtask_order_service",
        side_effect=HTTPException(status_code=404, detail="Task not found"),
        new_callable=AsyncMock,
    ) as mock_change_order:
        with pytest.raises(HTTPException) as exc_info:
            await change_subtask_order(
                task_id=task_id,
                authentication_credential=creds,
                update_subtask_order_request=request,
            )
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
        assert mock_change_order.call_count == 1


@pytest.mark.asyncio
async def test_change_subtask_order_invalid_token():
    """Test subtask order change with invalid authentication token (401 Unauthorized)"""
    from fastapi import HTTPException
    
    task_id = uuid.uuid4()
    sub_task_id = uuid.uuid4()
    
    request = SubTaskOrderRequest(
        subtasks=[
            SubtaskOrderItem(id=sub_task_id, display_order=1),
        ]
    )
    
    creds = _Creds(token="expired_token")
    
    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.change_subtask_order_service",
        side_effect=HTTPException(status_code=401, detail="Invalid or expired token"),
        new_callable=AsyncMock,
    ) as mock_change_order:
        with pytest.raises(HTTPException) as exc_info:
            await change_subtask_order(
                task_id=task_id,
                authentication_credential=creds,
                update_subtask_order_request=request,
            )
        
        assert exc_info.value.status_code == 401
        assert mock_change_order.call_count == 1


@pytest.mark.asyncio
async def test_change_subtask_order_database_error():
    """Test subtask order change with database error (500 Internal Server Error)"""
    from fastapi import HTTPException
    
    task_id = uuid.uuid4()
    sub_task_ids = [uuid.uuid4() for _ in range(3)]
    
    request = SubTaskOrderRequest(
        subtasks=[
            SubtaskOrderItem(id=sub_task_ids[0], display_order=1),
            SubtaskOrderItem(id=sub_task_ids[1], display_order=2),
            SubtaskOrderItem(id=sub_task_ids[2], display_order=3),
        ]
    )
    
    creds = _Creds(token="valid_token")
    
    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.change_subtask_order_service",
        side_effect=HTTPException(status_code=500, detail="Database connection error"),
        new_callable=AsyncMock,
    ) as mock_change_order:
        with pytest.raises(HTTPException) as exc_info:
            await change_subtask_order(
                task_id=task_id,
                authentication_credential=creds,
                update_subtask_order_request=request,
            )
        
        assert exc_info.value.status_code == 500
        assert mock_change_order.call_count == 1


@pytest.mark.asyncio
async def test_change_subtask_order_update_failed():
    """Test subtask order change when update operation fails (400 Bad Request)"""
    from fastapi import HTTPException
    
    task_id = uuid.uuid4()
    sub_task_ids = [uuid.uuid4() for _ in range(2)]
    
    request = SubTaskOrderRequest(
        subtasks=[
            SubtaskOrderItem(id=sub_task_ids[0], display_order=2),
            SubtaskOrderItem(id=sub_task_ids[1], display_order=1),
        ]
    )
    
    creds = _Creds(token="valid_token")
    
    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.change_subtask_order_service",
        side_effect=HTTPException(status_code=400, detail="Subtask order update failed"),
        new_callable=AsyncMock,
    ) as mock_change_order:
        with pytest.raises(HTTPException) as exc_info:
            await change_subtask_order(
                task_id=task_id,
                authentication_credential=creds,
                update_subtask_order_request=request,
            )
        
        assert exc_info.value.status_code == 400
        assert "failed" in exc_info.value.detail.lower()
        assert mock_change_order.call_count == 1
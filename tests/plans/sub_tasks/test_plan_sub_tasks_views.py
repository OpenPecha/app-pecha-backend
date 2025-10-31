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
            SubtaskOrderItem(sub_task_id=sub_task_id_1, display_order=3),
            SubtaskOrderItem(sub_task_id=sub_task_id_2, display_order=1),
            SubtaskOrderItem(sub_task_id=sub_task_id_3, display_order=2),
        ]
    )
    
    expected = SubTaskOrderResponse(
        updated_subtasks=[
            UpdatedSubtaskOrderItem(sub_task_id=sub_task_id_1, display_order=3),
            UpdatedSubtaskOrderItem(sub_task_id=sub_task_id_2, display_order=1),
            UpdatedSubtaskOrderItem(sub_task_id=sub_task_id_3, display_order=2),
        ]
    )
    
    creds = _Creds(token="token123")
    
    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.change_subtask_order_service",
        return_value=expected,
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
            "update_subtask_order_request": request,
        }
        
        assert resp == expected
        assert len(resp.updated_subtasks) == 3
        assert resp.updated_subtasks[0].sub_task_id == sub_task_id_1
        assert resp.updated_subtasks[0].display_order == 3
        assert resp.updated_subtasks[1].sub_task_id == sub_task_id_2
        assert resp.updated_subtasks[1].display_order == 1
        assert resp.updated_subtasks[2].sub_task_id == sub_task_id_3
        assert resp.updated_subtasks[2].display_order == 2


@pytest.mark.asyncio
async def test_change_subtask_order_single_subtask():
    """Test subtask order change with single subtask"""
    task_id = uuid.uuid4()
    sub_task_id = uuid.uuid4()
    
    request = SubTaskOrderRequest(
        subtasks=[
            SubtaskOrderItem(sub_task_id=sub_task_id, display_order=1),
        ]
    )
    
    expected = SubTaskOrderResponse(
        updated_subtasks=[
            UpdatedSubtaskOrderItem(sub_task_id=sub_task_id, display_order=1),
        ]
    )
    
    creds = _Creds(token="token456")
    
    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.change_subtask_order_service",
        return_value=expected,
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
        assert len(mock_change_order.call_args.kwargs["update_subtask_order_request"].subtasks) == 1
        
        assert len(resp.updated_subtasks) == 1
        assert resp.updated_subtasks[0].sub_task_id == sub_task_id
        assert resp.updated_subtasks[0].display_order == 1


@pytest.mark.asyncio
async def test_change_subtask_order_reordering_multiple():
    """Test reordering multiple subtasks to different positions"""
    task_id = uuid.uuid4()
    sub_task_ids = [uuid.uuid4() for _ in range(5)]
    
    # Reorder from [1,2,3,4,5] to [5,3,1,4,2]
    request = SubTaskOrderRequest(
        subtasks=[
            SubtaskOrderItem(sub_task_id=sub_task_ids[4], display_order=1),
            SubtaskOrderItem(sub_task_id=sub_task_ids[2], display_order=2),
            SubtaskOrderItem(sub_task_id=sub_task_ids[0], display_order=3),
            SubtaskOrderItem(sub_task_id=sub_task_ids[3], display_order=4),
            SubtaskOrderItem(sub_task_id=sub_task_ids[1], display_order=5),
        ]
    )
    
    expected = SubTaskOrderResponse(
        updated_subtasks=[
            UpdatedSubtaskOrderItem(sub_task_id=sub_task_ids[4], display_order=1),
            UpdatedSubtaskOrderItem(sub_task_id=sub_task_ids[2], display_order=2),
            UpdatedSubtaskOrderItem(sub_task_id=sub_task_ids[0], display_order=3),
            UpdatedSubtaskOrderItem(sub_task_id=sub_task_ids[3], display_order=4),
            UpdatedSubtaskOrderItem(sub_task_id=sub_task_ids[1], display_order=5),
        ]
    )
    
    creds = _Creds(token="test_token")
    
    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views.change_subtask_order_service",
        return_value=expected,
        new_callable=AsyncMock,
    ) as mock_change_order:
        resp = await change_subtask_order(
            task_id=task_id,
            authentication_credential=creds,
            update_subtask_order_request=request,
        )
        
        assert mock_change_order.call_count == 1
        assert len(resp.updated_subtasks) == 5
        # Verify the new order
        assert resp.updated_subtasks[0].sub_task_id == sub_task_ids[4]
        assert resp.updated_subtasks[0].display_order == 1
        assert resp.updated_subtasks[4].sub_task_id == sub_task_ids[1]
        assert resp.updated_subtasks[4].display_order == 5
import uuid
import pytest
from unittest.mock import patch, AsyncMock

from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_response_model import (
    SubTaskDTO,
    SubTaskRequest,
    SubTaskRequestFields,
    SubTaskResponse,
)
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_views import create_sub_tasks


class _Creds:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_create_sub_tasks_success():
    request = SubTaskRequest(
        sub_tasks=[
            SubTaskRequestFields(content_type="TEXT", content="First"),
            SubTaskRequestFields(content_type="TEXT", content="Second"),
        ]
    )

    task_id = uuid.uuid4()
    expected = SubTaskResponse(
        data=[
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
            task_id=task_id,
        )

        assert mock_create.call_count == 1
        assert mock_create.call_args.kwargs == {
            "token": "token123",
            "create_task_request": request,
            "task_id": task_id,
        }

        assert resp == expected



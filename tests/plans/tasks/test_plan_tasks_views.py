import uuid
import pytest
from unittest.mock import patch, AsyncMock

from pecha_api.plans.plans_enums import ContentType
from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO
from pecha_api.plans.tasks.plan_tasks_views import create_task


class _Creds:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_create_task_success():
    request = CreateTaskRequest(
        title="Read intro",
        description="Do reading",
        content_type=ContentType.TEXT,
        content="Intro content",
        estimated_time=15,
    )

    expected = TaskDTO(
        id=str(uuid.uuid4()),
        title=request.title,
        description=request.description,
        content_type=request.content_type,
        content=request.content,
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
            plan_id="plan_1",
            day_id="day_1",
        )

        assert mock_create.call_count == 1
        assert mock_create.call_args.kwargs == {
            "token": "token123",
            "create_task_request": request,
            "plan_id": "plan_1",
            "day_id": "day_1",
        }

        assert resp == expected



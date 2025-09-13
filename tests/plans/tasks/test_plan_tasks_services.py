import uuid
import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from pecha_api.plans.plans_enums import ContentType
from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO
from pecha_api.plans.tasks.plan_tasks_services import create_new_task


@pytest.mark.asyncio
async def test_create_new_task_forwards_and_uses_author_email():
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

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        return_value=SimpleNamespace(email="author@example.com"),
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.create_task",
        return_value=expected,
    ) as mock_repo:
        resp = await create_new_task(
            token="token123",
            create_task_request=request,
            plan_id="plan_1",
            day_id="day_1",
        )

        assert mock_validate.call_count == 1
        assert mock_validate.call_args.kwargs == {"token": "token123"}

        assert mock_repo.call_count == 1
        assert mock_repo.call_args.kwargs == {
            "create_task_request": request,
            "plan_id": "plan_1",
            "day_id": "day_1",
            "created_by": "author@example.com",
        }

        assert resp == expected



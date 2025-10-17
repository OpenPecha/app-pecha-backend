import uuid
import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_response_model import (
    SubTaskDTO,
    SubTaskRequest,
    SubTaskRequestFields,
    SubTaskResponse,
    UpdateSubTaskRequest,
)
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services import create_new_sub_tasks, update_sub_task_by_task_id
from pecha_api.plans.response_message import BAD_REQUEST


@pytest.mark.asyncio
async def test_create_new_sub_tasks_builds_and_saves_with_incremented_display_order():
    task_id = uuid.uuid4()
    request = SubTaskRequest(
        task_id=task_id,
        sub_tasks=[
            SubTaskRequestFields(content_type="TEXT", content="First"),
            SubTaskRequestFields(content_type="TEXT", content="Second"),
        ]
    )

    # Mock DB session as context manager
    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    saved_items = [
        SimpleNamespace(
            id=uuid.uuid4(), content_type="TEXT", content="First", display_order=6
        ),
        SimpleNamespace(
            id=uuid.uuid4(), content_type="TEXT", content="Second", display_order=7
        ),
    ]

    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.validate_and_extract_author_details",
        return_value=SimpleNamespace(email="author@example.com"),
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.SessionLocal",
        return_value=session_cm,
    ) as mock_session, patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.get_task_by_id",
        return_value=SimpleNamespace(id=task_id),
    ) as mock_get_task, patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.get_max_display_order_for_sub_task",
        return_value=5,
    ) as mock_get_max, patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.PlanSubTask",
    ) as MockPlanSubTask, patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.save_sub_tasks_bulk",
        return_value=saved_items,
    ) as mock_save:
        # build return instances for each call
        constructed_1 = SimpleNamespace(
            task_id=task_id,
            content_type="TEXT",
            content="First",
            display_order=6,
            created_by="author@example.com",
        )
        constructed_2 = SimpleNamespace(
            task_id=task_id,
            content_type="TEXT",
            content="Second",
            display_order=7,
            created_by="author@example.com",
        )

        MockPlanSubTask.side_effect = [constructed_1, constructed_2]

        resp = await create_new_sub_tasks(
            token="token123",
            create_task_request=request,
        )

        assert mock_validate.call_count == 1
        assert mock_validate.call_args.kwargs == {"token": "token123"}

        assert mock_session.call_count == 1
        assert mock_get_task.call_count == 1

        assert mock_get_max.call_count == 1
        assert mock_get_max.call_args.kwargs == {"db": db_mock, "task_id": task_id}

        # constructor called twice with expected args
        call1 = MockPlanSubTask.call_args_list[0].kwargs
        call2 = MockPlanSubTask.call_args_list[1].kwargs
        assert call1 == {
            "task_id": task_id,
            "content_type": "TEXT",
            "content": "First",
            "display_order": 6,
            "created_by": "author@example.com",
        }
        assert call2 == {
            "task_id": task_id,
            "content_type": "TEXT",
            "content": "Second",
            "display_order": 7,
            "created_by": "author@example.com",
        }

        assert mock_save.call_count == 1
        save_kwargs = mock_save.call_args.kwargs
        assert save_kwargs["db"] is db_mock
        # verify the same constructed instances were passed
        assert save_kwargs["sub_tasks"] == [constructed_1, constructed_2]

        # response mapping
        expected = SubTaskResponse(
            sub_tasks=[
                SubTaskDTO(
                    id=saved_items[0].id,
                    content_type=saved_items[0].content_type,
                    content=saved_items[0].content,
                    display_order=saved_items[0].display_order,
                ),
                SubTaskDTO(
                    id=saved_items[1].id,
                    content_type=saved_items[1].content_type,
                    content=saved_items[1].content,
                    display_order=saved_items[1].display_order,
                ),
            ]
        )

        assert resp == expected


@pytest.mark.asyncio
async def test_create_new_sub_tasks_task_not_found_raises_http_exception():
    task_id = uuid.uuid4()
    request = SubTaskRequest(
        task_id=task_id,
        sub_tasks=[SubTaskRequestFields(content_type="TEXT", content="First")]
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.validate_and_extract_author_details",
        return_value=SimpleNamespace(email="author@example.com"),
    ), patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.get_task_by_id",
        return_value=None,
    ):
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            await create_new_sub_tasks(
                token="token123",
                create_task_request=request,
            )

        assert exc.value.status_code == 400
        detail = exc.value.detail
        assert detail["error"] == BAD_REQUEST
        # message is set from ErrorConstants.TASK_NOT_FOUND; validate presence
        assert "not found" in detail["message"].lower()



@pytest.mark.asyncio
async def test_update_sub_task_by_task_id_deletes_missing_and_updates_existing_and_returns_none():
    task_id = uuid.uuid4()
    existing_to_keep_id = uuid.uuid4()
    existing_to_delete_id = uuid.uuid4()

    request = UpdateSubTaskRequest(
        task_id=task_id,
        sub_tasks=[
            SubTaskDTO(id=existing_to_keep_id, content_type="TEXT", content="First updated", display_order=1),
        ],
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.validate_and_extract_author_details",
        return_value=SimpleNamespace(email="author@example.com"),
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.SessionLocal",
        return_value=session_cm,
    ) as mock_session, patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.get_task_by_id",
        return_value=SimpleNamespace(id=task_id, created_by="author@example.com"),
    ) as mock_get_task, patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.get_sub_tasks_by_task_id",
        return_value=[
            SimpleNamespace(id=existing_to_keep_id),
            SimpleNamespace(id=existing_to_delete_id),
        ],
    ) as mock_get_subtasks, patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.delete_sub_tasks_bulk",
    ) as mock_delete_bulk, patch(
        "pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services.update_sub_tasks_bulk",
    ) as mock_update_bulk:
        resp = await update_sub_task_by_task_id(
            token="token123",
            update_sub_task_request=request,
        )

        assert mock_validate.call_count == 1
        assert mock_validate.call_args.kwargs == {"token": "token123"}

        assert mock_session.call_count == 1
        assert mock_get_task.call_count == 1

        assert mock_get_subtasks.call_count == 1
        assert mock_get_subtasks.call_args.kwargs == {"db": db_mock, "task_id": task_id}

        # deleted only the missing id
        assert mock_delete_bulk.call_count == 1
        delete_kwargs = mock_delete_bulk.call_args.kwargs
        assert delete_kwargs["db"] is db_mock
        assert delete_kwargs["sub_tasks_ids"] == [existing_to_delete_id]

        # update called with provided DTOs list
        assert mock_update_bulk.call_count == 1
        update_kwargs = mock_update_bulk.call_args.kwargs
        assert update_kwargs["db"] is db_mock
        assert update_kwargs["sub_tasks"] == request.sub_tasks

        assert resp is None


import uuid
import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from pecha_api.plans.response_message import BAD_REQUEST, PLAN_DAY_NOT_FOUND, FORBIDDEN, UNAUTHORIZED_TASK_ACCESS, TASK_NOT_FOUND
from pecha_api.plans.tasks.plan_tasks_response_model import (
    CreateTaskRequest,
    TaskDTO,
    UpdateTaskDayRequest,
    UpdatedTaskDayResponse,
    GetTaskResponse,
    UpdateTaskTitleRequest,
    UpdateTaskTitleResponse,
)
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_response_model import SubTaskDTO
from pecha_api.plans.plans_enums import ContentType
from pecha_api.plans.tasks.plan_tasks_services import (
    create_new_task,
    change_task_day_service,
    delete_task_by_id,
    get_task_subtasks_service,
    update_task_title_service,
    _get_max_display_order,
    _reorder_sequentially,
    _get_author_task,
)


@pytest.mark.asyncio
async def test_create_new_task_builds_and_saves_with_incremented_display_order():
    plan_id = uuid.uuid4()
    day_id = uuid.uuid4()
    
    request = CreateTaskRequest(
        plan_id=plan_id,
        day_id=day_id,
        title="Read intro",
        description="Do reading",
        estimated_time=15,
    )

    # Mock DB session as context manager
    db_mock = MagicMock()

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
        "pecha_api.plans.tasks.plan_tasks_services._get_max_display_order",
        return_value=5,
    ) as mock_get_max, patch(
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

        # display order calculation used helper
        assert mock_get_max.call_count == 1
        assert mock_get_max.call_args.kwargs == {"plan_item_id": plan_item.id}

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
        plan_item_id=uuid.uuid4(),
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
    ) as mock_delete, patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_tasks_by_plan_item_id",
        return_value=[SimpleNamespace(id=uuid.uuid4(), display_order=2)],
    ) as mock_get_tasks, patch(
        "pecha_api.plans.tasks.plan_tasks_services._reorder_sequentially",
    ) as mock_reorder:
        await delete_task_by_id(task_id=task_id, token=token)

        assert mock_validate.call_count == 1
        assert mock_validate.call_args.kwargs == {"token": token}

        assert mock_session.call_count == 1
        assert mock_get_task.call_count == 1
        assert mock_get_task.call_args.kwargs == {"db": db_mock, "task_id": task_id}

        assert mock_delete.call_count == 1
        assert mock_delete.call_args.kwargs == {"db": db_mock, "task_id": task_id}

        # ensure tasks fetched and reorder is triggered with fetched tasks
        assert mock_get_tasks.call_count == 1
        assert mock_get_tasks.call_args.kwargs == {"db": db_mock, "plan_item_id": mock_task.plan_item_id}
        assert mock_reorder.call_count == 1
        # _reorder_sequentially(db, tasks)
        assert "db" in mock_reorder.call_args.kwargs
        assert "tasks" in mock_reorder.call_args.kwargs


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
        plan_item_id=uuid.uuid4(),
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        return_value=SimpleNamespace(email=author_email),
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
        return_value=mock_task,
    ) as mock_get_task, patch(
        "pecha_api.plans.tasks.plan_tasks_services.delete_task",
    ) as mock_delete, patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_tasks_by_plan_item_id",
    ) as mock_get_tasks, patch(
        "pecha_api.plans.tasks.plan_tasks_services._reorder_sequentially",
    ) as mock_reorder:
        with pytest.raises(HTTPException) as exc_info:
            await delete_task_by_id(task_id=task_id, token=token)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error"] == "Forbidden"
        assert exc_info.value.detail["message"] == "You are not authorized to delete this task"

        assert mock_validate.call_count == 1
        assert mock_get_task.call_count == 1
        # ensure delete, get_tasks and reorder were not called
        assert mock_delete.call_count == 0
        assert mock_get_tasks.call_count == 0
        assert mock_reorder.call_count == 0


@pytest.mark.asyncio
async def test_get_task_subtasks_service_image_content_uses_presigned_url():
    task_id = uuid.uuid4()

    # subtask with IMAGE content should be transformed to presigned URL
    image_key = "plans/tasks/images/img-123.png"
    subtask_image = SimpleNamespace(
        id=uuid.uuid4(),
        content_type=ContentType.IMAGE,  # enum to match service comparison
        content=image_key,
        display_order=1,
    )

    mock_task = SimpleNamespace(
        id=task_id,
        title="Task with image",
        display_order=1,
        estimated_time=5,
        created_by="creator@example.com",
        sub_tasks=[subtask_image],
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    presigned = "https://signed-url.example.com/img-123.png?sig=abc"

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        return_value=SimpleNamespace(email="creator@example.com"),
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
        return_value=mock_task,
    ) as mock_get_task, patch(
        "pecha_api.plans.tasks.plan_tasks_services.get",
        return_value="my-bucket",
    ) as mock_get_cfg, patch(
        "pecha_api.plans.tasks.plan_tasks_services.generate_presigned_access_url",
        return_value=presigned,
    ) as mock_presign:
        resp = await get_task_subtasks_service(task_id=task_id, token="token789")

        assert mock_validate.call_count == 1
        assert mock_get_task.call_count == 1
        assert mock_get_cfg.call_count == 1
        mock_presign.assert_called_once_with(bucket_name="my-bucket", s3_key=image_key)

        expected = GetTaskResponse(
            id=mock_task.id,
            title=mock_task.title,
            display_order=mock_task.display_order,
            estimated_time=mock_task.estimated_time,
            subtasks=[
                SubTaskDTO(
                    id=subtask_image.id,
                    content_type=ContentType.IMAGE,
                    content=presigned,
                    image_url=image_key,
                    display_order=subtask_image.display_order,
                ),
            ],
        )
        assert resp == expected


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
    ) as mock_delete, patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_tasks_by_plan_item_id",
    ) as mock_get_tasks, patch(
        "pecha_api.plans.tasks.plan_tasks_services._reorder_sequentially",
    ) as mock_reorder:
        with pytest.raises(HTTPException) as exc_info:
            await delete_task_by_id(task_id=task_id, token=token)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail["message"].lower()

        assert mock_validate.call_count == 1
        assert mock_get_task.call_count == 1

        assert mock_delete.call_count == 0
        assert mock_reorder.call_count == 0


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
    ) as mock_delete, patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_tasks_by_plan_item_id",
    ) as mock_get_tasks, patch(
        "pecha_api.plans.tasks.plan_tasks_services._reorder_sequentially",
    ) as mock_reorder:
        with pytest.raises(HTTPException) as exc_info:
            await delete_task_by_id(task_id=task_id, token=token)

        assert exc_info.value.status_code == 401

        assert mock_validate.call_count == 1
        assert mock_session.call_count == 0
        assert mock_get_task.call_count == 0
        assert mock_delete.call_count == 0
        assert mock_get_tasks.call_count == 0
        assert mock_reorder.call_count == 0


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
        plan_item_id=uuid.uuid4(),
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
    ) as mock_delete, patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_tasks_by_plan_item_id",
    ) as mock_get_tasks, patch(
        "pecha_api.plans.tasks.plan_tasks_services._reorder_sequentially",
    ) as mock_reorder:
        with pytest.raises(HTTPException) as exc_info:
            await delete_task_by_id(task_id=task_id, token=token)

        assert exc_info.value.status_code == 400

        assert mock_validate.call_count == 1
        assert mock_get_task.call_count == 1
        assert mock_delete.call_count == 1
        # get_tasks and reorder should not be called if delete fails
        assert mock_get_tasks.call_count == 0
        assert mock_reorder.call_count == 0


@pytest.mark.asyncio
async def test_change_task_day_service_success():
    task_id = uuid.uuid4()
    target_day_id = uuid.uuid4()

    request = UpdateTaskDayRequest(target_day_id=target_day_id)

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    updated_task = SimpleNamespace(
        id=task_id,
        plan_item_id=target_day_id,
        display_order=3,
        estimated_time=None,
        title="Moved Task",
    )

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.tasks.plan_tasks_services._get_max_display_order",
        return_value=2,
    ) as mock_get_max, patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_plan_item_by_id",
        return_value=SimpleNamespace(id=target_day_id),
    ) as mock_get_day, patch(
        "pecha_api.plans.tasks.plan_tasks_services._get_author_task",
        return_value=SimpleNamespace(
            id=task_id,
            plan_item_id=uuid.uuid4(),
            display_order=None,
            estimated_time=None,
            title="Moved Task",
            created_by="creator@example.com",
        ),
    ) as mock_get_author_task, patch(
        "pecha_api.plans.tasks.plan_tasks_services.update_task_day",
        return_value=updated_task,
    ) as mock_update:
        resp = await change_task_day_service(
            token="token456",
            task_id=task_id,
            update_task_request=request,
        )

        assert mock_validate.call_count == 1
        assert mock_get_max.call_count == 1
        assert mock_get_max.call_args.kwargs == {"plan_item_id": target_day_id}
        assert mock_get_day.call_count == 1
        assert mock_get_day.call_args.kwargs == {"db": db_mock, "day_id": target_day_id}
        assert mock_get_author_task.call_count == 1
        # update_task_day should be called with the mutated task instance
        assert mock_update.call_count == 1
        assert set(mock_update.call_args.kwargs.keys()) == {"db", "updated_task"}
        assert mock_update.call_args.kwargs["db"] is db_mock

        expected = UpdatedTaskDayResponse(
            task_id=updated_task.id,
            day_id=updated_task.plan_item_id,
            display_order=updated_task.display_order,
            estimated_time=updated_task.estimated_time,
            title=updated_task.title,
        )
        assert resp == expected


@pytest.mark.asyncio
async def test_change_task_day_service_day_not_found():
    task_id = uuid.uuid4()
    target_day_id = uuid.uuid4()
    request = UpdateTaskDayRequest(target_day_id=target_day_id)

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.tasks.plan_tasks_services._get_max_display_order",
        return_value=5,
    ) as mock_get_max, patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_plan_item_by_id",
        return_value=None,
    ) as mock_get_day:
        with pytest.raises(HTTPException) as exc_info:
            await change_task_day_service(
                token="token456",
                task_id=task_id,
                update_task_request=request,
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["error"] == BAD_REQUEST
        assert exc_info.value.detail["message"] == PLAN_DAY_NOT_FOUND
        assert mock_validate.call_count == 1
        assert mock_get_max.call_count == 1
        assert mock_get_day.call_count == 1


@pytest.mark.asyncio
async def test_get_task_subtasks_service_success():
    task_id = uuid.uuid4()

    subtask1 = SimpleNamespace(
        id=uuid.uuid4(),
        content_type=ContentType.TEXT,
        content="Read page 1",
        display_order=1,
    )
    subtask2 = SimpleNamespace(
        id=uuid.uuid4(),
        content_type=ContentType.VIDEO,
        content="Watch intro video",
        display_order=2,
    )

    mock_task = SimpleNamespace(
        id=task_id,
        title="Sample Task",
        display_order=2,
        estimated_time=30,
        created_by="creator@example.com",
        sub_tasks=[subtask1, subtask2],
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        return_value=SimpleNamespace(email="creator@example.com"),
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
        return_value=mock_task,
    ) as mock_get_task:
        resp = await get_task_subtasks_service(task_id=task_id, token="token789")

        assert mock_validate.call_count == 1
        assert mock_get_task.call_count == 1
        assert mock_get_task.call_args.kwargs == {"db": db_mock, "task_id": task_id}

        expected = GetTaskResponse(
            id=mock_task.id,
            title=mock_task.title,
            display_order=mock_task.display_order,
            estimated_time=mock_task.estimated_time,
            subtasks=[
                SubTaskDTO(
                    id=subtask1.id,
                    content_type=subtask1.content_type,
                    content=subtask1.content,
                    display_order=subtask1.display_order,
                ),
                SubTaskDTO(
                    id=subtask2.id,
                    content_type=subtask2.content_type,
                    content=subtask2.content,
                    display_order=subtask2.display_order,
                ),
            ],
        )
        assert resp == expected


@pytest.mark.asyncio
async def test_get_task_subtasks_service_forbidden_when_not_creator():
    task_id = uuid.uuid4()

    mock_task = SimpleNamespace(
        id=task_id,
        title="Sample Task",
        display_order=1,
        estimated_time=10,
        created_by="someone_else@example.com",
        sub_tasks=[],
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        return_value=SimpleNamespace(email="current_user@example.com"),
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
        return_value=mock_task,
    ) as mock_get_task:
        with pytest.raises(HTTPException) as exc_info:
            await get_task_subtasks_service(task_id=task_id, token="token789")

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error"] == FORBIDDEN
        assert exc_info.value.detail["message"] == UNAUTHORIZED_TASK_ACCESS

        assert mock_validate.call_count == 1
        assert mock_get_task.call_count == 1


def test__get_max_display_order_returns_zero_when_no_tasks():
    plan_item_id = uuid.uuid4()

    db_mock = MagicMock()

    # Chain: db.query(...).filter(...).scalar() -> None
    query_mock = MagicMock()
    filter_mock = MagicMock()
    filter_mock.scalar.return_value = None
    query_mock.filter.return_value = filter_mock
    db_mock.query.return_value = query_mock

    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ):
        result = _get_max_display_order(plan_item_id=plan_item_id)

    # None -> coalesce to 0
    assert result == 0
    assert db_mock.query.call_count == 1
    assert query_mock.filter.call_count == 1
    assert filter_mock.scalar.call_count == 1


def test__get_max_display_order_returns_max_value():
    plan_item_id = uuid.uuid4()

    db_mock = MagicMock()

    # Chain: db.query(...).filter(...).scalar() -> 7
    query_mock = MagicMock()
    filter_mock = MagicMock()
    filter_mock.scalar.return_value = 7
    query_mock.filter.return_value = filter_mock
    db_mock.query.return_value = query_mock

    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ):
        result = _get_max_display_order(plan_item_id=plan_item_id)

    assert result == 7
    assert db_mock.query.call_count == 1
    assert query_mock.filter.call_count == 1
    assert filter_mock.scalar.call_count == 1


    

@pytest.mark.asyncio
async def test_get_task_subtasks_service_invalid_token():
    task_id = uuid.uuid4()

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        side_effect=HTTPException(status_code=401, detail={"error": "UNAUTHORIZED", "message": "Invalid token"}),
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
    ) as mock_session, patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
    ) as mock_get_task:
        with pytest.raises(HTTPException) as exc_info:
            await get_task_subtasks_service(task_id=task_id, token="invalid")

        assert exc_info.value.status_code == 401
        assert mock_validate.call_count == 1
        assert mock_session.call_count == 0
        assert mock_get_task.call_count == 0


@pytest.mark.asyncio
async def test_get_task_subtasks_service_task_not_found():
    task_id = uuid.uuid4()

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
    ) as mock_validate, patch(
        "pecha_api.plans.tasks.plan_tasks_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
        side_effect=HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": "Task not found"}),
    ) as mock_get_task:
        with pytest.raises(HTTPException) as exc_info:
            await get_task_subtasks_service(task_id=task_id, token="token789")

        assert exc_info.value.status_code == 404
        assert mock_validate.call_count == 1
        assert mock_get_task.call_count == 1

@pytest.mark.asyncio
async def test_update_task_title_service_success():
    task_id = uuid.uuid4()
    new_title = "Updated Task Title"
    author_email = "author@example.com"
    
    request = UpdateTaskTitleRequest(title=new_title)
    
    mock_author = SimpleNamespace(
        id=uuid.uuid4(),
        email=author_email,
        first_name="John",
        last_name="Doe",
    )
    
    mock_task = SimpleNamespace(
        id=task_id,
        title="Old Title",
        created_by=author_email,
    )
    
    mock_updated_task = SimpleNamespace(
        id=task_id,
        title=new_title,
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
        "pecha_api.plans.tasks.plan_tasks_services._get_author_task",
        return_value=mock_task,
    ) as mock_get_author_task, patch(
        "pecha_api.plans.tasks.plan_tasks_services.update_task_title",
        return_value=mock_updated_task,
    ) as mock_update:
        
        result = await update_task_title_service(
            token="valid_token_123",
            task_id=task_id,
            update_request=request,
        )
        
        assert mock_validate.call_count == 1
        assert mock_validate.call_args.kwargs == {"token": "valid_token_123"}
        
        assert mock_get_author_task.call_count == 1
        # title should be set on the task object before repository call
        assert mock_task.title == new_title
        
        assert mock_update.call_count == 1
        assert mock_update.call_args.kwargs == {
            "db": db_mock,
            "updated_task": mock_task,
        }
        
        assert isinstance(result, UpdateTaskTitleResponse)
        assert result.task_id == task_id
        assert result.title == new_title


@pytest.mark.asyncio
async def test_update_task_title_service_unauthorized():
    task_id = uuid.uuid4()
    new_title = "Updated Task Title"
    author_email = "author@example.com"
    different_email = "different@example.com"
    
    request = UpdateTaskTitleRequest(title=new_title)
    
    mock_author = SimpleNamespace(
        id=uuid.uuid4(),
        email=different_email,
        first_name="Jane",
        last_name="Smith",
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
        "pecha_api.plans.tasks.plan_tasks_services._get_author_task",
        side_effect=HTTPException(status_code=403, detail={"error": FORBIDDEN, "message": UNAUTHORIZED_TASK_ACCESS}),
    ) as mock_get_author_task:
        
        with pytest.raises(HTTPException) as exc_info:
            await update_task_title_service(
                token="valid_token_123",
                task_id=task_id,
                update_request=request,
            )
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error"] == FORBIDDEN
        assert exc_info.value.detail["message"] == UNAUTHORIZED_TASK_ACCESS
        
        assert mock_validate.call_count == 1
        assert mock_get_author_task.call_count == 1


@pytest.mark.asyncio
async def test_update_task_title_service_task_not_found():
    task_id = uuid.uuid4()
    new_title = "Updated Task Title"
    
    request = UpdateTaskTitleRequest(title=new_title)
    
    mock_author = SimpleNamespace(
        id=uuid.uuid4(),
        email="author@example.com",
        first_name="John",
        last_name="Doe",
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
        "pecha_api.plans.tasks.plan_tasks_services._get_author_task",
        side_effect=HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "Task not found"}
        ),
    ) as mock_get_author_task:
        
        with pytest.raises(HTTPException) as exc_info:
            await update_task_title_service(
                token="valid_token_123",
                task_id=task_id,
                update_request=request,
            )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["error"] == "NOT_FOUND"
        
        assert mock_validate.call_count == 1
        assert mock_get_author_task.call_count == 1


@pytest.mark.asyncio
async def test_update_task_title_service_invalid_token():
    task_id = uuid.uuid4()
    new_title = "Updated Task Title"
    
    request = UpdateTaskTitleRequest(title=new_title)
    
    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.validate_and_extract_author_details",
        side_effect=HTTPException(
            status_code=401,
            detail={"error": "UNAUTHORIZED", "message": "Invalid authentication token"}
        ),
    ) as mock_validate:
        
        with pytest.raises(HTTPException) as exc_info:
            await update_task_title_service(
                token="invalid_token",
                task_id=task_id,
                update_request=request,
            )
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error"] == "UNAUTHORIZED"
        
        assert mock_validate.call_count == 1


@pytest.mark.asyncio
async def test_update_task_title_service_database_error():
    task_id = uuid.uuid4()
    new_title = "Updated Task Title"
    author_email = "author@example.com"
    
    request = UpdateTaskTitleRequest(title=new_title)
    
    mock_author = SimpleNamespace(
        id=uuid.uuid4(),
        email=author_email,
        first_name="John",
        last_name="Doe",
    )
    
    mock_task = SimpleNamespace(
        id=task_id,
        title="Old Title",
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
        "pecha_api.plans.tasks.plan_tasks_services._get_author_task",
        return_value=mock_task,
    ) as mock_get_author_task, patch(
        "pecha_api.plans.tasks.plan_tasks_services.update_task_title",
        side_effect=Exception("Database connection error"),
    ) as mock_update:
        
        with pytest.raises(Exception) as exc_info:
            await update_task_title_service(
                token="valid_token_123",
                task_id=task_id,
                update_request=request,
            )
        
        assert str(exc_info.value) == "Database connection error"
        
        assert mock_validate.call_count == 1
        assert mock_get_author_task.call_count == 1
        assert mock_update.call_count == 1


def test__reorder_sequentially_updates_only_when_needed_and_calls_repository():
    db = MagicMock()
    # Current orders: 1, 3, 3 -> should become 1, 2, 3; only second task changes
    t1 = SimpleNamespace(id=1, display_order=1)
    t2 = SimpleNamespace(id=2, display_order=3)
    t3 = SimpleNamespace(id=3, display_order=3)

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.reorder_day_tasks_display_order",
    ) as mock_repo_reorder:
        _reorder_sequentially(db=db, tasks=[t1, t2, t3])

    # Only tasks with mismatched order should be updated before calling repo
    assert t1.display_order == 1
    assert t2.display_order == 2
    assert t3.display_order == 3

    # Repository called with tasks that needed updating (t2 only)
    assert mock_repo_reorder.call_count == 1
    called_tasks = mock_repo_reorder.call_args.kwargs["tasks"]
    assert [t.id for t in called_tasks] == [2]


def test__reorder_sequentially_no_changes_does_not_call_repository():
    db = MagicMock()
    tasks = [
        SimpleNamespace(id=1, display_order=1),
        SimpleNamespace(id=2, display_order=2),
        SimpleNamespace(id=3, display_order=3),
    ]

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.reorder_day_tasks_display_order",
    ) as mock_repo_reorder:
        _reorder_sequentially(db=db, tasks=tasks)

    assert mock_repo_reorder.call_count == 0


def test__get_author_task_success():
    db = MagicMock()
    task_id = uuid.uuid4()
    current_author = SimpleNamespace(email="owner@example.com")

    # Return a task owned by current_author
    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
        return_value=SimpleNamespace(id=task_id, created_by="owner@example.com"),
    ) as mock_get:
        task = _get_author_task(db=db, task_id=task_id, current_author=current_author)

    assert task.id == task_id
    assert mock_get.call_count == 1


def test__get_author_task_not_found_raises_404():
    db = MagicMock()
    task_id = uuid.uuid4()
    current_author = SimpleNamespace(email="owner@example.com")

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc_info:
            _get_author_task(db=db, task_id=task_id, current_author=current_author)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail["error"] == BAD_REQUEST
    assert exc_info.value.detail["message"] == TASK_NOT_FOUND


def test__get_author_task_unauthorized_raises_403():
    db = MagicMock()
    task_id = uuid.uuid4()
    current_author = SimpleNamespace(email="owner@example.com")

    with patch(
        "pecha_api.plans.tasks.plan_tasks_services.get_task_by_id",
        return_value=SimpleNamespace(id=task_id, created_by="other@example.com"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            _get_author_task(db=db, task_id=task_id, current_author=current_author)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["error"] == FORBIDDEN
    assert exc_info.value.detail["message"] == UNAUTHORIZED_TASK_ACCESS


@pytest.mark.asyncio
async def test_update_task_title_service_empty_title():
    task_id = uuid.uuid4()
    author_email = "author@example.com"
    
    request = UpdateTaskTitleRequest(title="")
    
    mock_author = SimpleNamespace(
        id=uuid.uuid4(),
        email=author_email,
        first_name="John",
        last_name="Doe",
    )
    
    mock_task = SimpleNamespace(
        id=task_id,
        title="Old Title",
        created_by=author_email,
    )
    
    mock_updated_task = SimpleNamespace(
        id=task_id,
        title="",
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
        "pecha_api.plans.tasks.plan_tasks_services._get_author_task",
        return_value=mock_task,
    ) as mock_get_author_task, patch(
        "pecha_api.plans.tasks.plan_tasks_services.update_task_title",
        return_value=mock_updated_task,
    ) as mock_update:
        
        result = await update_task_title_service(
            token="valid_token_123",
            task_id=task_id,
            update_request=request,
        )
        
        assert isinstance(result, UpdateTaskTitleResponse)
        assert result.task_id == task_id
        assert result.title == ""
        
        assert mock_validate.call_count == 1
        assert mock_get_author_task.call_count == 1
        assert mock_update.call_count == 1

import uuid
import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import IntegrityError

# Ensure related mapped classes are registered for relationship resolution
from pecha_api.plans.users.plan_users_model import UserTaskCompletion as _utc_models  # noqa: F401
from pecha_api.users import users_models as _users_models  # noqa: F401

from pecha_api.plans.plans_enums import ContentType
from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO
from pecha_api.plans.tasks.plan_tasks_repository import create_task


def _make_db(max_display_order):
    db = MagicMock()
    # Chain: db.query(...).filter(...).scalar() -> max_display_order
    db.query.return_value.filter.return_value.scalar.return_value = max_display_order

    def _refresh_side_effect(obj):
        # Simulate DB assigning UUID on insert
        if not getattr(obj, "id", None):
            obj.id = str(uuid.uuid4())

    db.refresh.side_effect = _refresh_side_effect
    return db


def _patch_sessionlocal(db):
    cm = MagicMock()
    cm.__enter__.return_value = db
    cm.__exit__.return_value = False
    return patch("pecha_api.plans.tasks.plan_tasks_repository.SessionLocal", return_value=cm)


def _patch_get_plan_item(plan_item_id: str = "item-1"):
    return patch(
        "pecha_api.plans.tasks.plan_tasks_repository.get_plan_item",
        return_value=SimpleNamespace(id=plan_item_id),
    )


def _build_request() -> CreateTaskRequest:
    return CreateTaskRequest(
        title="Read intro",
        description="Do reading",
        content_type=ContentType.TEXT,
        content="Intro content",
        estimated_time=15,
    )


def test_create_task_success_with_existing_tasks():
    request = _build_request()
    db = _make_db(max_display_order=5)

    with _patch_sessionlocal(db), _patch_get_plan_item("plan-item-xyz"):
        dto: TaskDTO = create_task(
            create_task_request=request,
            plan_id="plan_1",
            day_id="day_1",
            created_by="author@example.com",
        )

    assert isinstance(dto, TaskDTO)
    assert dto.id is not None
    assert dto.title == request.title
    assert dto.description == request.description
    assert dto.content_type == request.content_type
    assert dto.content == request.content
    # max 5 -> display_order should be 6
    assert dto.display_order == 6
    assert dto.estimated_time == request.estimated_time


def test_create_task_success_when_no_existing_tasks():
    request = _build_request()
    db = _make_db(max_display_order=None)

    with _patch_sessionlocal(db), _patch_get_plan_item("plan-item-abc"):
        dto: TaskDTO = create_task(
            create_task_request=request,
            plan_id="plan_1",
            day_id="day_1",
            created_by="author@example.com",
        )

    # None -> treated as 0, so first task should be order 1
    assert dto.display_order == 1


def test_create_task_integrity_error_raises_http_exception():
    request = _build_request()
    db = _make_db(max_display_order=0)

    # Make commit raise IntegrityError
    db.commit.side_effect = IntegrityError(statement=None, params=None, orig=Exception("fail"))

    with _patch_sessionlocal(db), _patch_get_plan_item():
        with pytest.raises(Exception) as exc:
            create_task(
                create_task_request=request,
                plan_id="plan_1",
                day_id="day_1",
                created_by="author@example.com",
            )

    # Raised as FastAPI HTTPException with detail from orig
    # Cannot import HTTPException here without coupling; check message only
    assert "fail" in str(exc.value)



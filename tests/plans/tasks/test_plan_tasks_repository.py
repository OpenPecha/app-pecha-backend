import uuid
import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import IntegrityError

from pecha_api.plans.response_message import BAD_REQUEST, TASK_NOT_FOUND
# Ensure sub-task relationship backref is registered on PlanTask before repository import
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_models import PlanSubTask  # noqa: F401
from pecha_api.plans.tasks.plan_tasks_repository import (
    save_task,
    get_tasks_by_item_ids,
    get_task_by_id,
    update_task_day,
)


def test_save_task_success_sets_id_and_returns_object():
    db = MagicMock()

    def _refresh_side_effect(obj):
        if not getattr(obj, "id", None):
            obj.id = uuid.uuid4()

    db.refresh.side_effect = _refresh_side_effect

    new_task = SimpleNamespace()
    result = save_task(db=db, new_task=new_task)

    assert result is new_task
    assert getattr(result, "id", None) is not None
    assert db.add.call_count == 1
    assert db.commit.call_count == 1
    assert db.refresh.call_count == 1


def test_save_task_integrity_error_rolls_back_and_raises_http_exception():
    db = MagicMock()
    db.add.return_value = None
    db.commit.side_effect = IntegrityError(statement=None, params=None, orig=Exception("fail"))

    with pytest.raises(Exception) as exc:
        save_task(db=db, new_task=SimpleNamespace())

    assert db.rollback.call_count == 1
    from fastapi import HTTPException  # local import for assertion

    assert isinstance(exc.value, HTTPException)
    assert exc.value.status_code == 400
    assert exc.value.detail["error"] == BAD_REQUEST
    assert "fail" in exc.value.detail["message"]


def test_get_tasks_by_item_ids_empty_returns_empty_mapping():
    db = MagicMock()
    result = get_tasks_by_item_ids(db=db, plan_item_ids=[])
    assert result == {}


def test_get_tasks_by_item_ids_queries_and_returns_list():
    db = MagicMock()
    expected = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = expected

    ids = [uuid.uuid4(), uuid.uuid4()]
    result = get_tasks_by_item_ids(db=db, plan_item_ids=ids)

    assert result == expected
    assert db.query.call_count == 1


def test_get_task_by_id_queries_by_id():
    db = MagicMock()
    expected = SimpleNamespace(id=123)
    db.query.return_value.options.return_value.filter.return_value.first.return_value = expected

    task_id = uuid.uuid4()
    # Ensure repository PlanTask has the 'sub_tasks' attribute for joinedload and patch joinedload
    from pecha_api.plans.tasks.plan_tasks_repository import PlanTask as _RepoPlanTask
    setattr(_RepoPlanTask, "sub_tasks", object())
    with patch("pecha_api.plans.tasks.plan_tasks_repository.joinedload") as mock_joined:
        mock_joined.return_value = object()
        result = get_task_by_id(db=db, task_id=task_id)

    assert result is expected
    # verify filter used with correct condition object (we can't evaluate equality easily)
    assert db.query.call_count == 1


def test_update_task_day_updates_and_commits():
    db = MagicMock()
    task_id = uuid.uuid4()
    target_day_id = uuid.uuid4()

    task_obj = SimpleNamespace(id=task_id, plan_item_id=uuid.uuid4(), display_order=1)

    with patch(
        "pecha_api.plans.tasks.plan_tasks_repository.get_task_by_id",
        return_value=task_obj,
    ) as mock_get:
        result = update_task_day(db=db, task_id=task_id, target_day_id=target_day_id, display_order=5)

        assert mock_get.call_count == 1
        assert mock_get.call_args.kwargs == {"db": db, "task_id": task_id}

        assert task_obj.plan_item_id == target_day_id
        assert task_obj.display_order == 5
        assert db.commit.call_count == 1
        assert result is task_obj


def test_get_task_by_id_not_found_raises_http_404_with_payload():
    db = MagicMock()
    db.query.return_value.options.return_value.filter.return_value.first.return_value = None

    from fastapi import HTTPException

    # Ensure repository PlanTask has the 'sub_tasks' attribute for joinedload and patch joinedload
    from pecha_api.plans.tasks.plan_tasks_repository import PlanTask as _RepoPlanTask
    setattr(_RepoPlanTask, "sub_tasks", object())
    with patch("pecha_api.plans.tasks.plan_tasks_repository.joinedload") as mock_joined:
        mock_joined.return_value = object()
        with pytest.raises(HTTPException) as exc:
            get_task_by_id(db=db, task_id=uuid.uuid4())

    assert exc.value.status_code == 404
    assert exc.value.detail["error"] == BAD_REQUEST
    assert exc.value.detail["message"] == TASK_NOT_FOUND


def test_delete_task_success_deletes_and_commits():
    db = MagicMock()
    task_id = uuid.uuid4()
    task_obj = SimpleNamespace(id=task_id)

    with patch(
        "pecha_api.plans.tasks.plan_tasks_repository.get_task_by_id",
        return_value=task_obj,
    ) as mock_get:
        # After deletion, repository returns None for the deleted task
        db.query.return_value.filter.return_value.first.return_value = None

        from pecha_api.plans.tasks.plan_tasks_repository import delete_task

        result = delete_task(db=db, task_id=task_id)

        assert mock_get.call_count == 1
        assert db.delete.call_count == 1
        assert db.commit.call_count == 1
        assert result is None


def test_delete_task_error_rolls_back_and_raises_http_exception():
    db = MagicMock()
    task_id = uuid.uuid4()
    task_obj = SimpleNamespace(id=task_id)

    with patch(
        "pecha_api.plans.tasks.plan_tasks_repository.get_task_by_id",
        return_value=task_obj,
    ) as mock_get:
        db.delete.side_effect = Exception("boom")

        from fastapi import HTTPException
        from pecha_api.plans.tasks.plan_tasks_repository import delete_task

        with pytest.raises(HTTPException) as exc:
            delete_task(db=db, task_id=task_id)

        assert exc.value.status_code == 400
        assert exc.value.detail["error"] == BAD_REQUEST
        assert "boom" in exc.value.detail["message"]
        assert db.rollback.call_count == 1


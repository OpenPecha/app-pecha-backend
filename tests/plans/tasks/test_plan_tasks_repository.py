import uuid
import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError

from pecha_api.plans.tasks.plan_tasks_repository import save_task, get_tasks_by_item_ids


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
    assert "fail" in str(exc.value)


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



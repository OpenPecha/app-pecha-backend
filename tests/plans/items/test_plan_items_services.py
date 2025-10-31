import uuid
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from pecha_api.plans.items.plan_items_services import create_plan_item, delete_plan_day_by_id, update_plans_day_number
from pecha_api.plans.items.plan_items_models import PlanItem
from pecha_api.plans.items.plan_items_response_models import ItemDTO, ReorderDaysRequest, ItemDayNumberDTO


def _mock_session_local(mock_session_local):
    mock_db_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db_session
    mock_session_local.return_value.__exit__.return_value = False
    return mock_db_session


def test_create_plan_item_success():
    plan_id = uuid.uuid4()
    saved_item_id = uuid.uuid4()

    plan = MagicMock()
    plan.id = plan_id

    author = MagicMock()
    author.email = "author@example.com"

    with patch("pecha_api.plans.items.plan_items_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.items.plan_items_services.validate_and_extract_author_details") as mock_validate_author, \
         patch("pecha_api.plans.items.plan_items_services.get_plan_by_id_and_created_by") as mock_get_plan_by_id, \
         patch("pecha_api.plans.items.plan_items_services.get_last_day_number") as mock_get_last_day_number, \
         patch("pecha_api.plans.items.plan_items_services.save_plan_item") as mock_save_plan_item:
        db_session = _mock_session_local(mock_session_local)

        mock_validate_author.return_value = author
        mock_get_plan_by_id.return_value = plan
        mock_get_last_day_number.return_value = 3  # last existing day => expect new day = 4

        saved_item = MagicMock()
        saved_item.id = saved_item_id
        saved_item.plan_id = plan_id
        saved_item.day_number = 4
        mock_save_plan_item.return_value = saved_item

        resp = create_plan_item(token="dummy-token", plan_id=plan_id)

        assert mock_validate_author.call_count == 2
        mock_get_plan_by_id.assert_called_once_with(db=db_session, plan_id=plan_id, created_by=author.email)
        mock_get_last_day_number.assert_called_once_with(db=db_session, plan_id=plan_id)

        # Verify PlanItem created with correct fields and passed to repository
        mock_save_plan_item.assert_called_once()
        called_kwargs = mock_save_plan_item.call_args.kwargs
        assert called_kwargs["db"] is db_session
        created_item_arg = called_kwargs["plan_item"]
        assert isinstance(created_item_arg, PlanItem)
        assert created_item_arg.plan_id == plan_id
        assert created_item_arg.day_number == 4
        assert created_item_arg.created_by == author.email

        # Verify response mapping
        assert isinstance(resp, ItemDTO)
        assert resp.id == saved_item_id
        assert resp.plan_id == plan_id
        assert resp.day_number == 4


def test_create_plan_item_propagates_repository_error():
    plan_id = uuid.uuid4()

    plan = MagicMock()
    plan.id = plan_id

    author = MagicMock()
    author.email = "author@example.com"

    with patch("pecha_api.plans.items.plan_items_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.items.plan_items_services.validate_and_extract_author_details") as mock_validate_author, \
         patch("pecha_api.plans.items.plan_items_services.get_plan_by_id_and_created_by") as mock_get_plan_by_id, \
         patch("pecha_api.plans.items.plan_items_services.get_last_day_number") as mock_get_last_day_number, \
         patch("pecha_api.plans.items.plan_items_services.save_plan_item") as mock_save_plan_item:
        _ = _mock_session_local(mock_session_local)

        mock_validate_author.return_value = author
        mock_get_plan_by_id.return_value = plan
        mock_get_last_day_number.return_value = 0  # new day should be 1

        error = HTTPException(status_code=404, detail={"error": "Bad request", "message": "duplicate"})
        mock_save_plan_item.side_effect = error

        with pytest.raises(HTTPException) as exc_info:
            create_plan_item(token="dummy-token", plan_id=plan_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == {"error": "Bad request", "message": "duplicate"}


def test_delete_plan_day_success_reorders():
    plan_id = uuid.uuid4()
    day_id = uuid.uuid4()

    plan = MagicMock()
    plan.id = plan_id

    item_to_delete = MagicMock()
    item_to_delete.id = day_id

    # Create three items with day numbers 1, 3, 5 which should be reordered to 1,2,3 after delete
    remaining_items = [
        MagicMock(id=uuid.uuid4(), day_number=1),
        MagicMock(id=uuid.uuid4(), day_number=3),
        MagicMock(id=uuid.uuid4(), day_number=5),
    ]

    author = MagicMock()
    author.email = "author@example.com"

    with patch("pecha_api.plans.items.plan_items_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.items.plan_items_services.validate_and_extract_author_details") as mock_validate_author, \
         patch("pecha_api.plans.items.plan_items_services.get_plan_by_id_and_created_by") as mock_get_plan_by_id, \
         patch("pecha_api.plans.items.plan_items_services.get_day_by_plan_day_id") as mock_get_day, \
         patch("pecha_api.plans.items.plan_items_services.delete_day_by_id") as mock_delete, \
         patch("pecha_api.plans.items.plan_items_services.get_days_by_plan_id") as mock_get_days, \
         patch("pecha_api.plans.items.plan_items_services.update_day_by_id") as mock_update_day:
        db_session = _mock_session_local(mock_session_local)

        mock_validate_author.return_value = author
        mock_get_plan_by_id.return_value = plan
        mock_get_day.return_value = item_to_delete
        mock_get_days.return_value = remaining_items

        delete_plan_day_by_id(token="dummy-token", plan_id=plan_id, day_id=day_id)

        assert mock_validate_author.call_count == 2
        mock_get_plan_by_id.assert_called_once_with(db=db_session, plan_id=plan_id, created_by=author.email)
        mock_get_day.assert_called_once_with(db=db_session, plan_id=plan_id, day_id=day_id)
        mock_delete.assert_called_once_with(db=db_session, plan_id=plan_id, day_id=item_to_delete.id)

        # Verify reordering calls: items sorted by original day_number -> indices 1..n
        assert mock_update_day.call_count == 3
        # First call should set first item's day_number to 1, etc.
        expected_new_numbers = [1, 2, 3]
        for call, new_num in zip(mock_update_day.call_args_list, expected_new_numbers):
            kwargs = call.kwargs
            assert kwargs["db"] is db_session
            assert kwargs["plan_id"] == plan_id
            assert "day_id" in kwargs and kwargs["day_id"] is not None
            assert kwargs["day_number"] == new_num


def test_delete_plan_day_not_found():
    plan_id = uuid.uuid4()
    day_id = uuid.uuid4()

    plan = MagicMock()
    plan.id = plan_id

    author = MagicMock()
    author.email = "author@example.com"

    with patch("pecha_api.plans.items.plan_items_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.items.plan_items_services.validate_and_extract_author_details") as mock_validate_author, \
         patch("pecha_api.plans.items.plan_items_services.get_plan_by_id_and_created_by") as mock_get_plan_by_id, \
         patch("pecha_api.plans.items.plan_items_services.get_day_by_plan_day_id") as mock_get_day:
        _ = _mock_session_local(mock_session_local)

        mock_validate_author.return_value = author
        mock_get_plan_by_id.return_value = plan
        mock_get_day.side_effect = HTTPException(status_code=404, detail={"error": "Not Found", "message": "day not found"})

        with pytest.raises(HTTPException) as exc_info:
            delete_plan_day_by_id(token="dummy-token", plan_id=plan_id, day_id=day_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == {"error": "Not Found", "message": "day not found"}


def test_delete_plan_day_auth_error():
    plan_id = uuid.uuid4()
    day_id = uuid.uuid4()

    with patch("pecha_api.plans.items.plan_items_services.validate_and_extract_author_details") as mock_validate_author:
        mock_validate_author.side_effect = HTTPException(status_code=401, detail="Unauthorized")

        with pytest.raises(HTTPException) as exc_info:
            delete_plan_day_by_id(token="bad-token", plan_id=plan_id, day_id=day_id)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Unauthorized"


def test_delete_plan_day_repository_error():
    plan_id = uuid.uuid4()
    day_id = uuid.uuid4()

    plan = MagicMock()
    plan.id = plan_id

    item_to_delete = MagicMock()
    item_to_delete.id = day_id

    author = MagicMock()
    author.email = "author@example.com"

    with patch("pecha_api.plans.items.plan_items_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.items.plan_items_services.validate_and_extract_author_details") as mock_validate_author, \
         patch("pecha_api.plans.items.plan_items_services.get_plan_by_id_and_created_by") as mock_get_plan_by_id, \
         patch("pecha_api.plans.items.plan_items_services.get_day_by_plan_day_id") as mock_get_day, \
         patch("pecha_api.plans.items.plan_items_services.delete_day_by_id") as mock_delete:
        _ = _mock_session_local(mock_session_local)

        mock_validate_author.return_value = author
        mock_get_plan_by_id.return_value = plan
        mock_get_day.return_value = item_to_delete
        mock_delete.side_effect = HTTPException(status_code=400, detail={"error": "Bad request", "message": "cannot delete"})

        with pytest.raises(HTTPException) as exc_info:
            delete_plan_day_by_id(token="dummy-token", plan_id=plan_id, day_id=day_id)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == {"error": "Bad request", "message": "cannot delete"}


def test_update_plans_day_number_success_calls_bulk_update():
    plan_id = uuid.uuid4()

    plan = MagicMock()
    plan.id = plan_id

    author = MagicMock()
    author.email = "author@example.com"

    payload = ReorderDaysRequest(
        days=[
            ItemDayNumberDTO(id=uuid.uuid4(), day_number=1),
            ItemDayNumberDTO(id=uuid.uuid4(), day_number=2),
            ItemDayNumberDTO(id=uuid.uuid4(), day_number=3),
        ]
    )

    with patch("pecha_api.plans.items.plan_items_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.items.plan_items_services.validate_and_extract_author_details") as mock_validate_author, \
         patch("pecha_api.plans.items.plan_items_services.get_plan_by_id_and_created_by") as mock_get_plan_by_id, \
         patch("pecha_api.plans.items.plan_items_services.update_days_in_bulk_by_plan_id") as mock_bulk_update:
        db_session = _mock_session_local(mock_session_local)

        mock_validate_author.return_value = author
        mock_get_plan_by_id.return_value = plan

        update_plans_day_number(token="dummy-token", plan_id=plan_id, reorder_days_request=payload)

        # validate called twice (directly and via _get_author_plan)
        assert mock_validate_author.call_count == 2
        mock_get_plan_by_id.assert_called_once_with(db=db_session, plan_id=plan_id, created_by=author.email)
        mock_bulk_update.assert_called_once()
        called_kwargs = mock_bulk_update.call_args.kwargs
        assert called_kwargs["db"] is db_session
        assert called_kwargs["days"] == payload.days


def test_update_plans_day_number_duplicate_payload_raises_400():
    plan_id = uuid.uuid4()

    payload = ReorderDaysRequest(
        days=[
            ItemDayNumberDTO(id=uuid.uuid4(), day_number=1),
            ItemDayNumberDTO(id=uuid.uuid4(), day_number=1),  # duplicate
        ]
    )

    plan = MagicMock()
    plan.id = plan_id

    with patch("pecha_api.plans.items.plan_items_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.items.plan_items_services.validate_and_extract_author_details") as mock_validate_author, \
         patch("pecha_api.plans.items.plan_items_services.get_plan_by_id_and_created_by") as mock_get_plan_by_id:
        _ = _mock_session_local(mock_session_local)

        mock_validate_author.return_value = MagicMock(email="author@example.com")
        mock_get_plan_by_id.return_value = plan

        with pytest.raises(HTTPException) as exc_info:
            update_plans_day_number(token="dummy-token", plan_id=plan_id, reorder_days_request=payload)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == {"error": "Bad request", "message": "Duplicate day numbers"}
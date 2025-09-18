import uuid
import pytest
from unittest.mock import patch, MagicMock, ANY

from pecha_api.plans.items.plan_items_services import create_plan_item
from pecha_api.plans.items.plan_items_models import PlanItem
from pecha_api.plans.items.plan_items_response_models import ItemDTO


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
         patch("pecha_api.plans.items.plan_items_services.get_plan_by_id") as mock_get_plan_by_id, \
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

        mock_validate_author.assert_called_once_with(token="dummy-token")
        mock_get_plan_by_id.assert_called_once_with(db=db_session, plan_id=plan_id)
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

import uuid
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from starlette import status

from pecha_api.plans.public.plan_service import get_plan_days
from pecha_api.plans.public.plan_response_models import PlanDaysResponse
from pecha_api.error_contants import ErrorConstants


def _mock_session_local(mock_session_local):
    """Helper function to mock SessionLocal context manager"""
    mock_db_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db_session
    mock_session_local.return_value.__exit__.return_value = False
    return mock_db_session


@pytest.mark.asyncio
async def test_get_plan_days_success():
    """Test successful retrieval of plan days"""
    token = "valid_token_123"
    plan_id = uuid.uuid4()
    
    mock_plan = MagicMock()
    mock_plan.id = plan_id
    mock_plan.title = "Test Plan"
    
    mock_day_1 = MagicMock()
    mock_day_1.id = uuid.uuid4()
    mock_day_1.day_number = 1
    
    mock_day_2 = MagicMock()
    mock_day_2.id = uuid.uuid4()
    mock_day_2.day_number = 2
    
    mock_plan_days = [mock_day_1, mock_day_2]
    
    mock_user = MagicMock()
    mock_user.id = uuid.uuid4()
    mock_user.email = "test@example.com"

    with patch("pecha_api.plans.public.plan_service.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.public.plan_service.validate_and_extract_user_details") as mock_validate_user, \
         patch("pecha_api.plans.public.plan_service.get_plan_by_id") as mock_get_plan, \
         patch("pecha_api.plans.public.plan_service.get_days_by_plan_id") as mock_get_days:
        
        db_session = _mock_session_local(mock_session_local)
        mock_validate_user.return_value = mock_user
        mock_get_plan.return_value = mock_plan
        mock_get_days.return_value = mock_plan_days

        response = await get_plan_days(token=token, plan_id=plan_id)

        mock_validate_user.assert_called_once_with(token=token)
        
        mock_get_plan.assert_called_once_with(db=db_session, plan_id=plan_id)
        mock_get_days.assert_called_once_with(db=db_session, plan_id=plan_id)

        assert isinstance(response, PlanDaysResponse)
        assert len(response.days) == 2
        
        assert response.days[0].id == str(mock_day_1.id)
        assert response.days[0].day_number == 1
        assert response.days[1].id == str(mock_day_2.id)
        assert response.days[1].day_number == 2


@pytest.mark.asyncio
async def test_get_plan_days_empty_days():
    """Test retrieval when plan has no days"""
    token = "valid_token_456"
    plan_id = uuid.uuid4()
    
    mock_plan = MagicMock()
    mock_plan.id = plan_id
    mock_plan.title = "Empty Plan"
    
    mock_user = MagicMock()
    mock_user.id = uuid.uuid4()

    with patch("pecha_api.plans.public.plan_service.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.public.plan_service.validate_and_extract_user_details") as mock_validate_user, \
         patch("pecha_api.plans.public.plan_service.get_plan_by_id") as mock_get_plan, \
         patch("pecha_api.plans.public.plan_service.get_days_by_plan_id") as mock_get_days:
        
        db_session = _mock_session_local(mock_session_local)
        mock_validate_user.return_value = mock_user
        mock_get_plan.return_value = mock_plan
        mock_get_days.return_value = []

        response = await get_plan_days(token=token, plan_id=plan_id)

        mock_validate_user.assert_called_once_with(token=token)
        mock_get_plan.assert_called_once_with(db=db_session, plan_id=plan_id)
        mock_get_days.assert_called_once_with(db=db_session, plan_id=plan_id)

        assert isinstance(response, PlanDaysResponse)
        assert len(response.days) == 0


@pytest.mark.asyncio
async def test_get_plan_days_plan_not_found():
    """Test when plan does not exist"""
    token = "valid_token_789"
    plan_id = uuid.uuid4()
    
    mock_user = MagicMock()
    mock_user.id = uuid.uuid4()

    with patch("pecha_api.plans.public.plan_service.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.public.plan_service.validate_and_extract_user_details") as mock_validate_user, \
         patch("pecha_api.plans.public.plan_service.get_plan_by_id") as mock_get_plan:
        
        db_session = _mock_session_local(mock_session_local)
        mock_validate_user.return_value = mock_user
        mock_get_plan.return_value = None 

        with pytest.raises(HTTPException) as exc_info:
            await get_plan_days(token=token, plan_id=plan_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.PLAN_NOT_FOUND

        mock_validate_user.assert_called_once_with(token=token)
        mock_get_plan.assert_called_once_with(db=db_session, plan_id=plan_id)
import uuid
import pytest
from unittest.mock import patch, AsyncMock

from pecha_api.plans.public.plan_models import PlanDaysResponse, PlanDayBasic
from pecha_api.plans.public.plan_views import get_plan_days_list


class _Creds:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_get_plan_days_list_success():
    """Test successful retrieval of plan days list"""
    creds = _Creds(token="valid_token_123")
    plan_id = uuid.uuid4()
    
    expected_days = [
        PlanDayBasic(id=str(uuid.uuid4()), day_number=1),
        PlanDayBasic(id=str(uuid.uuid4()), day_number=2),
    ]
    expected_response = PlanDaysResponse(days=expected_days)

    with patch(
        "pecha_api.plans.public.plan_views.get_plan_days",
        return_value=expected_response,
        new_callable=AsyncMock,
    ) as mock_service:
        response = await get_plan_days_list(
            authentication_credential=creds,
            plan_id=plan_id
        )

        mock_service.assert_called_once_with(
            token="valid_token_123",
            plan_id=plan_id
        )

        assert response == expected_response
        assert len(response.days) == 2
        assert response.days[0].day_number == 1
        assert response.days[1].day_number == 2


@pytest.mark.asyncio
async def test_get_plan_days_list_empty_days():
    """Test retrieval when plan has no days"""
    creds = _Creds(token="valid_token_456")
    plan_id = uuid.uuid4()
    
    expected_response = PlanDaysResponse(days=[])

    with patch(
        "pecha_api.plans.public.plan_views.get_plan_days",
        return_value=expected_response,
        new_callable=AsyncMock,
    ) as mock_service:
        response = await get_plan_days_list(
            authentication_credential=creds,
            plan_id=plan_id
        )

        mock_service.assert_called_once_with(
            token="valid_token_456",
            plan_id=plan_id
        )

        assert response == expected_response
        assert len(response.days) == 0

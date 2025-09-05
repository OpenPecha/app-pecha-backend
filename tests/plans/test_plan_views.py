import uuid
import pytest
from unittest.mock import patch, MagicMock

from pecha_api.plans.plans_enums import DifficultyLevel, PlanStatus
from pecha_api.plans.plans_response_models import CreatePlanRequest, PlanDTO
from pecha_api.plans.plans_views import create_plan


class _Creds:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_create_plan_success():
    request = CreatePlanRequest(
        title="Mindfulness Basics",
        description="A simple plan to get started with mindfulness.",
        difficulty_level=DifficultyLevel.BEGINNER,
        total_days=7,
        language="en",
        image_url="https://example.com/image.jpg",
        tags=["mindfulness", "beginner"],
    )

    plan_id = uuid.uuid4()
    expected = PlanDTO(
        id=plan_id,
        title=request.title,
        description=request.description,
        image_url=request.image_url,
        total_days=0,
        status=PlanStatus.DRAFT,
        subscription_count=0,
    )

    creds = _Creds(token="token123")

    with patch("pecha_api.plans.plans_views.create_new_plan", return_value=expected) as mock_create:
        response = await create_plan(authentication_credential=creds, create_plan_request=request)

        mock_create.assert_called_once_with(token="token123", create_plan_request=request)

        assert response is not None
        assert isinstance(response, PlanDTO)
        assert response.id == plan_id
        assert response.title == request.title
        assert response.description == request.description
        assert response.image_url == request.image_url
        assert response.total_days == 0
        assert response.status == PlanStatus.DRAFT
        assert response.subscription_count == 0



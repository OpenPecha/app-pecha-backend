import uuid
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from pecha_api.plans.plans_enums import DifficultyLevel, PlanStatus, SortBy, SortOrder
from pecha_api.plans.plans_response_models import CreatePlanRequest, PlanDTO, PlansResponse
from pecha_api.plans.plans_views import create_plan, get_plans


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



@pytest.mark.asyncio
async def test_get_plans_success_with_params():
    creds = _Creds(token="token123")

    plan1 = PlanDTO(
        id=uuid.uuid4(),
        title="Plan One",
        description="Desc 1",
        image_url="https://example.com/1.jpg",
        total_days=0,
        status=PlanStatus.PUBLISHED,
        subscription_count=0,
    )
    plan2 = PlanDTO(
        id=uuid.uuid4(),
        title="Plan Two",
        description="Desc 2",
        image_url="https://example.com/2.jpg",
        total_days=0,
        status=PlanStatus.DRAFT,
        subscription_count=0,
    )
    expected = PlansResponse(plans=[plan1, plan2], skip=1, limit=5, total=2)

    with patch("pecha_api.plans.plans_views.get_filtered_plans", return_value=expected, new_callable=AsyncMock) as mock_service:
        resp = await get_plans(
            authentication_credential=creds,
            search="plan",
            sort_by=SortBy.TITLE,
            sort_order=SortOrder.ASC,
            skip=1,
            limit=5,
        )

        mock_service.assert_awaited_once_with(
            token="token123",
            search="plan",
            sort_by=SortBy.TITLE,
            sort_order=SortOrder.ASC,
            skip=1,
            limit=5,
        )

        assert resp == expected


@pytest.mark.asyncio
async def test_get_plans_defaults():
    creds = _Creds(token="tkn")
    expected = PlansResponse(plans=[], skip=0, limit=10, total=0)

    with patch("pecha_api.plans.plans_views.get_filtered_plans", return_value=expected, new_callable=AsyncMock) as mock_service:
        resp = await get_plans(authentication_credential=creds, search=None, sort_by=None, sort_order=None, skip=0, limit=10)

        mock_service.assert_awaited_once_with(
            token="tkn",
            search=None,
            sort_by=None,
            sort_order=None,
            skip=0,
            limit=10,
        )
        assert resp == expected


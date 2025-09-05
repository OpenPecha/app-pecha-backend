import uuid
from unittest.mock import patch, MagicMock, ANY

from pecha_api.plans.plans_enums import DifficultyLevel, PlanStatus
from pecha_api.plans.plans_response_models import CreatePlanRequest
from pecha_api.plans.plans_service import create_new_plan


def _mock_session_local(mock_session_local):
    mock_db_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db_session
    mock_session_local.return_value.__exit__.return_value = False
    return mock_db_session


def test_create_new_plan_success():
    request = CreatePlanRequest(
        title="Mindfulness Basics",
        description="A simple plan to get started with mindfulness.",
        difficulty_level=DifficultyLevel.BEGINNER,
        total_days=7,
        language="en",
        image_url="https://example.com/image.jpg",
        tags=["mindfulness", "beginner"],
    )

    saved_plan = MagicMock()
    saved_plan.id = uuid.uuid4()
    saved_plan.title = request.title
    saved_plan.description = request.description
    saved_plan.image_url = request.image_url
    saved_plan.status = PlanStatus.DRAFT

    with patch("pecha_api.plans.plans_service.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.plans_service.save_plan") as mock_save_plan:
        db_session = _mock_session_local(mock_session_local)
        mock_save_plan.return_value = saved_plan

        response = create_new_plan(token="dummy", create_plan_request=request)

        # verify repository interactions
        mock_save_plan.assert_called_once_with(db=db_session, plan=ANY)
        called_kwargs = mock_save_plan.call_args.kwargs
        created_plan_model = called_kwargs["plan"]
        assert created_plan_model.title == request.title
        assert created_plan_model.description == request.description
        assert created_plan_model.image_url == request.image_url
        assert created_plan_model.author_id is not None and str(created_plan_model.author_id) != ""

        # verify response mapping
        assert response is not None
        assert response.id == saved_plan.id
        assert response.title == request.title
        assert response.description == request.description
        assert response.image_url == request.image_url
        assert response.total_days == 0
        assert response.status == PlanStatus.DRAFT
        assert response.subscription_count == 0



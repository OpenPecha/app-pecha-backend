import uuid
import pytest
from unittest.mock import patch, MagicMock, ANY
from fastapi import HTTPException

import pecha_api.plans.cms.cms_plans_service as plans_service
from pecha_api.plans.plans_enums import DifficultyLevel, PlanStatus, ContentType
from pecha_api.plans.plans_models import Plan
from pecha_api.plans.items.plan_items_models import PlanItem
from pecha_api.plans.tasks.plan_tasks_models import PlanTask
from pecha_api.plans.plans_response_models import (
    CreatePlanRequest, UpdatePlanRequest, PlanStatusUpdate,
    PlanDTO,PlanWithAggregates, PlansRepositoryResponse
)
from pecha_api.plans.cms.cms_plans_service import (
    create_new_plan, get_filtered_plans, get_details_plan,
    update_plan_details, update_selected_plan_status, delete_selected_plan,
    DUMMY_PLANS, DUMMY_DAYS
)


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
    saved_plan.language = request.language
    saved_plan.status = PlanStatus.DRAFT

    with patch("pecha_api.plans.cms.cms_plans_service.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.cms.cms_plans_service.save_plan") as mock_save_plan, \
        patch("pecha_api.plans.cms.cms_plans_service.save_plan_items") as mock_save_plan_items, \
        patch("pecha_api.plans.cms.cms_plans_service.get_plan_progress") as mock_get_plan_progress, \
        patch("pecha_api.plans.cms.cms_plans_service.validate_and_extract_author_details") as mock_validate_author:
        db_session = _mock_session_local(mock_session_local)
        mock_save_plan.return_value = saved_plan
        # save_plan_items returns the list of saved items; return a list sized to total_days
        mock_save_plan_items.return_value = [MagicMock() for _ in range(request.total_days)]
        mock_get_plan_progress.return_value = []

        author = MagicMock()
        author.id = uuid.uuid4()
        author.email = "author@example.com"
        mock_validate_author.return_value = author

        response = create_new_plan(token="dummy", create_plan_request=request)

        mock_validate_author.assert_called_once_with(token="dummy")
        mock_get_plan_progress.assert_called_once_with(db=db_session, plan_id=saved_plan.id)

        # verify repository interactions - plan
        mock_save_plan.assert_called_once_with(db=db_session, plan=ANY)
        called_kwargs = mock_save_plan.call_args.kwargs
        created_plan_model = called_kwargs["plan"]
        assert created_plan_model.title == request.title
        assert created_plan_model.description == request.description
        assert created_plan_model.image_url == request.image_url
        assert created_plan_model.author_id is not None and str(created_plan_model.author_id) != ""

        # verify repository interactions - plan items (bulk)
        mock_save_plan_items.assert_called_once_with(db=db_session, plan_items=ANY)
        called_item_kwargs = mock_save_plan_items.call_args.kwargs
        created_plan_items = called_item_kwargs["plan_items"]
        assert isinstance(created_plan_items, list)
        assert len(created_plan_items) == request.total_days
        # verify each generated PlanItem model
        expected_days = list(range(1, request.total_days + 1))
        actual_days = [item.day_number for item in created_plan_items]
        assert actual_days == expected_days
        assert all(item.plan_id == saved_plan.id for item in created_plan_items)
        assert all(item.created_by == author.email for item in created_plan_items)

        # verify response mapping
        assert response is not None
        assert response.id == saved_plan.id
        assert response.title == request.title
        assert response.description == request.description
        assert response.image_url == request.image_url
        assert response.total_days == request.total_days
        assert response.status == PlanStatus.DRAFT
        assert response.subscription_count == 0



@pytest.mark.asyncio
async def test_get_filtered_plans_success():
    plan1 = Plan(
        id=uuid.uuid4(),
        title="Plan One",
        description="Description One",
        image_url="https://example.com/one.jpg",
        status=PlanStatus.PUBLISHED,
        author_id=uuid.uuid4(),
        created_by="tester@example.com",
    )

    plan2 = Plan(
        id=uuid.uuid4(),
        title="Plan Two",
        description="Description Two",
        language="en",
        image_url="https://example.com/two.jpg",
        status=PlanStatus.DRAFT,
        author_id=uuid.uuid4(),
        created_by="tester@example.com",
    )

    # Repository now returns PlansRepositoryResponse with PlanWithAggregates items
    repo_response = PlansRepositoryResponse(
        plan_info=[
            PlanWithAggregates(plan=plan1, total_days=5, subscription_count=2),
            PlanWithAggregates(plan=plan2, total_days=0, subscription_count=0),
        ],
        total=2,
    )

    with patch("pecha_api.plans.cms.cms_plans_service.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.cms.cms_plans_service.get_plans") as mock_get_plans, \
        patch("pecha_api.plans.cms.cms_plans_service.validate_and_extract_author_details") as mock_validate_author, \
        patch("pecha_api.plans.cms.cms_plans_service.generate_presigned_access_url") as mock_presign, \
        patch("pecha_api.plans.cms.cms_plans_service.get") as mock_get_config:
        db_session = _mock_session_local(mock_session_local)
        mock_get_plans.return_value = repo_response
        mock_validate_author.return_value = MagicMock()
        # Return the original key so assertions comparing to plan.image_url still pass
        mock_presign.side_effect = lambda bucket_name, s3_key: s3_key
        mock_get_config.return_value = "dummy-bucket"

        resp = await get_filtered_plans(
            token="dummy-token",
            search="plan",
            sort_by="created_at",
            sort_order="desc",
            skip=5,
            limit=10,
        )

        mock_validate_author.assert_called_once_with(token="dummy-token")

        # verify repository interaction
        mock_get_plans.assert_called_once()
        called_kwargs = mock_get_plans.call_args.kwargs
        assert called_kwargs == {
            "db": db_session,
            "search": "plan",
            "sort_by": "created_at",
            "sort_order": "desc",
            "skip": 5,
            "limit": 10,
        }

        # verify response mapping
        assert resp is not None
        assert resp.skip == 5
        assert resp.limit == 10
        assert resp.total == 2
        assert len(resp.plans) == 2

        p1 = resp.plans[0]
        assert p1.id == plan1.id
        assert p1.title == plan1.title
        assert p1.description == plan1.description
        assert p1.image_url == plan1.image_url
        assert p1.total_days == 5
        assert p1.status == PlanStatus.PUBLISHED
        assert p1.subscription_count == 2
        # language fallback to default when missing on plan
        assert p1.language == "EN"

        p2 = resp.plans[1]
        assert p2.id == plan2.id
        assert p2.status == PlanStatus.DRAFT
        # language preserved when provided on plan
        assert p2.language == "en"


@pytest.mark.asyncio
async def test_get_details_plan_success():
    plan = Plan(
        id=uuid.uuid4(),
        title="Test Plan",
        description="Test Description",
        image_url="https://example.com/image.jpg",
        status=PlanStatus.PUBLISHED,
        author_id=uuid.uuid4(),
        created_by="tester@example.com",
    )

    item1 = PlanItem(id=uuid.uuid4(), plan_id=plan.id, day_number=1, created_by="tester@example.com")
    item2 = PlanItem(id=uuid.uuid4(), plan_id=plan.id, day_number=2, created_by="tester@example.com")

    task1 = PlanTask(
        id=uuid.uuid4(),
        plan_item_id=item1.id,
        title="Morning Practice",
        content_type=ContentType.TEXT,
        content="Breathe for 10 minutes",
        display_order=1,
        estimated_time=10,
        created_by="tester@example.com",
    )
    task2 = PlanTask(
        id=uuid.uuid4(),
        plan_item_id=item2.id,
        title="Listen Audio",
        content_type=ContentType.AUDIO,
        content="https://example.com/audio.mp3",
        display_order=1,
        estimated_time=20,
        created_by="tester@example.com",
    )

    with patch("pecha_api.plans.cms.cms_plans_service.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.cms.cms_plans_service.get_plan_by_id") as mock_get_plan_by_id, \
        patch("pecha_api.plans.cms.cms_plans_service.get_plan_items_by_plan_id") as mock_get_plan_items_by_plan_id, \
        patch("pecha_api.plans.cms.cms_plans_service.get_tasks_by_item_ids") as mock_get_tasks_by_item_ids, \
        patch("pecha_api.plans.cms.cms_plans_service.validate_and_extract_author_details") as mock_validate_author:
        db_session = _mock_session_local(mock_session_local)
        mock_validate_author.return_value = MagicMock()
        mock_get_plan_by_id.return_value = plan
        mock_get_plan_items_by_plan_id.return_value = [item1, item2]
        mock_get_tasks_by_item_ids.return_value = [task1, task2]

        response = await get_details_plan(token="dummy-token", plan_id=plan.id)

        mock_validate_author.assert_called_once_with(token="dummy-token")
        mock_get_plan_by_id.assert_called_once_with(db=db_session, plan_id=plan.id)
        mock_get_plan_items_by_plan_id.assert_called_once_with(db=db_session, plan_id=plan.id)
        mock_get_tasks_by_item_ids.assert_called_once_with(db=db_session, plan_item_ids=[item1.id, item2.id])

        assert response is not None
        assert response.id == plan.id
        assert response.title == plan.title
        assert response.description == plan.description
        assert response.total_days == 2
        assert len(response.days) == 2

        day1 = next(d for d in response.days if d.id == item1.id)
        assert day1.day_number == 1
        assert len(day1.tasks) == 1
        assert day1.tasks[0].id == task1.id
        assert day1.tasks[0].title == task1.title
        assert day1.tasks[0].estimated_time == task1.estimated_time

        day2 = next(d for d in response.days if d.id == item2.id)
        assert day2.day_number == 2
        assert len(day2.tasks) == 1
        assert day2.tasks[0].id == task2.id
        assert day2.tasks[0].estimated_time == task2.estimated_time
@pytest.mark.asyncio
async def test_get_details_plan_not_found():
    non_existent_id = uuid.uuid4()


    with patch("pecha_api.plans.cms.cms_plans_service.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.cms.cms_plans_service.get_plan_by_id") as mock_get_plan_by_id, \
        patch("pecha_api.plans.cms.cms_plans_service.validate_and_extract_author_details") as mock_validate_author:
        _ = _mock_session_local(mock_session_local)

        mock_validate_author.return_value = MagicMock()
        mock_get_plan_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_details_plan(token="dummy-token", plan_id=non_existent_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == {"error": "Bad request", "message": "Plan not found"}


@pytest.mark.asyncio
async def test_update_plan_details_success():
    # Get a test plan from DUMMY_PLANS
    test_plan = DUMMY_PLANS[0]
    
    update_request = UpdatePlanRequest(
        title="Updated Title",
        description="Updated Description",
        total_days=10,
        image_url="https://example.com/updated.jpg"
    )
    
    with patch("pecha_api.plans.cms.cms_plans_service.validate_and_extract_author_details") as mock_validate_author:
        mock_validate_author.return_value = MagicMock()
        
        response = await update_plan_details(
            token="dummy-token",
            plan_id=test_plan.id,
            update_plan_request=update_request
        )
        
        # Verify response
        assert response is not None
        assert response.id == test_plan.id
        assert response.title == update_request.title
        assert response.description == update_request.description
        assert response.total_days == update_request.total_days
        assert response.image_url == update_request.image_url


@pytest.mark.asyncio
async def test_update_plan_details_not_found():
    non_existent_id = uuid.uuid4()
    update_request = UpdatePlanRequest(title="Updated Title")
    
    with patch("pecha_api.plans.cms.cms_plans_service.validate_and_extract_author_details") as mock_validate_author:
        mock_validate_author.return_value = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            await update_plan_details(
                token="dummy-token",
                plan_id=non_existent_id,
                update_plan_request=update_request
            )
        
        assert exc_info.value.status_code == 404
        assert "Plan not found" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_update_selected_plan_status_success():
    # Get a test plan from DUMMY_PLANS
    test_plan = DUMMY_PLANS[0]
    
    status_update = PlanStatusUpdate(status=PlanStatus.PUBLISHED)
    
    with patch("pecha_api.plans.cms.cms_plans_service.validate_and_extract_author_details") as mock_validate_author:
        mock_validate_author.return_value = MagicMock()
        
        response = await update_selected_plan_status(
            token="dummy-token",
            plan_id=test_plan.id,
            plan_status_update=status_update
        )
        
        # Verify response
        assert response is not None
        assert response.id == test_plan.id
        assert response.status == PlanStatus.PUBLISHED


@pytest.mark.asyncio
async def test_update_selected_plan_status_invalid_transition():
    # Ensure a plan with zero days exists
    zero_day_plan = next((p for p in DUMMY_PLANS if getattr(p, "total_days", 0) == 0), None)
    if zero_day_plan is None:
        # Inject a zero-day plan for this test
        zero_day_plan = PlanDTO(
            id=uuid.uuid4(),
            title="Zero Day Plan",
            description="Should not publish",
            language="en",
            image_url="https://example.com/zero.jpg",
            total_days=0,
            status=PlanStatus.DRAFT,
            subscription_count=0
        )
        DUMMY_PLANS.append(zero_day_plan)

    status_update = PlanStatusUpdate(status=PlanStatus.PUBLISHED)
    
    with patch("pecha_api.plans.cms.cms_plans_service.validate_and_extract_author_details") as mock_validate_author:
        mock_validate_author.return_value = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            await update_selected_plan_status(
                token="dummy-token",
                plan_id=zero_day_plan.id,
                plan_status_update=status_update
            )
        
        assert exc_info.value.status_code == 400
        assert "must have at least one day with content" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_delete_selected_plan_success():
    # Get a test plan from DUMMY_PLANS
    test_plan = DUMMY_PLANS[0]
    initial_plan_count = len(DUMMY_PLANS)
    
    with patch("pecha_api.plans.cms.cms_plans_service.validate_and_extract_author_details") as mock_validate_author:
        mock_validate_author.return_value = MagicMock()
        
        await delete_selected_plan(token="dummy-token", plan_id=test_plan.id)
        
        # Verify plan was removed from DUMMY_PLANS
        assert len(plans_service.DUMMY_PLANS) == initial_plan_count - 1
        assert not any(p.id == test_plan.id for p in plans_service.DUMMY_PLANS)


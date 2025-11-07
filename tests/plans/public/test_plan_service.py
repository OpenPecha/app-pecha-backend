"""
Test suite for public plan service functions.

Tests the following service functions:
1. get_published_plans() - Retrieve published plans with filtering and sorting
2. get_published_plan() - Retrieve single published plan by ID
"""

import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock, Mock
from fastapi import HTTPException
from starlette import status

from pecha_api.plans.public.plan_service import get_published_plans, get_published_plan
from pecha_api.plans.plans_response_models import PlansResponse, PlanDTO, AuthorDTO, PlanWithAggregates
from pecha_api.plans.plans_models import Plan
from pecha_api.plans.authors.plan_authors_model import Author
from pecha_api.plans.plans_enums import PlanStatus, DifficultyLevel, LanguageCode
from pecha_api.error_contants import ErrorConstants


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_author():
    """Sample author model for testing."""
    author = Author(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        image_url="images/author_avatars/author-id/avatar.jpg",
        is_verified=True
    )
    return author


@pytest.fixture
def sample_plan(sample_author):
    """Sample plan model for testing."""
    plan = Plan(
        id=uuid4(),
        title="Introduction to Meditation",
        description="A comprehensive guide to meditation practices",
        language=LanguageCode.EN,
        difficulty_level=DifficultyLevel.BEGINNER,
        image_url="images/plan_images/plan-id/uuid/image.jpg",
        status=PlanStatus.PUBLISHED,
        tags=["meditation", "mindfulness", "beginner"],
        author_id=sample_author.id,
        author=sample_author,
        deleted_at=None
    )
    return plan


@pytest.fixture
def sample_plan_aggregate(sample_plan):
    """Sample plan aggregate for testing."""
    return PlanWithAggregates(
        plan=sample_plan,
        total_days=30,
        subscription_count=150
    )


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = MagicMock()
    session.__enter__ = Mock(return_value=session)
    session.__exit__ = Mock(return_value=None)
    return session


# ============================================================================
# get_published_plans() Service Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_published_plans_success(sample_plan_aggregate, mock_db_session):
    """Test successful retrieval of published plans."""
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[sample_plan_aggregate]) as mock_repo, \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=1), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value="https://bucket.s3.amazonaws.com/presigned-url") as mock_plan_url, \
         patch("pecha_api.plans.public.plan_service.generate_author_avatar_url", return_value="https://bucket.s3.amazonaws.com/author-presigned-url") as mock_author_url:
        
        result = await get_published_plans(
            search=None,
            language=None,
            sort_by="title",
            sort_order="asc",
            skip=0,
            limit=20
        )
        
        # Verify result structure
        assert isinstance(result, PlansResponse)
        assert len(result.plans) == 1
        assert result.skip == 0
        assert result.limit == 20
        assert result.total == 1
        
        # Verify plan DTO
        plan_dto = result.plans[0]
        assert plan_dto.title == "Introduction to Meditation"
        assert plan_dto.language == "en"
        assert plan_dto.total_days == 30
        assert plan_dto.subscription_count == 150
        assert plan_dto.image_url == "https://bucket.s3.amazonaws.com/presigned-url"
        assert plan_dto.image_key == "images/plan_images/plan-id/uuid/image.jpg"
        
        # Verify author DTO
        assert plan_dto.author is not None
        assert plan_dto.author.firstname == "John"
        assert plan_dto.author.lastname == "Doe"
        assert plan_dto.author.image_url == "https://bucket.s3.amazonaws.com/author-presigned-url"
        assert plan_dto.author.image_key == "images/author_avatars/author-id/avatar.jpg"
        
        # Verify repository was called correctly
        mock_repo.assert_called_once_with(
            db=mock_db_session.__enter__.return_value,
            skip=0,
            limit=20,
            search=None,
            language=None
        )


@pytest.mark.asyncio
async def test_get_published_plans_with_search(sample_plan_aggregate, mock_db_session):
    """Test retrieval with search filter."""
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[sample_plan_aggregate]) as mock_repo, \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=1), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value=None), \
         patch("pecha_api.plans.public.plan_service.generate_author_avatar_url", return_value=None):
        
        result = await get_published_plans(
            search="meditation",
            language=None,
            sort_by="title",
            sort_order="asc",
            skip=0,
            limit=20
        )
        
        assert len(result.plans) == 1
        mock_repo.assert_called_once_with(
            db=mock_db_session.__enter__.return_value,
            skip=0,
            limit=20,
            search="meditation",
            language=None
        )


@pytest.mark.asyncio
async def test_get_published_plans_with_language_filter(sample_plan_aggregate, mock_db_session):
    """Test retrieval with language filter."""
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[sample_plan_aggregate]) as mock_repo, \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=1), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value=None), \
         patch("pecha_api.plans.public.plan_service.generate_author_avatar_url", return_value=None):
        
        result = await get_published_plans(
            search=None,
            language="en",
            sort_by="title",
            sort_order="asc",
            skip=0,
            limit=20
        )
        
        assert len(result.plans) == 1
        mock_repo.assert_called_once_with(
            db=mock_db_session.__enter__.return_value,
            skip=0,
            limit=20,
            search=None,
            language="en"
        )


@pytest.mark.asyncio
async def test_get_published_plans_sort_by_title_asc(sample_plan_aggregate, mock_db_session):
    """Test sorting by title in ascending order."""
    plan1 = Plan(
        id=uuid4(),
        title="Advanced Meditation",
        description="Advanced techniques",
        language=LanguageCode.EN,
        status=PlanStatus.PUBLISHED,
        tags=[],
        deleted_at=None
    )
    plan2 = Plan(
        id=uuid4(),
        title="Beginner Meditation",
        description="Basic techniques",
        language=LanguageCode.EN,
        status=PlanStatus.PUBLISHED,
        tags=[],
        deleted_at=None
    )
    
    aggregates = [
        PlanWithAggregates(plan=plan1, total_days=20, subscription_count=100),
        PlanWithAggregates(plan=plan2, total_days=10, subscription_count=50)
    ]
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=aggregates), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=2), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value=None), \
         patch("pecha_api.plans.public.plan_service.generate_author_avatar_url", return_value=None):
        
        result = await get_published_plans(sort_by="title", sort_order="asc")
        
        # Should be sorted: Advanced, Beginner
        assert result.plans[0].title == "Advanced Meditation"
        assert result.plans[1].title == "Beginner Meditation"


@pytest.mark.asyncio
async def test_get_published_plans_sort_by_title_desc(sample_plan_aggregate, mock_db_session):
    """Test sorting by title in descending order."""
    plan1 = Plan(
        id=uuid4(),
        title="Advanced Meditation",
        description="Advanced techniques",
        language=LanguageCode.EN,
        status=PlanStatus.PUBLISHED,
        tags=[],
        deleted_at=None
    )
    plan2 = Plan(
        id=uuid4(),
        title="Beginner Meditation",
        description="Basic techniques",
        language=LanguageCode.EN,
        status=PlanStatus.PUBLISHED,
        tags=[],
        deleted_at=None
    )
    
    aggregates = [
        PlanWithAggregates(plan=plan1, total_days=20, subscription_count=100),
        PlanWithAggregates(plan=plan2, total_days=10, subscription_count=50)
    ]
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=aggregates), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=2), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value=None), \
         patch("pecha_api.plans.public.plan_service.generate_author_avatar_url", return_value=None):
        
        result = await get_published_plans(sort_by="title", sort_order="desc")
        
        # Should be sorted: Beginner, Advanced
        assert result.plans[0].title == "Beginner Meditation"
        assert result.plans[1].title == "Advanced Meditation"


@pytest.mark.asyncio
async def test_get_published_plans_sort_by_total_days(sample_plan_aggregate, mock_db_session):
    """Test sorting by total_days."""
    plan1 = Plan(
        id=uuid4(),
        title="Short Plan",
        description="Short plan",
        language=LanguageCode.EN,
        status=PlanStatus.PUBLISHED,
        tags=[],
        deleted_at=None
    )
    plan2 = Plan(
        id=uuid4(),
        title="Long Plan",
        description="Long plan",
        language=LanguageCode.EN,
        status=PlanStatus.PUBLISHED,
        tags=[],
        deleted_at=None
    )
    
    aggregates = [
        PlanWithAggregates(plan=plan1, total_days=10, subscription_count=100),
        PlanWithAggregates(plan=plan2, total_days=30, subscription_count=50)
    ]
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=aggregates), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=2), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value=None), \
         patch("pecha_api.plans.public.plan_service.generate_author_avatar_url", return_value=None):
        
        result = await get_published_plans(sort_by="total_days", sort_order="asc")
        
        # Should be sorted by total_days: 10, 30
        assert result.plans[0].total_days == 10
        assert result.plans[1].total_days == 30


@pytest.mark.asyncio
async def test_get_published_plans_sort_by_subscription_count(sample_plan_aggregate, mock_db_session):
    """Test sorting by subscription_count."""
    plan1 = Plan(
        id=uuid4(),
        title="Popular Plan",
        description="Popular plan",
        language=LanguageCode.EN,
        status=PlanStatus.PUBLISHED,
        tags=[],
        deleted_at=None
    )
    plan2 = Plan(
        id=uuid4(),
        title="Less Popular Plan",
        description="Less popular plan",
        language=LanguageCode.EN,
        status=PlanStatus.PUBLISHED,
        tags=[],
        deleted_at=None
    )
    
    aggregates = [
        PlanWithAggregates(plan=plan1, total_days=10, subscription_count=200),
        PlanWithAggregates(plan=plan2, total_days=10, subscription_count=50)
    ]
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=aggregates), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=2), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value=None), \
         patch("pecha_api.plans.public.plan_service.generate_author_avatar_url", return_value=None):
        
        result = await get_published_plans(sort_by="subscription_count", sort_order="desc")
        
        # Should be sorted by subscription_count descending: 200, 50
        assert result.plans[0].subscription_count == 200
        assert result.plans[1].subscription_count == 50


@pytest.mark.asyncio
async def test_get_published_plans_empty_result(mock_db_session):
    """Test retrieval when no plans are found."""
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[]), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=0):
        
        result = await get_published_plans()
        
        assert isinstance(result, PlansResponse)
        assert len(result.plans) == 0
        assert result.total == 0


@pytest.mark.asyncio
async def test_get_published_plans_without_author(mock_db_session):
    """Test retrieval of plans without author information."""
    plan_no_author = Plan(
        id=uuid4(),
        title="Orphan Plan",
        description="Plan without author",
        language=LanguageCode.EN,
        status=PlanStatus.PUBLISHED,
        tags=[],
        author=None,
        deleted_at=None
    )
    
    aggregate = PlanWithAggregates(plan=plan_no_author, total_days=10, subscription_count=0)
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[aggregate]), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=1), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value=None):
        
        result = await get_published_plans()
        
        assert len(result.plans) == 1
        assert result.plans[0].author is None


@pytest.mark.asyncio
async def test_get_published_plans_with_pagination(sample_plan_aggregate, mock_db_session):
    """Test retrieval with pagination parameters."""
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[sample_plan_aggregate]) as mock_repo, \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=1), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value=None), \
         patch("pecha_api.plans.public.plan_service.generate_author_avatar_url", return_value=None):
        
        result = await get_published_plans(skip=10, limit=5)
        
        assert result.skip == 10
        assert result.limit == 5
        mock_repo.assert_called_once_with(
            db=mock_db_session.__enter__.return_value,
            skip=10,
            limit=5,
            search=None,
            language=None
        )


@pytest.mark.asyncio
async def test_get_published_plans_image_url_generation_failure(sample_plan_aggregate, mock_db_session):
    """Test handling when presigned URL generation fails."""
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[sample_plan_aggregate]), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value=None) as mock_plan_url, \
         patch("pecha_api.plans.public.plan_service.generate_author_avatar_url", return_value=None) as mock_author_url:
        
        result = await get_published_plans()
        
        # Should still return plan with None image URLs
        assert len(result.plans) == 1
        assert result.plans[0].image_url is None
        assert result.plans[0].image_key == "images/plan_images/plan-id/uuid/image.jpg"
        assert result.plans[0].author.image_url is None


@pytest.mark.asyncio
async def test_get_published_plans_database_error(mock_db_session):
    """Test handling of database errors."""
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", side_effect=Exception("Database connection error")):
        
        with pytest.raises(HTTPException) as exc_info:
            await get_published_plans()
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to fetch published plans" in str(exc_info.value.detail)


# ============================================================================
# get_published_plan() Service Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_published_plan_success(sample_plan, sample_author, mock_db_session):
    """Test successful retrieval of a single published plan."""
    plan_id = sample_plan.id
    
    # Mock database queries
    mock_query = MagicMock()
    mock_db_session.__enter__.return_value.query.return_value = mock_query
    mock_query.filter.return_value.count.return_value = 30  # total_days
    mock_query.filter.return_value.distinct.return_value.count.return_value = 150  # subscription_count
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", return_value=sample_plan) as mock_repo, \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value="https://bucket.s3.amazonaws.com/presigned-url") as mock_plan_url, \
         patch("pecha_api.plans.public.plan_service.generate_author_avatar_url", return_value="https://bucket.s3.amazonaws.com/author-presigned-url") as mock_author_url:
        
        result = await get_published_plan(plan_id=plan_id)
        
        # Verify result structure
        assert isinstance(result, PlanDTO)
        assert result.id == plan_id
        assert result.title == "Introduction to Meditation"
        assert result.language == "en"
        assert result.total_days == 30
        assert result.subscription_count == 150
        assert result.image_url == "https://bucket.s3.amazonaws.com/presigned-url"
        assert result.image_key == "images/plan_images/plan-id/uuid/image.jpg"
        
        # Verify author
        assert result.author is not None
        assert result.author.firstname == "John"
        assert result.author.lastname == "Doe"
        assert result.author.image_url == "https://bucket.s3.amazonaws.com/author-presigned-url"
        
        # Verify repository was called
        mock_repo.assert_called_once_with(db=mock_db_session.__enter__.return_value, plan_id=plan_id)


@pytest.mark.asyncio
async def test_get_published_plan_not_found(mock_db_session):
    """Test retrieval of non-existent plan."""
    plan_id = uuid4()
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", return_value=None):
        
        # The service catches the 404 and wraps it in a 500 error
        with pytest.raises(HTTPException) as exc_info:
            await get_published_plan(plan_id=plan_id)
        
        # Service wraps 404 in 500 error with detail message
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to fetch published plan details" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_published_plan_without_author(mock_db_session):
    """Test retrieval of plan without author information."""
    plan_no_author = Plan(
        id=uuid4(),
        title="Orphan Plan",
        description="Plan without author",
        language=LanguageCode.EN,
        status=PlanStatus.PUBLISHED,
        tags=[],
        image_url=None,
        author=None,
        deleted_at=None
    )
    
    # Mock database queries
    mock_query = MagicMock()
    mock_db_session.__enter__.return_value.query.return_value = mock_query
    mock_query.filter.return_value.count.return_value = 10
    mock_query.filter.return_value.distinct.return_value.count.return_value = 5
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", return_value=plan_no_author), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value=None):
        
        result = await get_published_plan(plan_id=plan_no_author.id)
        
        assert result.author is None
        assert result.title == "Orphan Plan"


@pytest.mark.asyncio
async def test_get_published_plan_image_url_generation_failure(sample_plan, mock_db_session):
    """Test handling when presigned URL generation fails."""
    plan_id = sample_plan.id
    
    # Mock database queries
    mock_query = MagicMock()
    mock_db_session.__enter__.return_value.query.return_value = mock_query
    mock_query.filter.return_value.count.return_value = 30
    mock_query.filter.return_value.distinct.return_value.count.return_value = 150
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", return_value=sample_plan), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value=None), \
         patch("pecha_api.plans.public.plan_service.generate_author_avatar_url", return_value=None):
        
        result = await get_published_plan(plan_id=plan_id)
        
        # Should still return plan with None image URLs but valid image_key
        assert result.image_url is None
        assert result.image_key == "images/plan_images/plan-id/uuid/image.jpg"
        assert result.author.image_url is None


@pytest.mark.asyncio
async def test_get_published_plan_database_error(mock_db_session):
    """Test handling of database errors."""
    plan_id = uuid4()
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", side_effect=Exception("Database connection error")):
        
        with pytest.raises(HTTPException) as exc_info:
            await get_published_plan(plan_id=plan_id)
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to fetch published plan details" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_published_plan_with_empty_tags(sample_plan, mock_db_session):
    """Test retrieval of plan with empty tags."""
    sample_plan.tags = None
    
    # Mock database queries
    mock_query = MagicMock()
    mock_db_session.__enter__.return_value.query.return_value = mock_query
    mock_query.filter.return_value.count.return_value = 10
    mock_query.filter.return_value.distinct.return_value.count.return_value = 5
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", return_value=sample_plan), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value=None), \
         patch("pecha_api.plans.public.plan_service.generate_author_avatar_url", return_value=None):
        
        result = await get_published_plan(plan_id=sample_plan.id)
        
        # Should return empty list for tags
        assert result.tags == []


@pytest.mark.asyncio
async def test_get_published_plan_zero_subscriptions(sample_plan, mock_db_session):
    """Test retrieval of plan with zero subscriptions."""
    # Mock database queries
    mock_query = MagicMock()
    mock_db_session.__enter__.return_value.query.return_value = mock_query
    mock_query.filter.return_value.count.return_value = 15
    mock_query.filter.return_value.distinct.return_value.count.return_value = 0  # No subscriptions
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", return_value=sample_plan), \
         patch("pecha_api.plans.public.plan_service.generate_plan_image_url", return_value=None), \
         patch("pecha_api.plans.public.plan_service.generate_author_avatar_url", return_value=None):
        
        result = await get_published_plan(plan_id=sample_plan.id)
        
        assert result.subscription_count == 0

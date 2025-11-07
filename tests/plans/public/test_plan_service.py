import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock, Mock
from fastapi import HTTPException
from starlette import status

from pecha_api.plans.public.plan_service import get_published_plans, get_published_plan
from pecha_api.plans.public.plan_response_models import PublicPlansResponse, PublicPlanDTO
from pecha_api.plans.plans_enums import PlanStatus, DifficultyLevel, LanguageCode


@pytest.fixture
def sample_author():
    author = MagicMock()
    author.id = uuid4()
    author.first_name = "John"
    author.last_name = "Doe"
    author.email = "john.doe@example.com"
    author.image_url = "images/author_avatars/author-id/avatar.jpg"
    author.is_verified = True
    return author


@pytest.fixture
def sample_plan(sample_author):
    plan = MagicMock()
    plan.id = uuid4()
    plan.title = "Introduction to Meditation"
    plan.description = "A comprehensive guide to meditation practices"
    plan.language = LanguageCode.EN
    plan.difficulty_level = DifficultyLevel.BEGINNER
    plan.image_url = "images/plan_images/plan-id/uuid/image.jpg"
    plan.status = PlanStatus.PUBLISHED
    plan.tags = ["meditation", "mindfulness", "beginner"]
    plan.author = sample_author
    plan.deleted_at = None
    return plan


@pytest.fixture
def sample_plan_aggregate(sample_plan):
    aggregate = MagicMock()
    aggregate.plan = sample_plan
    aggregate.total_days = 30
    aggregate.subscription_count = 150
    return aggregate


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.__enter__ = Mock(return_value=session)
    session.__exit__ = Mock(return_value=None)
    return session


@pytest.mark.asyncio
async def test_get_published_plans_success(sample_plan_aggregate, mock_db_session):
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[sample_plan_aggregate]) as mock_repo, \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=1), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value="https://bucket.s3.amazonaws.com/presigned-url") as mock_presigned_url:
        
        result = await get_published_plans(
            search=None,
            language=None,
            sort_by="title",
            sort_order="asc",
            skip=0,
            limit=20
        )
        
        assert isinstance(result, PublicPlansResponse)
        assert len(result.plans) == 1
        assert result.skip == 0
        assert result.limit == 20
        assert result.total == 1
        
        plan_dto = result.plans[0]
        assert plan_dto.title == "Introduction to Meditation"
        assert plan_dto.language == "EN"
        assert plan_dto.total_days == 30
        assert plan_dto.image_url == "https://bucket.s3.amazonaws.com/presigned-url"
        assert plan_dto.author is None
        
        mock_repo.assert_called_once_with(
            db=mock_db_session.__enter__.return_value,
            skip=0,
            limit=20,
            search=None,
            language=None,
            sort_by="title",
            sort_order="asc"
        )


@pytest.mark.asyncio
async def test_get_published_plans_with_search(sample_plan_aggregate, mock_db_session):
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[sample_plan_aggregate]) as mock_repo, \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=1), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value=None):
        
        result = await get_published_plans(
            search="meditation",
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
            search="meditation",
            language="en",
            sort_by="title",
            sort_order="asc"
        )


@pytest.mark.asyncio
async def test_get_published_plans_with_language_filter(sample_plan_aggregate, mock_db_session):
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[sample_plan_aggregate]) as mock_repo, \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=1), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value=None):
        
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
            language="en",
            sort_by="title",
            sort_order="asc"
        )


@pytest.mark.asyncio
async def test_get_published_plans_sort_by_title_asc(sample_plan_aggregate, mock_db_session):
    plan1 = MagicMock()
    plan1.id = uuid4()
    plan1.title = "Advanced Meditation"
    plan1.description = "Advanced techniques"
    plan1.language = LanguageCode.EN
    plan1.difficulty_level = DifficultyLevel.BEGINNER
    plan1.image_url = None
    plan1.status = PlanStatus.PUBLISHED
    plan1.tags = []
    plan1.author = None
    
    plan2 = MagicMock()
    plan2.id = uuid4()
    plan2.title = "Beginner Meditation"
    plan2.description = "Basic techniques"
    plan2.language = LanguageCode.EN
    plan2.difficulty_level = DifficultyLevel.BEGINNER
    plan2.image_url = None
    plan2.status = PlanStatus.PUBLISHED
    plan2.tags = []
    plan2.author = None
    
    agg1 = MagicMock()
    agg1.plan = plan1
    agg1.total_days = 20
    agg1.subscription_count = 100
    
    agg2 = MagicMock()
    agg2.plan = plan2
    agg2.total_days = 10
    agg2.subscription_count = 50
    
    aggregates = [agg1, agg2]
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=aggregates), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=2), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value=None):
        
        result = await get_published_plans(sort_by="title", sort_order="asc")
        
        assert result.plans[0].title == "Advanced Meditation"
        assert result.plans[1].title == "Beginner Meditation"


@pytest.mark.asyncio
async def test_get_published_plans_sort_by_title_desc(sample_plan_aggregate, mock_db_session):
    plan1 = MagicMock()
    plan1.id = uuid4()
    plan1.title = "Advanced Meditation"
    plan1.description = "Advanced techniques"
    plan1.language = LanguageCode.EN
    plan1.difficulty_level = DifficultyLevel.BEGINNER
    plan1.image_url = None
    plan1.status = PlanStatus.PUBLISHED
    plan1.tags = []
    plan1.author = None
    
    plan2 = MagicMock()
    plan2.id = uuid4()
    plan2.title = "Beginner Meditation"
    plan2.description = "Basic techniques"
    plan2.language = LanguageCode.EN
    plan2.difficulty_level = DifficultyLevel.BEGINNER
    plan2.image_url = None
    plan2.status = PlanStatus.PUBLISHED
    plan2.tags = []
    plan2.author = None
    
    agg1 = MagicMock()
    agg1.plan = plan1
    agg1.total_days = 20
    agg1.subscription_count = 100
    
    agg2 = MagicMock()
    agg2.plan = plan2
    agg2.total_days = 10
    agg2.subscription_count = 50
    
    aggregates = [agg1, agg2]
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=aggregates), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=2), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value=None):
        
        result = await get_published_plans(sort_by="title", sort_order="desc")
        
        assert len(result.plans) == 2
        assert result.plans[0].title == "Advanced Meditation"
        assert result.plans[1].title == "Beginner Meditation"


@pytest.mark.asyncio
async def test_get_published_plans_sort_by_total_days(sample_plan_aggregate, mock_db_session):
    plan1 = MagicMock()
    plan1.id = uuid4()
    plan1.title = "Short Plan"
    plan1.description = "Short plan"
    plan1.language = LanguageCode.EN
    plan1.difficulty_level = DifficultyLevel.BEGINNER
    plan1.image_url = None
    plan1.status = PlanStatus.PUBLISHED
    plan1.tags = []
    plan1.author = None
    
    plan2 = MagicMock()
    plan2.id = uuid4()
    plan2.title = "Long Plan"
    plan2.description = "Long plan"
    plan2.language = LanguageCode.EN
    plan2.difficulty_level = DifficultyLevel.BEGINNER
    plan2.image_url = None
    plan2.status = PlanStatus.PUBLISHED
    plan2.tags = []
    plan2.author = None
    
    agg1 = MagicMock()
    agg1.plan = plan1
    agg1.total_days = 10
    agg1.subscription_count = 100
    
    agg2 = MagicMock()
    agg2.plan = plan2
    agg2.total_days = 30
    agg2.subscription_count = 50
    
    aggregates = [agg1, agg2]
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=aggregates), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=2), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value=None):
        
        result = await get_published_plans(sort_by="total_days", sort_order="asc")
        
        assert result.plans[0].total_days == 10
        assert result.plans[1].total_days == 30


@pytest.mark.asyncio
async def test_get_published_plans_sort_by_subscription_count(sample_plan_aggregate, mock_db_session):
    plan1 = MagicMock()
    plan1.id = uuid4()
    plan1.title = "Popular Plan"
    plan1.description = "Popular plan"
    plan1.language = LanguageCode.EN
    plan1.difficulty_level = DifficultyLevel.BEGINNER
    plan1.image_url = None
    plan1.status = PlanStatus.PUBLISHED
    plan1.tags = []
    plan1.author = None
    
    plan2 = MagicMock()
    plan2.id = uuid4()
    plan2.title = "Less Popular Plan"
    plan2.description = "Less popular plan"
    plan2.language = LanguageCode.EN
    plan2.difficulty_level = DifficultyLevel.BEGINNER
    plan2.image_url = None
    plan2.status = PlanStatus.PUBLISHED
    plan2.tags = []
    plan2.author = None
    
    agg1 = MagicMock()
    agg1.plan = plan1
    agg1.total_days = 10
    agg1.subscription_count = 200
    
    agg2 = MagicMock()
    agg2.plan = plan2
    agg2.total_days = 10
    agg2.subscription_count = 50
    
    aggregates = [agg1, agg2]
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=aggregates), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=2), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value=None):
        
        result = await get_published_plans(sort_by="subscription_count", sort_order="desc")
        
        assert len(result.plans) == 2
        assert result.plans[0].title == "Popular Plan"
        assert result.plans[1].title == "Less Popular Plan"


@pytest.mark.asyncio
async def test_get_published_plans_empty_result(mock_db_session):
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[]), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=0):
        
        result = await get_published_plans()
        
        assert isinstance(result, PublicPlansResponse)
        assert len(result.plans) == 0
        assert result.total == 0


@pytest.mark.asyncio
async def test_get_published_plans_without_author(mock_db_session):
    plan_no_author = MagicMock()
    plan_no_author.id = uuid4()
    plan_no_author.title = "Orphan Plan"
    plan_no_author.description = "Plan without author"
    plan_no_author.language = LanguageCode.EN
    plan_no_author.difficulty_level = DifficultyLevel.BEGINNER
    plan_no_author.image_url = None
    plan_no_author.status = PlanStatus.PUBLISHED
    plan_no_author.tags = []
    plan_no_author.author = None
    
    aggregate = MagicMock()
    aggregate.plan = plan_no_author
    aggregate.total_days = 10
    aggregate.subscription_count = 0
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[aggregate]), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=1), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value=None):
        
        result = await get_published_plans()
        
        assert len(result.plans) == 1
        assert result.plans[0].author is None


@pytest.mark.asyncio
async def test_get_published_plans_with_pagination(sample_plan_aggregate, mock_db_session):
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[sample_plan_aggregate]) as mock_repo, \
         patch("pecha_api.plans.public.plan_service.get_published_plans_count", return_value=1), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value=None):
        
        result = await get_published_plans(skip=10, limit=5)
        
        assert result.skip == 10
        assert result.limit == 5
        mock_repo.assert_called_once_with(
            db=mock_db_session.__enter__.return_value,
            skip=10,
            limit=5,
            search=None,
            language="en",
            sort_by="title",
            sort_order="asc"
        )


@pytest.mark.asyncio
async def test_get_published_plans_image_url_generation_failure(sample_plan_aggregate, mock_db_session):
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", return_value=[sample_plan_aggregate]), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value=None):
        
        result = await get_published_plans()
        
        assert len(result.plans) == 1
        assert result.plans[0].image_url is None


@pytest.mark.asyncio
async def test_get_published_plans_database_error(mock_db_session):
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plans_from_db", side_effect=Exception("Database connection error")):
        
        with pytest.raises(HTTPException) as exc_info:
            await get_published_plans()
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to fetch published plans" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_published_plan_success(sample_plan, sample_author, mock_db_session):
    plan_id = sample_plan.id
    
    mock_query = MagicMock()
    mock_db_session.__enter__.return_value.query.return_value = mock_query
    mock_query.filter.return_value.count.return_value = 30 
    mock_query.filter.return_value.distinct.return_value.count.return_value = 150 
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", return_value=sample_plan) as mock_repo, \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value="https://bucket.s3.amazonaws.com/presigned-url") as mock_presigned_url:
        
        result = await get_published_plan(plan_id=plan_id)
        
        assert isinstance(result, PublicPlanDTO)
        assert result.id == plan_id
        assert result.title == "Introduction to Meditation"
        assert result.language == "EN" 
        assert result.total_days == 30
        assert result.image_url == "https://bucket.s3.amazonaws.com/presigned-url"
        
        assert result.author is not None
        assert result.author.firstname == "John"
        assert result.author.lastname == "Doe"
        assert result.author.image_url == "https://bucket.s3.amazonaws.com/presigned-url"
        assert result.author.image_key == "images/author_avatars/author-id/avatar.jpg"
        
        mock_repo.assert_called_once_with(db=mock_db_session.__enter__.return_value, plan_id=plan_id)


@pytest.mark.asyncio
async def test_get_published_plan_not_found(mock_db_session):
    plan_id = uuid4()
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", return_value=None):
        
        with pytest.raises(HTTPException) as exc_info:
            await get_published_plan(plan_id=plan_id)
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to fetch published plan details" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_published_plan_without_author(mock_db_session):
    plan_no_author = MagicMock()
    plan_no_author.id = uuid4()
    plan_no_author.title = "Orphan Plan"
    plan_no_author.description = "Plan without author"
    plan_no_author.language = LanguageCode.EN
    plan_no_author.difficulty_level = DifficultyLevel.BEGINNER
    plan_no_author.image_url = None
    plan_no_author.status = PlanStatus.PUBLISHED
    plan_no_author.tags = []
    plan_no_author.author = None
    
    mock_query = MagicMock()
    mock_db_session.__enter__.return_value.query.return_value = mock_query
    mock_query.filter.return_value.count.return_value = 10
    mock_query.filter.return_value.distinct.return_value.count.return_value = 5
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", return_value=plan_no_author), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value=None):
        
        result = await get_published_plan(plan_id=plan_no_author.id)
        
        assert result.author is None
        assert result.title == "Orphan Plan"


@pytest.mark.asyncio
async def test_get_published_plan_image_url_generation_failure(sample_plan, mock_db_session):
    plan_id = sample_plan.id
    
    mock_query = MagicMock()
    mock_db_session.__enter__.return_value.query.return_value = mock_query
    mock_query.filter.return_value.count.return_value = 30
    mock_query.filter.return_value.distinct.return_value.count.return_value = 150
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", return_value=sample_plan), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value=None):
        
        result = await get_published_plan(plan_id=plan_id)
        
        assert result.image_url is None


@pytest.mark.asyncio
async def test_get_published_plan_database_error(mock_db_session):
    plan_id = uuid4()
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", side_effect=Exception("Database connection error")):
        
        with pytest.raises(HTTPException) as exc_info:
            await get_published_plan(plan_id=plan_id)
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to fetch published plan details" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_published_plan_with_empty_tags(sample_plan, mock_db_session):
    sample_plan.tags = None
    
    mock_query = MagicMock()
    mock_db_session.__enter__.return_value.query.return_value = mock_query
    mock_query.filter.return_value.count.return_value = 10
    mock_query.filter.return_value.distinct.return_value.count.return_value = 5
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", return_value=sample_plan), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value=None):
        
        result = await get_published_plan(plan_id=sample_plan.id)
        
        assert result.tags == []


@pytest.mark.asyncio
async def test_get_published_plan_zero_subscriptions(sample_plan, mock_db_session):
    mock_query = MagicMock()
    mock_db_session.__enter__.return_value.query.return_value = mock_query
    mock_query.filter.return_value.count.return_value = 15
    mock_query.filter.return_value.distinct.return_value.count.return_value = 0
    
    with patch("pecha_api.plans.public.plan_service.SessionLocal", return_value=mock_db_session), \
         patch("pecha_api.plans.public.plan_service.get_published_plan_by_id", return_value=sample_plan), \
         patch("pecha_api.plans.public.plan_service.generate_presigned_access_url", return_value=None):
        
        result = await get_published_plan(plan_id=sample_plan.id)
        
        assert result.title == sample_plan.title
        assert result.id == sample_plan.id

"""
Test suite for public plan view endpoints.

Tests the following endpoints:
1. GET /api/v1/public/plans - List published plans with filtering and pagination
2. GET /api/v1/public/plans/{plan_id} - Get published plan details
"""

import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette import status

from pecha_api.app import api
from pecha_api.plans.plans_response_models import PlansResponse, PlanDTO, AuthorDTO
from pecha_api.plans.plans_enums import PlanStatus, DifficultyLevel
from pecha_api.error_contants import ErrorConstants


client = TestClient(api)


@pytest.fixture
def sample_author_dto():
    """Sample author DTO for testing."""
    return AuthorDTO(
        id=uuid4(),
        firstname="John",
        lastname="Doe",
        image_url="https://bucket.s3.amazonaws.com/presigned-url",
        image_key="images/author_avatars/author-id/avatar.jpg"
    )


@pytest.fixture
def sample_plan_dto(sample_author_dto):
    """Sample plan DTO for testing."""
    return PlanDTO(
        id=uuid4(),
        title="Introduction to Meditation",
        description="A comprehensive guide to meditation practices",
        language="en",
        difficulty_level=DifficultyLevel.BEGINNER,
        image_url="https://bucket.s3.amazonaws.com/presigned-url",
        image_key="images/plan_images/plan-id/uuid/image.jpg",
        total_days=30,
        tags=["meditation", "mindfulness", "beginner"],
        status=PlanStatus.PUBLISHED,
        subscription_count=150,
        author=sample_author_dto
    )


@pytest.fixture
def sample_plans_response(sample_plan_dto):
    """Sample plans response for testing."""
    return PlansResponse(
        plans=[sample_plan_dto],
        skip=0,
        limit=20,
        total=1
    )

@pytest.mark.asyncio
async def test_get_plans_success(sample_plans_response):
    """Test successful retrieval of published plans."""
    with patch("pecha_api.plans.public.plan_views.get_published_plans", return_value=sample_plans_response) as mock_service:
        response = client.get("/api/v1/plans")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "plans" in data
        assert "skip" in data
        assert "limit" in data
        assert "total" in data
        assert len(data["plans"]) == 1
        assert data["skip"] == 0
        assert data["limit"] == 20
        assert data["total"] == 1
        
        plan = data["plans"][0]
        assert "id" in plan
        assert plan["title"] == "Introduction to Meditation"
        assert plan["language"] == "en"
        assert plan["total_days"] == 30
        assert plan["subscription_count"] == 150
        assert "author" in plan
        
        mock_service.assert_called_once_with(
            search=None,
            language=None,
            sort_by="title",
            sort_order="asc",
            skip=0,
            limit=20
        )


@pytest.mark.asyncio
async def test_get_plans_with_search_filter(sample_plans_response):
    """Test retrieval of plans with search filter."""
    with patch("pecha_api.plans.public.plan_views.get_published_plans", return_value=sample_plans_response) as mock_service:
        response = client.get("/api/v1/plans?search=meditation")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["plans"]) == 1
        
        mock_service.assert_called_once_with(
            search="meditation",
            language=None,
            sort_by="title",
            sort_order="asc",
            skip=0,
            limit=20
        )


@pytest.mark.asyncio
async def test_get_plans_with_language_filter(sample_plans_response):
    """Test retrieval of plans with language filter."""
    with patch("pecha_api.plans.public.plan_views.get_published_plans", return_value=sample_plans_response) as mock_service:
        response = client.get("/api/v1/plans?language=en")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["plans"]) == 1
        
        mock_service.assert_called_once_with(
            search=None,
            language="en",
            sort_by="title",
            sort_order="asc",
            skip=0,
            limit=20
        )


@pytest.mark.asyncio
async def test_get_plans_with_sorting(sample_plans_response):
    """Test retrieval of plans with custom sorting."""
    with patch("pecha_api.plans.public.plan_views.get_published_plans", return_value=sample_plans_response) as mock_service:
        response = client.get("/api/v1/plans?sort_by=subscription_count&sort_order=desc")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["plans"]) == 1
        
        mock_service.assert_called_once_with(
            search=None,
            language=None,
            sort_by="subscription_count",
            sort_order="desc",
            skip=0,
            limit=20
        )


@pytest.mark.asyncio
async def test_get_plans_with_pagination(sample_plans_response):
    """Test retrieval of plans with pagination parameters."""
    with patch("pecha_api.plans.public.plan_views.get_published_plans", return_value=sample_plans_response) as mock_service:
        response = client.get("/api/v1/plans?skip=10&limit=5")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        mock_service.assert_called_once_with(
            search=None,
            language=None,
            sort_by="title",
            sort_order="asc",
            skip=10,
            limit=5
        )


@pytest.mark.asyncio
async def test_get_plans_with_all_filters(sample_plans_response):
    """Test retrieval of plans with all filter parameters."""
    with patch("pecha_api.plans.public.plan_views.get_published_plans", return_value=sample_plans_response) as mock_service:
        response = client.get(
            "/api/v1/plans?search=meditation&language=en&sort_by=total_days&sort_order=desc&skip=5&limit=10"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        mock_service.assert_called_once_with(
            search="meditation",
            language="en",
            sort_by="total_days",
            sort_order="desc",
            skip=5,
            limit=10
        )


@pytest.mark.asyncio
async def test_get_plans_empty_result():
    """Test retrieval when no plans are found."""
    empty_response = PlansResponse(plans=[], skip=0, limit=20, total=0)
    
    with patch("pecha_api.plans.public.plan_views.get_published_plans", return_value=empty_response):
        response = client.get("/api/v1/plans")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["plans"]) == 0
        assert data["total"] == 0


@pytest.mark.asyncio
async def test_get_plans_invalid_sort_by():
    """Test retrieval with invalid sort_by parameter."""
    response = client.get("/api/v1/plans?sort_by=invalid_field")
    
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_plans_invalid_sort_order():
    """Test retrieval with invalid sort_order parameter."""
    response = client.get("/api/v1/plans?sort_order=invalid_order")
    
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_plans_negative_skip():
    """Test retrieval with negative skip parameter."""
    response = client.get("/api/v1/plans?skip=-1")
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_plans_invalid_limit():
    """Test retrieval with invalid limit parameter (exceeds max)."""
    response = client.get("/api/v1/plans?limit=100")
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_plans_service_error():
    """Test handling of service layer errors."""
    with patch("pecha_api.plans.public.plan_views.get_published_plans", side_effect=HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database connection error"
    )):
        response = client.get("/api/v1/plans")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Database connection error" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_plan_details_success(sample_plan_dto):
    """Test successful retrieval of plan details."""
    plan_id = sample_plan_dto.id
    
    with patch("pecha_api.plans.public.plan_views.get_published_plan", return_value=sample_plan_dto) as mock_service:
        response = client.get(f"/api/v1/plans/{plan_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == str(plan_id)
        assert data["title"] == "Introduction to Meditation"
        assert data["description"] == "A comprehensive guide to meditation practices"
        assert data["language"] == "en"
        assert data["difficulty_level"] == "BEGINNER"
        assert data["total_days"] == 30
        assert data["subscription_count"] == 150
        assert data["status"] == "PUBLISHED"
        assert len(data["tags"]) == 3
        
        assert "author" in data
        assert data["author"]["firstname"] == "John"
        assert data["author"]["lastname"] == "Doe"
        
        assert "image_url" in data
        assert "image_key" in data
        assert data["author"]["image_url"] is not None
        assert data["author"]["image_key"] is not None
        
        mock_service.assert_called_once_with(plan_id=plan_id)


@pytest.mark.asyncio
async def test_get_plan_details_not_found():
    """Test retrieval of non-existent plan."""
    plan_id = uuid4()
    
    with patch("pecha_api.plans.public.plan_views.get_published_plan", side_effect=HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorConstants.PLAN_NOT_FOUND
    )):
        response = client.get(f"/api/v1/plans/{plan_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert ErrorConstants.PLAN_NOT_FOUND in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_plan_details_invalid_uuid():
    """Test retrieval with invalid UUID format."""
    response = client.get("/api/v1/plans/invalid-uuid")
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_plan_details_without_author(sample_plan_dto):
    """Test retrieval of plan without author information."""
    plan_dto_no_author = PlanDTO(
        id=uuid4(),
        title="Test Plan",
        description="Test Description",
        language="en",
        difficulty_level=DifficultyLevel.BEGINNER,
        image_url=None,
        image_key=None,
        total_days=10,
        tags=[],
        status=PlanStatus.PUBLISHED,
        subscription_count=0,
        author=None
    )
    
    with patch("pecha_api.plans.public.plan_views.get_published_plan", return_value=plan_dto_no_author):
        response = client.get(f"/api/v1/plans/{plan_dto_no_author.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["author"] is None


@pytest.mark.asyncio
async def test_get_plan_details_service_error():
    """Test handling of service layer errors."""
    plan_id = uuid4()
    
    with patch("pecha_api.plans.public.plan_views.get_published_plan", side_effect=HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to fetch published plan details"
    )):
        response = client.get(f"/api/v1/plans/{plan_id}")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to fetch published plan details" in response.json()["detail"]

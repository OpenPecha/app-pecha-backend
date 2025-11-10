import uuid
import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException
from starlette import status

from pecha_api.app import api


VALID_TOKEN = "valid_token"


@pytest.fixture
def authenticated_client():
    from pecha_api.plans.users import plan_users_views

    original_dependency_overrides = api.dependency_overrides.copy()

    def get_token_override():
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=VALID_TOKEN)

    api.dependency_overrides[plan_users_views.oauth2_scheme] = get_token_override
    client = TestClient(api)

    yield client

    api.dependency_overrides = original_dependency_overrides


@pytest.fixture
def unauthenticated_client():
    original_dependency_overrides = api.dependency_overrides.copy()
    client = TestClient(api)
    yield client
    api.dependency_overrides = original_dependency_overrides


def test_enroll_in_plan_success(authenticated_client):
    plan_id = uuid.uuid4()
    payload = {"plan_id": str(plan_id)}

    with patch("pecha_api.plans.users.plan_users_views.enroll_user_in_plan", return_value=None) as mock_enroll:
        response = authenticated_client.post(
            "/users/me/plans", json=payload, headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.text == ""
        assert mock_enroll.call_count == 1
        # Validate token argument
        assert mock_enroll.call_args.kwargs.get("token") == VALID_TOKEN
        # Validate request payload passed through
        enroll_request = mock_enroll.call_args.kwargs.get("enroll_request")
        assert getattr(enroll_request, "plan_id", None) == plan_id


def test_enroll_in_plan_service_error(authenticated_client):
    plan_id = uuid.uuid4()
    payload = {"plan_id": str(plan_id)}

    with patch("pecha_api.plans.users.plan_users_views.enroll_user_in_plan") as mock_enroll:
        mock_enroll.side_effect = HTTPException(
            status_code=404,
            detail={"error": "Not Found", "message": "plan not found"}
        )

        response = authenticated_client.post(
            "/users/me/plans", json=payload, headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == {"error": "Not Found", "message": "plan not found"}


def test_complete_sub_task_success(authenticated_client):
    sub_task_id = uuid.uuid4()

    with patch("pecha_api.plans.users.plan_users_views.complete_sub_task_service", return_value=None) as mock_complete:
        response = authenticated_client.post(
            f"/users/me/sub-tasks/{sub_task_id}/complete", 
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.text == ""
        assert mock_complete.call_count == 1
        assert mock_complete.call_args.kwargs.get("token") == VALID_TOKEN
        assert mock_complete.call_args.kwargs.get("id") == sub_task_id


def test_complete_sub_task_service_error_sub_task_not_found(authenticated_client):
    sub_task_id = uuid.uuid4()

    with patch("pecha_api.plans.users.plan_users_views.complete_sub_task_service") as mock_complete:
        mock_complete.side_effect = HTTPException(
            status_code=404,
            detail={"error": "Bad request", "message": "Sub task not found"}
        )

        response = authenticated_client.post(
            f"/users/me/sub-tasks/{sub_task_id}/complete",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == {"error": "Bad request", "message": "Sub task not found"}

def test_complete_sub_task_unauthenticated(unauthenticated_client):
    sub_task_id = uuid.uuid4()

    response = unauthenticated_client.post(f"/users/me/sub-tasks/{sub_task_id}/complete")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_plans_success(authenticated_client):
    from pecha_api.plans.users.plan_users_response_models import UserPlansResponse, UserPlanDTO
    from datetime import datetime, timezone
    
    plan_id = uuid.uuid4()
    mock_response = UserPlansResponse(
        plans=[
            UserPlanDTO(
                id=plan_id,
                title="Test Plan",
                description="Test Description",
                language="EN",
                difficulty_level="BEGINNER",
                image_url="https://s3.amazonaws.com/presigned-url",
                started_at=datetime.now(timezone.utc),
                total_days=30,
                tags=["meditation", "mindfulness"]
            )
        ],
        skip=0,
        limit=20,
        total=1
    )
    
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", return_value=mock_response) as mock_get_plans:
        response = authenticated_client.get(
            "/users/me/plans",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "plans" in data
        assert "skip" in data
        assert "limit" in data
        assert "total" in data
        
        assert data["skip"] == 0
        assert data["limit"] == 20
        assert data["total"] == 1
        
        assert len(data["plans"]) == 1
        plan = data["plans"][0]
        assert plan["id"] == str(plan_id)
        assert plan["title"] == "Test Plan"
        assert plan["description"] == "Test Description"
        assert plan["language"] == "EN"
        assert plan["difficulty_level"] == "BEGINNER"
        assert plan["image_url"] == "https://s3.amazonaws.com/presigned-url"
        assert plan["total_days"] == 30
        assert plan["tags"] == ["meditation", "mindfulness"]
        
        assert mock_get_plans.call_count == 1
        assert mock_get_plans.call_args.kwargs.get("token") == VALID_TOKEN
        assert mock_get_plans.call_args.kwargs.get("status_filter") is None
        assert mock_get_plans.call_args.kwargs.get("skip") == 0
        assert mock_get_plans.call_args.kwargs.get("limit") == 20


def test_get_user_plans_with_status_filter(authenticated_client):
    """Test retrieval of user plans with status filter"""
    from pecha_api.plans.users.plan_users_response_models import UserPlansResponse
    
    mock_response = UserPlansResponse(
        plans=[],
        skip=0,
        limit=20,
        total=0
    )
    
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", return_value=mock_response) as mock_get_plans:
        response = authenticated_client.get(
            "/users/me/plans?status_filter=active",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        assert mock_get_plans.call_count == 1
        assert mock_get_plans.call_args.kwargs.get("token") == VALID_TOKEN
        assert mock_get_plans.call_args.kwargs.get("status_filter") == "active"


def test_get_user_plans_with_pagination(authenticated_client):
    """Test retrieval of user plans with custom pagination"""
    from pecha_api.plans.users.plan_users_response_models import UserPlansResponse, UserPlanDTO
    from datetime import datetime, timezone
    
    mock_plans = [
        UserPlanDTO(
            id=uuid.uuid4(),
            title=f"Plan {i}",
            description=f"Description {i}",
            language="EN",
            difficulty_level="BEGINNER",
            image_url="",
            started_at=datetime.now(timezone.utc),
            total_days=30,
            tags=[]
        )
        for i in range(10)
    ]
    
    mock_response = UserPlansResponse(
        plans=mock_plans,
        skip=10,
        limit=10,
        total=50
    )
    
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", return_value=mock_response) as mock_get_plans:
        response = authenticated_client.get(
            "/users/me/plans?skip=10&limit=10",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["skip"] == 10
        assert data["limit"] == 10
        assert data["total"] == 50
        assert len(data["plans"]) == 10
        
        assert mock_get_plans.call_count == 1
        assert mock_get_plans.call_args.kwargs.get("skip") == 10
        assert mock_get_plans.call_args.kwargs.get("limit") == 10


def test_get_user_plans_with_all_filters(authenticated_client):
    """Test retrieval of user plans with all query parameters"""
    from pecha_api.plans.users.plan_users_response_models import UserPlansResponse
    
    mock_response = UserPlansResponse(
        plans=[],
        skip=5,
        limit=15,
        total=0
    )
    
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", return_value=mock_response) as mock_get_plans:
        response = authenticated_client.get(
            "/users/me/plans?status_filter=completed&skip=5&limit=15",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        assert mock_get_plans.call_count == 1
        assert mock_get_plans.call_args.kwargs.get("token") == VALID_TOKEN
        assert mock_get_plans.call_args.kwargs.get("status_filter") == "completed"
        assert mock_get_plans.call_args.kwargs.get("skip") == 5
        assert mock_get_plans.call_args.kwargs.get("limit") == 15


def test_get_user_plans_empty_result(authenticated_client):
    """Test retrieval when user has no enrolled plans"""
    from pecha_api.plans.users.plan_users_response_models import UserPlansResponse
    
    mock_response = UserPlansResponse(
        plans=[],
        skip=0,
        limit=20,
        total=0
    )
    
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", return_value=mock_response) as mock_get_plans:
        response = authenticated_client.get(
            "/users/me/plans",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["plans"] == []
        assert data["skip"] == 0
        assert data["limit"] == 20
        assert data["total"] == 0


def test_get_user_plans_invalid_token(authenticated_client):
    """Test retrieval with invalid authentication token"""
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans") as mock_get_plans:
        mock_get_plans.side_effect = HTTPException(
            status_code=401,
            detail={"error": "Unauthorized", "message": "Invalid token"}
        )
        
        response = authenticated_client.get(
            "/users/me/plans",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == {"error": "Unauthorized", "message": "Invalid token"}


def test_get_user_plans_negative_skip(authenticated_client):
    """Test retrieval with negative skip parameter (validation error)"""
    response = authenticated_client.get(
        "/users/me/plans?skip=-1",
        headers={"Authorization": f"Bearer {VALID_TOKEN}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_user_plans_invalid_limit(authenticated_client):
    """Test retrieval with limit exceeding maximum (validation error)"""
    response = authenticated_client.get(
        "/users/me/plans?limit=100",
        headers={"Authorization": f"Bearer {VALID_TOKEN}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_user_plans_zero_limit(authenticated_client):
    """Test retrieval with zero limit (validation error)"""
    response = authenticated_client.get(
        "/users/me/plans?limit=0",
        headers={"Authorization": f"Bearer {VALID_TOKEN}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_user_plans_unauthenticated(unauthenticated_client):
    """Test retrieval without authentication"""
    response = unauthenticated_client.get("/users/me/plans")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_plans_database_error(authenticated_client):
    """Test retrieval when database error occurs"""
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans") as mock_get_plans:
        mock_get_plans.side_effect = HTTPException(
            status_code=500,
            detail={"error": "Internal Server Error", "message": "Database connection failed"}
        )
        
        response = authenticated_client.get(
            "/users/me/plans",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error" in response.json()["detail"]


def test_get_user_plans_multiple_plans(authenticated_client):
    """Test retrieval of multiple enrolled plans"""
    from pecha_api.plans.users.plan_users_response_models import UserPlansResponse, UserPlanDTO
    from datetime import datetime, timezone
    
    mock_plans = [
        UserPlanDTO(
            id=uuid.uuid4(),
            title="Meditation Plan",
            description="Daily meditation practice",
            language="EN",
            difficulty_level="BEGINNER",
            image_url="https://s3.amazonaws.com/plan1.jpg",
            started_at=datetime.now(timezone.utc),
            total_days=21,
            tags=["meditation", "mindfulness"]
        ),
        UserPlanDTO(
            id=uuid.uuid4(),
            title="Advanced Dharma",
            description="Advanced Buddhist teachings",
            language="BO",
            difficulty_level="ADVANCED",
            image_url="https://s3.amazonaws.com/plan2.jpg",
            started_at=datetime.now(timezone.utc),
            total_days=90,
            tags=["dharma", "philosophy"]
        ),
        UserPlanDTO(
            id=uuid.uuid4(),
            title="Beginner's Guide",
            description="Introduction to Buddhism",
            language="EN",
            difficulty_level="BEGINNER",
            image_url="",
            started_at=datetime.now(timezone.utc),
            total_days=7,
            tags=["basics"]
        )
    ]
    
    mock_response = UserPlansResponse(
        plans=mock_plans,
        skip=0,
        limit=20,
        total=3
    )
    
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", return_value=mock_response) as mock_get_plans:
        response = authenticated_client.get(
            "/users/me/plans",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["plans"]) == 3
        assert data["total"] == 3
        
        assert data["plans"][0]["title"] == "Meditation Plan"
        assert data["plans"][1]["language"] == "BO"
        assert data["plans"][2]["image_url"] == ""
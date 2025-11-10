import uuid
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime

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
    from pecha_api.plans.plans_response_models import PlansResponse, PlanDTO
    
    plan_id = uuid.uuid4()
    mock_response = PlansResponse(
        plans=[
            PlanDTO(
                id=plan_id,
                title="Test Plan",
                description="Test Description",
                language="EN",
                difficulty_level="BEGINNER",
                image_url="https://s3.amazonaws.com/presigned-url",
                total_days=30,
                tags=["meditation", "mindfulness"],
                status="PUBLISHED",
                subscription_count=0,
            )
        ],
        skip=0,
        limit=20,
        total=1
    )
    
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", new_callable=AsyncMock, return_value=mock_response) as mock_get_plans:
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
    from pecha_api.plans.plans_response_models import PlansResponse
    
    mock_response = PlansResponse(
        plans=[],
        skip=0,
        limit=20,
        total=0,
    )
    
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", new_callable=AsyncMock, return_value=mock_response) as mock_get_plans:
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
    from pecha_api.plans.plans_response_models import PlansResponse, PlanDTO
    from datetime import datetime, timezone
    
    mock_plans = [
        PlanDTO(
            id=uuid.uuid4(),
            title=f"Plan {i}",
            description=f"Description {i}",
            language="EN",
            difficulty_level="BEGINNER",
            image_url="",
            total_days=30,
            tags=[],
            status="PUBLISHED",
            subscription_count=0,
        )
        for i in range(10)
    ]
    
    mock_response = PlansResponse(
        plans=mock_plans,
        skip=10,
        limit=10,
        total=50
    )
    
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", new_callable=AsyncMock, return_value=mock_response) as mock_get_plans:
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
    from pecha_api.plans.plans_response_models import PlansResponse
    
    mock_response = PlansResponse(
        plans=[],
        skip=5,
        limit=15,
        total=0
    )
    
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", new_callable=AsyncMock, return_value=mock_response) as mock_get_plans:
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
    from pecha_api.plans.plans_response_models import PlansResponse
    
    mock_response = PlansResponse(
        plans=[],
        skip=0,
        limit=20,
        total=0
    )
    
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", new_callable=AsyncMock, return_value=mock_response) as mock_get_plans:
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
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", new_callable=AsyncMock) as mock_get_plans:
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
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", new_callable=AsyncMock) as mock_get_plans:
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
    from pecha_api.plans.plans_response_models import PlansResponse, PlanDTO
    from datetime import datetime, timezone
    
    mock_plans = [
        PlanDTO(
            id=uuid.uuid4(),
            title="Meditation Plan",
            description="Daily meditation practice",
            language="EN",
            difficulty_level="BEGINNER",
            image_url="https://s3.amazonaws.com/plan1.jpg",
            total_days=21,
            tags=["meditation", "mindfulness"],
            status="PUBLISHED",
            subscription_count=0,
        ),
        PlanDTO(
            id=uuid.uuid4(),
            title="Advanced Dharma",
            description="Advanced Buddhist teachings",
            language="BO",
            difficulty_level="ADVANCED",
            image_url="https://s3.amazonaws.com/plan2.jpg",
            total_days=90,
            tags=["dharma", "philosophy"],
            status="PUBLISHED",
            subscription_count=0,
        ),
        PlanDTO(
            id=uuid.uuid4(),
            title="Beginner's Guide",
            description="Introduction to Buddhism",
            language="EN",
            difficulty_level="BEGINNER",
            image_url="",
            total_days=7,
            tags=["basics"],
            status="PUBLISHED",
            subscription_count=0,
        )
    ]
    
    mock_response = PlansResponse(
        plans=mock_plans,
        skip=0,
        limit=20,
        total=3
    )
    
    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", new_callable=AsyncMock, return_value=mock_response) as mock_get_plans:
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
def test_get_user_plans_success_default_pagination(authenticated_client):
    response_payload = {"plans": [], "skip": 0, "limit": 20, "total": 0}

    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", new_callable=AsyncMock, return_value=response_payload) as mock_get:
        response = authenticated_client.get(
            "/users/me/plans", headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == response_payload
        assert mock_get.call_count == 1
        assert mock_get.call_args.kwargs.get("token") == VALID_TOKEN
        assert mock_get.call_args.kwargs.get("status_filter") is None
        assert mock_get.call_args.kwargs.get("skip") == 0
        assert mock_get.call_args.kwargs.get("limit") == 20


def test_get_user_plans_with_filters_and_pagination(authenticated_client):
    response_payload = {"plans": [], "skip": 10, "limit": 5, "total": 0}

    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", new_callable=AsyncMock, return_value=response_payload) as mock_get:
        response = authenticated_client.get(
            "/users/me/plans?status_filter=active&skip=10&limit=5",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == response_payload
        assert mock_get.call_count == 1
        assert mock_get.call_args.kwargs.get("token") == VALID_TOKEN
        assert mock_get.call_args.kwargs.get("status_filter") == "active"
        assert mock_get.call_args.kwargs.get("skip") == 10
        assert mock_get.call_args.kwargs.get("limit") == 5


def test_get_user_plan_progress_details_success(authenticated_client):
    plan_id = uuid.uuid4()
    payload = {
        "id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "plan_id": plan_id,
        "plan": {"id": str(plan_id), "title": "Sample"},
        "started_at": datetime.utcnow(),
        "streak_count": 3,
        "longest_streak": 5,
        "status": "active",
        "is_completed": False,
        "created_at": datetime.utcnow(),
        "completed_at": None,
    }

    with patch("pecha_api.plans.users.plan_users_views.get_user_plan_progress", new_callable=AsyncMock, return_value=payload) as mock_get:
        response = authenticated_client.get(
            f"/users/me/plans/{plan_id}", headers={"Authorization": f"Bearer {VALID_TOKEN}"}
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["id"] == str(payload["id"])  # datetime fields auto-serialized
        assert body["plan_id"] == str(plan_id)
        assert mock_get.call_count == 1
        assert mock_get.call_args.kwargs.get("token") == VALID_TOKEN
        assert mock_get.call_args.kwargs.get("plan_id") == plan_id


def test_complete_task_success(authenticated_client):
    task_id = uuid.uuid4()

    with patch("pecha_api.plans.users.plan_users_views.complete_task_service", return_value=None) as mock_complete:
        response = authenticated_client.post(
            f"/users/me/tasks/{task_id}/completion",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.text == ""
        assert mock_complete.call_count == 1
        assert mock_complete.call_args.kwargs.get("token") == VALID_TOKEN
        assert mock_complete.call_args.kwargs.get("task_id") == task_id


# New tests for delete task endpoint
def test_delete_task_success(authenticated_client):
    task_id = uuid.uuid4()

    with patch("pecha_api.plans.users.plan_users_views.delete_task_service", return_value=None) as mock_delete:
        response = authenticated_client.delete(
            f"/users/me/task/{task_id}",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.text == ""
        assert mock_delete.call_count == 1
        assert mock_delete.call_args.kwargs.get("token") == VALID_TOKEN
        assert mock_delete.call_args.kwargs.get("task_id") == task_id


def test_delete_task_service_error_propagates(authenticated_client):
    task_id = uuid.uuid4()

    with patch("pecha_api.plans.users.plan_users_views.delete_task_service") as mock_delete:
        mock_delete.side_effect = HTTPException(
            status_code=404,
            detail={"error": "Bad request", "message": "Task not found"},
        )

        response = authenticated_client.delete(
            f"/users/me/task/{task_id}",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == {"error": "Bad request", "message": "Task not found"}


def test_delete_task_unauthenticated(unauthenticated_client):
    task_id = uuid.uuid4()

    response = unauthenticated_client.delete(f"/users/me/task/{task_id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_user_plan_day_details_success(authenticated_client):
    plan_id = uuid.uuid4()
    day_number = 4

    payload = {
        "id": str(uuid.uuid4()),
        "day_number": day_number,
        "is_completed": True,
        "tasks": [
            {
                "id": str(uuid.uuid4()),
                "title": "Task 1",
                "estimated_time": 10,
                "display_order": 1,
                "is_completed": True,
                "sub_tasks": [
                    {
                        "id": str(uuid.uuid4()),
                        "display_order": 1,
                        "is_completed": True,
                        "content_type": "TEXT",
                        "content": "A",
                    }
                ],
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Task 2",
                "estimated_time": 5,
                "display_order": 2,
                "is_completed": False,
                "sub_tasks": [
                    {
                        "id": str(uuid.uuid4()),
                        "display_order": 1,
                        "is_completed": False,
                        "content_type": "AUDIO",
                        "content": "B",
                    }
                ],
            },
        ],
    }

    with patch(
        "pecha_api.plans.users.plan_users_views.get_user_plan_day_details_service",
        return_value=payload,
    ) as mock_service:
        response = authenticated_client.get(
            f"/users/me/plan/{plan_id}/days/{day_number}",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["day_number"] == day_number
        assert body["is_completed"] is True
        assert isinstance(body["tasks"], list) and len(body["tasks"]) == 2

        # Service args
        assert mock_service.call_args.kwargs.get("token") == VALID_TOKEN
        assert mock_service.call_args.kwargs.get("plan_id") == plan_id
        assert mock_service.call_args.kwargs.get("day_number") == day_number


def test_get_user_plan_day_details_error_propagates(authenticated_client):
    plan_id = uuid.uuid4()
    day_number = 2

    with patch(
        "pecha_api.plans.users.plan_users_views.get_user_plan_day_details_service"
    ) as mock_service:
        mock_service.side_effect = HTTPException(
            status_code=404,
            detail={"error": "Not Found", "message": "Day not found"},
        )

        response = authenticated_client.get(
            f"/users/me/plan/{plan_id}/days/{day_number}",
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == {"error": "Not Found", "message": "Day not found"}


def test_get_user_plan_day_details_unauthenticated(unauthenticated_client):
    plan_id = uuid.uuid4()
    day_number = 1

    response = unauthenticated_client.get(f"/users/me/plan/{plan_id}/days/{day_number}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


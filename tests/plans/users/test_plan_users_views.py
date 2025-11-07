import uuid
import pytest
from unittest.mock import patch
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


def test_get_user_plans_success_default_pagination(authenticated_client):
    response_payload = {"plans": [], "skip": 0, "limit": 20, "total": 0}

    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", return_value=response_payload) as mock_get:
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

    with patch("pecha_api.plans.users.plan_users_views.get_user_enrolled_plans", return_value=response_payload) as mock_get:
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

    with patch("pecha_api.plans.users.plan_users_views.get_user_plan_progress", return_value=payload) as mock_get:
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



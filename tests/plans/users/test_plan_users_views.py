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



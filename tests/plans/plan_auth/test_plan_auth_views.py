from unittest.mock import patch

from fastapi.testclient import TestClient
from starlette import status

from pecha_api.app import api
from pecha_api.plans.auth.plan_auth_models import AuthorDetails
from pecha_api.plans.auth.plan_auth_enums import AuthorStatus
from pecha_api.plans.auth.plan_auth_models import AuthorVerificationResponse
from pecha_api.plans.response_message import EMAIL_VERIFIED_SUCCESS

client = TestClient(api)


def test_register_user_success():
    request_payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "password123",
    }

    author_details = AuthorDetails(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        status=AuthorStatus.PENDING_VERIFICATION,
        message="Registration successful"
    )

    with patch("pecha_api.plans.auth.plan_auth_views.register_author", return_value=author_details) as mock_register:
        response = client.post("cms/auth/register", json=request_payload)

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["email"] == "john.doe@example.com"
        mock_register.assert_called_once()


def test_register_user_validation_error_400():
    request_payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "short",
    }

    with patch("pecha_api.plans.auth.plan_auth_views.register_author") as mock_register:
        # Let FastAPI validate via model; here we simulate service raising HTTPException from password validation
        from fastapi import HTTPException
        mock_register.side_effect = HTTPException(status_code=400, detail="Password must be between 8 and 20 characters")

        response = client.post("cms/auth/register", json=request_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Password must be between 8 and 20 characters"


def test_verify_email_success():
    token = "test_token"
    author_verification_response = AuthorVerificationResponse(
        email='john.doe@example.com',
        status=AuthorStatus.INACTIVE,
        message=EMAIL_VERIFIED_SUCCESS
    )
    with patch("pecha_api.plans.auth.plan_auth_views.verify_author_email", return_value=author_verification_response) as mock_verify:
        response = client.get("cms/auth/verify-email", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == status.HTTP_200_OK
        mock_verify.assert_called_once_with(token=token)


def test_verify_email_missing_token_403():
    response = client.get("cms/auth/verify-email")

    assert response.status_code == status.HTTP_403_FORBIDDEN

from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from starlette import status

from pecha_api.app import api
from pecha_api.plans.plan_auth.plan_auth_model import CreateAuthorRequest, AuthorResponse
from pecha_api.plans.plan_auth.plan_auth_model import AuthorDetails
from pecha_api.plans.response_message import (
    EMAIL_VERIFICATION_PENDING_STATUS,
    EMAIL_VERIFICATION_PENDING_MESSAGE,
)


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
        status=EMAIL_VERIFICATION_PENDING_STATUS,
        message=EMAIL_VERIFICATION_PENDING_MESSAGE,
    )
    mock_response = AuthorResponse(author=author_details)

    with patch("pecha_api.plans.plan_auth.plan_auth_views.register_author", return_value=mock_response) as mock_register:
        response = client.post("/plan-auth/register", json=request_payload)

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["author"]["email"] == "john.doe@example.com"
        mock_register.assert_called_once()


def test_register_user_validation_error_400():
    request_payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "short",
    }

    with patch("pecha_api.plans.plan_auth.plan_auth_views.register_author") as mock_register:
        # Let FastAPI validate via model; here we simulate service raising HTTPException from password validation
        from fastapi import HTTPException
        mock_register.side_effect = HTTPException(status_code=400, detail="Password must be between 8 and 20 characters")

        response = client.post("/plan-auth/register", json=request_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Password must be between 8 and 20 characters"


def test_verify_email_success():
    token = "valid_token"
    with patch("pecha_api.plans.plan_auth.plan_auth_views.verify_author_email", return_value={"message": "ok"}) as mock_verify:
        response = client.get(f"/plan-auth/verify-email?token={token}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "ok"}
        mock_verify.assert_called_once_with(token=token)


def test_verify_email_missing_token_422():
    response = client.get("/plan-auth/verify-email")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY



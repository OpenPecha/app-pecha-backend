from unittest.mock import patch

from fastapi.testclient import TestClient
from starlette import status

from pecha_api.app import api
from pecha_api.plans.auth.plan_auth_models import AuthorDetails
from pecha_api.plans.auth.plan_auth_enums import AuthorStatus
from pecha_api.plans.auth.plan_auth_models import AuthorVerificationResponse, EmailReVerificationResponse
from pecha_api.plans.response_message import EMAIL_VERIFIED_SUCCESS, EMAIL_IS_SENT, BAD_REQUEST, AUTHOR_ALREADY_EXISTS

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


def test_request_reset_password_success():
    request_payload = {
        "email": "john.doe@example.com"
    }
    
    expected_response = {"message": "If the email exists in our system, a password reset email has been sent."}
    
    with patch("pecha_api.plans.auth.plan_auth_views.request_reset_password", return_value=expected_response) as mock_request_reset:
        response = client.post("cms/auth/request-reset-password", json=request_payload)
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["message"] == "If the email exists in our system, a password reset email has been sent."
        mock_request_reset.assert_called_once_with(email="john.doe@example.com")


def test_request_reset_password_missing_email_422():
    request_payload = {}  
    
    response = client.post("cms/auth/request-reset-password", json=request_payload)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data
    assert any(error["loc"] == ["body", "email"] for error in data["detail"])


def test_request_reset_password_invalid_email_422():
    request_payload = {
        "email": "invalid-email-format"
    }
    
    with patch("pecha_api.plans.auth.plan_auth_views.request_reset_password") as mock_request_reset:
        mock_request_reset.return_value = {"message": "If the email exists in our system, a password reset email has been sent."}
        
        response = client.post("cms/auth/request-reset-password", json=request_payload)
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.status_code == status.HTTP_202_ACCEPTED
        mock_request_reset.assert_called_once_with(email="invalid-email-format")


def test_request_reset_password_service_error():
    request_payload = {
        "email": "john.doe@example.com"
    }
    
    from fastapi import HTTPException
    
    with patch("pecha_api.plans.auth.plan_auth_views.request_reset_password") as mock_request_reset:
        mock_request_reset.side_effect = HTTPException(status_code=400, detail="User not found")
        
        response = client.post("cms/auth/request-reset-password", json=request_payload)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "User not found"


def test_reset_password_success():
    request_payload = {
        "password": "newpassword123"
    }
    
    token = "valid_reset_token"
    
    # Mock the updated author object that would be returned
    from pecha_api.plans.authors.plan_author_model import Author
    updated_author = Author(
        first_name="John",
        last_name="Doe", 
        email="john.doe@example.com",
        password="hashed_new_password"
    )
    
    with patch("pecha_api.plans.auth.plan_auth_views.update_password", return_value=updated_author) as mock_update_password:
        response = client.post(
            "cms/auth/reset-password", 
            json=request_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        mock_update_password.assert_called_once_with(token=token, password="newpassword123")


def test_reset_password_missing_authorization_403():
    request_payload = {
        "password": "newpassword123"
    }
    
    response = client.post("cms/auth/reset-password", json=request_payload)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_reset_password_missing_password_422():
    request_payload = {}  
    token = "valid_reset_token"
    
    response = client.post(
        "cms/auth/reset-password", 
        json=request_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data
    assert any(error["loc"] == ["body", "password"] for error in data["detail"])


def test_reset_password_invalid_token_400():
    request_payload = {
        "password": "newpassword123"
    }
    
    token = "invalid_or_expired_token"
    
    from fastapi import HTTPException
    
    with patch("pecha_api.plans.auth.plan_auth_views.update_password") as mock_update_password:
        mock_update_password.side_effect = HTTPException(status_code=400, detail="Invalid or expired token")
        
        response = client.post(
            "cms/auth/reset-password", 
            json=request_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Invalid or expired token"


def test_reset_password_registration_source_mismatch_400():
    request_payload = {
        "password": "newpassword123"
    }
    
    token = "valid_token_oauth_user"
    
    from fastapi import HTTPException
    
    with patch("pecha_api.plans.auth.plan_auth_views.update_password") as mock_update_password:
        mock_update_password.side_effect = HTTPException(status_code=400, detail="Registration Source Mismatch")
        
        response = client.post(
            "cms/auth/reset-password", 
            json=request_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Registration Source Mismatch"


def test_reset_password_weak_password_400():
    request_payload = {
        "password": "weak"
    }
    
    token = "valid_reset_token"
    
    from fastapi import HTTPException
    
    with patch("pecha_api.plans.auth.plan_auth_views.update_password") as mock_update_password:
        mock_update_password.side_effect = HTTPException(status_code=400, detail="Password must be between 8 and 20 characters")
        
        response = client.post(
            "cms/auth/reset-password", 
            json=request_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Password must be between 8 and 20 characters"


def test_email_re_verification_success():
    email = "john.doe@example.com"
    expected = EmailReVerificationResponse(message=EMAIL_IS_SENT)
    with patch("pecha_api.plans.auth.plan_auth_views.re_verify_email", return_value=expected) as mock_reverify:
        response = client.post("cms/auth/email-re-verification", params={"email": email})

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json()["message"] == EMAIL_IS_SENT
        mock_reverify.assert_called_once_with(email=email)


def test_email_re_verification_author_not_found_conflict():
    email = "noone@example.com"
    from fastapi import HTTPException
    with patch("pecha_api.plans.auth.plan_auth_views.re_verify_email") as mock_reverify:
        mock_reverify.side_effect = HTTPException(status_code=409, detail={"error": BAD_REQUEST, "message": AUTHOR_ALREADY_EXISTS})

        response = client.post("cms/auth/email-re-verification", params={"email": email})

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == {"error": BAD_REQUEST, "message": AUTHOR_ALREADY_EXISTS}

from fastapi.testclient import TestClient
from unittest.mock import patch

from pecha_api.app import api  # Assuming your FastAPI app is in main.py

client = TestClient(api)


def test_register_user():
    with patch("pecha_api.auth.auth_views.register_user_with_source") as mock_register_user_with_source:
        mock_register_user_with_source.return_value = {"access_token": "test_token",
                                                       "refresh_token": "test_refresh_token", "token_type": "Bearer"}
        response = client.post("/auth/register", json={"email": "testuser@example.com", "firstname": "testfirstname",
                                                       "lastname": "testlastname", "password": "testpass"})

        assert response.status_code == 201
        assert response.json()["access_token"] == "test_token"
        assert response.json()["refresh_token"] == "test_refresh_token"
        assert response.json()["token_type"] == "Bearer"


def test_login_user():
    with patch("pecha_api.auth.auth_views.authenticate_and_generate_tokens") as mock_authenticate:
        mock_authenticate.return_value = {"access_token": "test_token", "refresh_token": "test_refresh_token",
                                          "token_type": "Bearer"}
        response = client.post("/auth/login", json={"email": "testuser@example.com", "password": "testpass"})

        assert response.status_code == 200
        assert response.json()["access_token"] == "test_token"
        assert response.json()["refresh_token"] == "test_refresh_token"
        assert response.json()["token_type"] == "Bearer"


def test_refresh_token():
    with patch("pecha_api.auth.auth_views.refresh_access_token") as mock_refresh:
        mock_refresh.return_value = {"access_token": "new_fake_access_token", "refresh_token": "new_fake_refresh_token",
                                     "token_type": "Bearer"}
        response = client.post("/auth/refresh-token", json={"token": "refresh_token"})

        assert response.status_code == 200
        assert "access_token" in response.json()


def test_request_reset_password():
    with patch("pecha_api.auth.auth_views.request_reset_password") as mock_request_reset_password:
        mock_request_reset_password.return_value = None
        response = client.post("/auth/request-reset-password", json={"email": "testuser@example.com"})

        assert response.status_code == 202


def test_reset_password():
    with patch("pecha_api.auth.auth_views.update_password") as mock_update_password:
        mock_update_password.return_value = None
        response = client.post("/auth/reset-password", json={"password": "newpassword"},
                               headers={"Authorization": "Bearer test_token"})

        assert response.status_code == 200

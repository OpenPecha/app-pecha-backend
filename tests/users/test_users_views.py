from unittest.mock import patch
from typing import Optional

from fastapi import HTTPException
from fastapi.testclient import TestClient
from pecha_api.app import api
from pecha_api.users.user_response_models import UserInfoResponse
from fastapi import HTTPException
client = TestClient(api)


def test_get_user_information():
    user_info_response = UserInfoResponse(
        firstname="John",
        lastname="Doe",
        username="john.does",
        email="john.doe@gmail.com",
        title="",
        organization="",
        educations=[],
        avatar_url="",
        about_me="",
        followers=0,
        following=0,
        social_profiles=[]
    )
    with patch("pecha_api.users.users_views.get_user_info") as mock_get_user_info:
        mock_get_user_info.return_value = user_info_response
        response = client.get("/users/info", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 200


def test_update_user_information():
    user_info_request = {
        "firstname": "John",
        "lastname": "Doe",
        "title": "Software Engineer",
        "organization": "Tech Corp",
        "educations": [
            "Bachelor's in Computer Science",
            "Master's in Data Science"
        ],
        "avatar_url": "https://example.com/avatar.jpg",
        "about_me": "Passionate about technology and solving complex problems.",
        "social_profiles": []
    }
    with patch("pecha_api.users.users_views.update_user_info") as mock_update_user_info:
        mock_update_user_info.return_value = None
        response = client.post("/users/info", json=user_info_request, headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 201

def test_upload_user_avatar_image():
    with patch("pecha_api.users.users_views.upload_user_image") as mock_upload_user_image:
        mock_upload_user_image.return_value = {"message": "Image uploaded successfully"}
        with open("tests/test_image_200kb.jpg", "rb") as image_file:
            response = client.post(
                "/users/upload",
                files={"file": ("test_image_200kb.jpg", image_file, "image/jpeg")},
                headers={"Authorization": "Bearer testtoken"}
            )
        assert response.status_code == 201
        assert response.json() == {"message": "Image uploaded successfully"}

def test_upload_non_image_file():
    with patch("pecha_api.users.users_views.upload_user_image",
               side_effect=HTTPException(status_code=400, detail="Only image files are allowed.")):
        with open("tests/test_file.txt", "rb") as non_image_file:
            response = client.post(
                "/users/upload",
                files={"file": ("test_file.txt", non_image_file, "text/plain")},
                headers={"Authorization": "Bearer testtoken"}
            )
        assert response.status_code == 400
        assert response.json() == {"detail": "Only image files are allowed."}


def test_upload_large_file():
    with patch("pecha_api.users.users_views.upload_user_image",
               side_effect=HTTPException(status_code=413, detail="File size exceeds 2 MB limit")):
        with open("tests/test_image_2mb.jpg", "rb") as large_file:
            response = client.post(
                "/users/upload",
                files={"file": ("test_large_image.jpg", large_file, "image/jpeg")},
                headers={"Authorization": "Bearer testtoken"}
            )
        assert response.status_code == 413
        assert response.json() == {"detail": "File size exceeds 2 MB limit"}


def test_get_user_detail_by_username_success():
    user_info_response = UserInfoResponse(
        firstname="Jane",
        lastname="Smith",
        username="jane.smith",
        email="jane.smith@example.com",
        title="Senior Developer",
        organization="Tech Solutions Inc",
        location="San Francisco",
        educations=["Computer Science", "Software Engineering"],
        avatar_url="https://example.com/avatar.jpg",
        about_me="Experienced software developer with passion for clean code.",
        followers=150,
        following=75,
        social_profiles=[]
    )
    
    with patch("pecha_api.users.users_views.get_user_info_by_username") as mock_get_user_info:
        mock_get_user_info.return_value = user_info_response
        
        response = client.get("/users/jane.smith")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["username"] == "jane.smith"
        assert response_data["firstname"] == "Jane"
        assert response_data["lastname"] == "Smith"
        assert response_data["email"] == "jane.smith@example.com"
        assert response_data["title"] == "Senior Developer"
        assert response_data["organization"] == "Tech Solutions Inc"
        assert response_data["location"] == "San Francisco"
        assert response_data["about_me"] == "Experienced software developer with passion for clean code."
        assert response_data["followers"] == 150
        assert response_data["following"] == 75
        assert response_data["educations"] == ["Computer Science", "Software Engineering"]
        mock_get_user_info.assert_called_once_with("jane.smith")


def test_get_user_detail_by_username_not_found():
    with patch("pecha_api.users.users_views.get_user_info_by_username") as mock_get_user_info:
        mock_get_user_info.side_effect = HTTPException(status_code=404, detail="User not found")
        
        response = client.get("/users/nonexistent.user")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"
        
        mock_get_user_info.assert_called_once_with("nonexistent.user")


def test_get_user_detail_by_username_with_special_characters():
    user_info_response = UserInfoResponse(
        firstname="Test",
        lastname="User",
        username="test.user-123",
        email="test.user@example.com",
        title="",
        organization="",
        location="",
        educations=[],
        avatar_url="",
        about_me="",
        followers=0,
        following=0,
        social_profiles=[]
    )
    
    with patch("pecha_api.users.users_views.get_user_info_by_username") as mock_get_user_info:
        mock_get_user_info.return_value = user_info_response
        
        response = client.get("/users/test.user-123")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["username"] == "test.user-123"
        mock_get_user_info.assert_called_once_with("test.user-123")


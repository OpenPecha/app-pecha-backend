from unittest.mock import patch

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


from unittest.mock import patch

from fastapi.testclient import TestClient
from pecha_api.app import api
from pecha_api.users.user_response_models import UserInfoResponse

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
from unittest.mock import patch

from fastapi.testclient import TestClient
from fastapi import HTTPException

from pecha_api.app import api


client = TestClient(api)


def test_follow_user_success():
    expected_response = {"message": "success", "is_following": True, "follower_count": 5}
    with patch("pecha_api.user_follows.user_follow_views.post_user_follow") as mock_post_follow:
        mock_post_follow.return_value = expected_response
        response = client.post(
            "/users/follow",
            json={"username": "target.user"},
            headers={"Authorization": "Bearer testtoken"},
        )

    assert response.status_code == 201
    assert response.json() == expected_response


def test_follow_user_user_not_found():
    with patch(
        "pecha_api.user_follows.user_follow_views.post_user_follow",
        side_effect=HTTPException(status_code=404, detail="User not found"),
    ):
        response = client.post(
            "/users/follow",
            json={"username": "missing.user"},
            headers={"Authorization": "Bearer testtoken"},
        )

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_follow_user_cannot_follow_self():
    with patch(
        "pecha_api.user_follows.user_follow_views.post_user_follow",
        side_effect=HTTPException(status_code=400, detail="Bad Request - Cannot follow yourself"),
    ):
        response = client.post(
            "/users/follow",
            json={"username": "current.user"},
            headers={"Authorization": "Bearer testtoken"},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "Bad Request - Cannot follow yourself"}



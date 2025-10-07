import pytest
from unittest.mock import patch, MagicMock

from fastapi import HTTPException
from starlette import status

from pecha_api.user_follows.user_follow_services import post_user_follow


def _mock_session_cm():
    cm = MagicMock()
    cm.__enter__.return_value = MagicMock()
    cm.__exit__.return_value = None
    return cm


def test_post_user_follow_success_creates_follow():
    current_user = type("User", (), {"id": "follower-id"})
    target_user = type("User", (), {"id": "target-id"})

    with patch("pecha_api.user_follows.user_follow_services.validate_and_extract_user_details", return_value=current_user), \
         patch("pecha_api.user_follows.user_follow_services.database.SessionLocal", return_value=_mock_session_cm()), \
         patch("pecha_api.user_follows.user_follow_services.get_user_by_username", return_value=target_user), \
         patch("pecha_api.user_follows.user_follow_services.is_user_following_target_user", return_value=None), \
         patch("pecha_api.user_follows.user_follow_services.create_user_follow") as mock_create_follow, \
         patch("pecha_api.user_follows.user_follow_services.get_user_follow_count", return_value=10) as mock_follow_count:

        resp = post_user_follow(token="tkn", following_username="target")

        mock_create_follow.assert_called_once_with(follower_id="follower-id", following_id="target-id")
        mock_follow_count.assert_called_once_with(following_id="target-id")

        assert resp.message == "success"
        assert resp.is_following is True
        assert resp.follower_count == 10


def test_post_user_follow_success_already_following():
    current_user = type("User", (), {"id": "follower-id"})
    target_user = type("User", (), {"id": "target-id"})

    with patch("pecha_api.user_follows.user_follow_services.validate_and_extract_user_details", return_value=current_user), \
         patch("pecha_api.user_follows.user_follow_services.database.SessionLocal", return_value=_mock_session_cm()), \
         patch("pecha_api.user_follows.user_follow_services.get_user_by_username", return_value=target_user), \
         patch("pecha_api.user_follows.user_follow_services.is_user_following_target_user", return_value=True), \
         patch("pecha_api.user_follows.user_follow_services.create_user_follow") as mock_create_follow, \
         patch("pecha_api.user_follows.user_follow_services.get_user_follow_count", return_value=7):

        resp = post_user_follow(token="tkn", following_username="target")

        mock_create_follow.assert_not_called()
        assert resp.message == "success"
        assert resp.is_following is True
        assert resp.follower_count == 7


def test_post_user_follow_user_not_found():
    current_user = type("User", (), {"id": "follower-id"})

    with patch("pecha_api.user_follows.user_follow_services.validate_and_extract_user_details", return_value=current_user), \
         patch("pecha_api.user_follows.user_follow_services.database.SessionLocal", return_value=_mock_session_cm()), \
         patch("pecha_api.user_follows.user_follow_services.get_user_by_username", return_value=None):

        with pytest.raises(HTTPException) as exc:
            post_user_follow(token="tkn", following_username="missing")

        assert exc.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc.value.detail == "User not found"


def test_post_user_follow_cannot_follow_self():
    current_user = type("User", (), {"id": "same-id"})
    target_user = type("User", (), {"id": "same-id"})

    with patch("pecha_api.user_follows.user_follow_services.validate_and_extract_user_details", return_value=current_user), \
         patch("pecha_api.user_follows.user_follow_services.database.SessionLocal", return_value=_mock_session_cm()), \
         patch("pecha_api.user_follows.user_follow_services.get_user_by_username", return_value=target_user):

        with pytest.raises(HTTPException) as exc:
            post_user_follow(token="tkn", following_username="self")

        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.value.detail == "Bad Request - Cannot follow yourself"



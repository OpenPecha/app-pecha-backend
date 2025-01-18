from unittest.mock import patch
from pecha_api.users.users_service import get_user_info, update_user_info
from pecha_api.users.user_response_models import UserInfoRequest
from pecha_api.users.users_models import Users, SocialMediaAccount
from pecha_api.users.users_enums import SocialProfile


def test_get_user_info_success():
    token = "valid_token"
    user = Users(
        firstname="John",
        lastname="Doe",
        username="johndoe",
        email="john.doe@example.com",
        title="Developer",
        organization="ExampleOrg",
        education="BSc, MSc",
        avatar_url="http://example.com/avatar.jpg",
        about_me="About John",
        social_media_accounts=[]
    )

    with patch("pecha_api.users.users_service.decode_token", return_value={"sub": "john.doe@example.com"}):
        with patch("pecha_api.users.users_service.get_user_by_email", return_value=user):
            response = get_user_info(token)
            assert response.firstname == "John"
            assert response.lastname == "Doe"
            assert response.username == "johndoe"
            assert response.email == "john.doe@example.com"


def test_get_user_info_with_social_accounts():
    token = "valid_token"
    user = Users(
        firstname="John",
        lastname="Doe",
        username="johndoe",
        email="john.doe@example.com",
        title="Developer",
        organization="ExampleOrg",
        education="BSc, MSc",
        avatar_url="http://example.com/avatar.jpg",
        about_me="About John",
        social_media_accounts=[
            SocialMediaAccount(platform_name="EMAIL", profile_url="john.doe@gmail.com"),
            SocialMediaAccount(platform_name="LinkedIn", profile_url="http://linkedin.com/in/johndoe")
        ]
    )

    with patch("pecha_api.users.users_service.decode_token", return_value={"sub": "john.doe@example.com"}):
        with patch("pecha_api.users.users_service.get_user_by_email", return_value=user):
            response = get_user_info(token)
            assert response.firstname == "John"
            assert response.lastname == "Doe"
            assert response.username == "johndoe"
            assert response.email == "john.doe@example.com"
            assert len(response.social_profiles) == 2
            assert response.social_profiles[0].account.name == SocialProfile.EMAIL.name
            assert response.social_profiles[0].url == "john.doe@gmail.com"
            assert response.social_profiles[1].account.name == SocialProfile.LINKEDIN.name
            assert response.social_profiles[1].url == "http://linkedin.com/in/johndoe"


def test_get_user_info_invalid_token():
    token = "invalid_token"

    with patch("pecha_api.users.users_service.decode_token", return_value={"sub": None}):
        response = get_user_info(token)
        assert response.status_code == 401
        assert response.body == b'{"message":"Invalid token"}'


def test_update_user_info_success():
    token = "valid_token"
    user_info_request = UserInfoRequest(
        firstname="Jane",
        lastname="Doe",
        title="Manager",
        organization="ExampleOrg",
        educations=["BSc", "MBA"],
        avatar_url="http://example.com/avatar.jpg",
        about_me="About Jane",
        social_profiles=[]
    )
    user = Users(
        firstname="John",
        lastname="Doe",
        username="johndoe",
        email="john.doe@example.com",
        title="Developer",
        organization="ExampleOrg",
        education="BSc, MSc",
        avatar_url="http://example.com/avatar.jpg",
        about_me="About John",
        social_media_accounts=[]
    )

    with patch("pecha_api.users.users_service.decode_token", return_value={"sub": "john.doe@example.com"}):
        with patch("pecha_api.users.users_service.get_user_by_email", return_value=user):
            with patch("pecha_api.users.users_service.update_user") as mock_update_user:
                update_user_info(token, user_info_request)
                mock_update_user.assert_called_once()


def test_update_user_info_invalid_token():
    token = "invalid_token"
    user_info_request = UserInfoRequest(
        firstname="Jane",
        lastname="Doe",
        title="Manager",
        organization="ExampleOrg",
        educations=["BSc", "MBA"],
        avatar_url="http://example.com/avatar.jpg",
        about_me="About Jane",
        social_profiles=[]
    )

    with patch("pecha_api.users.users_service.decode_token", return_value={"sub": None}):
        response = update_user_info(token, user_info_request)
        assert response.status_code == 401
        assert response.body == b'{"message":"Invalid token"}'

import pytest

from pecha_api.users.users_service import get_user_info, update_user_info, validate_and_compress_image
from pecha_api.users.user_response_models import UserInfoRequest
from pecha_api.users.users_models import Users, SocialMediaAccount
from pecha_api.users.users_enums import SocialProfile
from unittest.mock import patch, MagicMock
from fastapi import HTTPException, UploadFile
from pecha_api.users.users_service import upload_user_image
import io


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


def test_upload_user_image_success():
    token = "valid_token"
    file_content = io.BytesIO(b"fake_image_data")

    file = UploadFile(filename="test.jpg", file=file_content)

    with patch("pecha_api.users.users_service.validate_and_extract_user_details", return_value=MagicMock(id="user_id")):
        with patch("pecha_api.users.users_service.validate_and_compress_image", return_value=file_content):
            with patch("pecha_api.users.users_service.delete_file") as mock_delete_file:
                with patch("pecha_api.users.users_service.upload_bytes", return_value="s3_key"):
                    with patch("pecha_api.users.users_service.generate_presigned_upload_url",
                               return_value="http://example.com/presigned_url"):
                        response = upload_user_image(token, file)
                        mock_delete_file.assert_called_once_with(file_path="images/profile_images/user_id.jpg")
                        assert response == "http://example.com/presigned_url"


def test_upload_user_image_invalid_token():
    token = "invalid_token"
    file_content = io.BytesIO(b"fake_image_data")
    file = UploadFile(filename="test.jpg", file=file_content)

    with patch("pecha_api.users.users_service.validate_and_extract_user_details",
               side_effect=HTTPException(status_code=401, detail="Invalid token")):
        response = upload_user_image(token, file)
        assert response.status_code == 401
        assert response.body == b'{"message":"Invalid token"}'


def test_validate_and_compress_image_success():
    file_content = io.BytesIO(b"fake_image_data")
    file = UploadFile(filename="test.jpg", file=file_content)

    with patch("pecha_api.users.users_service.get_int", side_effect=[5, 75]):
        with patch("pecha_api.users.users_service.Image.open") as mock_open:
            mock_image = MagicMock()
            mock_open.return_value = mock_image
            mock_image.save = MagicMock()

            compressed_image = validate_and_compress_image(file=file, content_type="image/jpeg")
            assert isinstance(compressed_image, io.BytesIO)
            mock_image.save.assert_called_once_with(compressed_image, format="JPEG", quality=75)


def test_validate_and_compress_image_invalid_file_type():
    file_content = io.BytesIO(b"fake_image_data")
    file = UploadFile(filename="test.txt", file=file_content)

    with pytest.raises(HTTPException) as exc_info:
        validate_and_compress_image(file=file, content_type="text/plain")
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Only image files are allowed."


def test_validate_and_compress_image_file_too_large():
    file_content = io.BytesIO(b"fake_image_data" * 1024 * 1024 * 6)  # 6 MB
    file = UploadFile(filename="test.jpg", file=file_content)

    with patch("pecha_api.users.users_service.get_int", return_value=5):
        with pytest.raises(HTTPException) as exc_info:
            validate_and_compress_image(file=file, content_type="image/jpeg")
        assert exc_info.value.status_code == 413
        assert exc_info.value.detail == "File size exceeds 5 MB limit."


def test_validate_and_compress_image_processing_failure():
    file_content = io.BytesIO(b"fake_image_data")
    file = UploadFile(filename="test.jpg", file=file_content)

    with patch("pecha_api.users.users_service.get_int", side_effect=[5, 75]):
        with patch("pecha_api.users.users_service.Image.open", side_effect=Exception("Processing error")):
            with pytest.raises(HTTPException) as exc_info:
                validate_and_compress_image(file=file, content_type="image/jpeg")
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Failed to process the image: Processing error"

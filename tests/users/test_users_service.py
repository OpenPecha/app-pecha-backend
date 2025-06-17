import jose
import pytest
from jose.exceptions import JWTClaimsError
from jwt import ExpiredSignatureError
from starlette import status
from pecha_api.image_utils import ImageUtils
from pecha_api.utils import Utils
from pecha_api.users.users_service import get_user_info, update_user_info, \
    validate_and_extract_user_details, verify_admin_access, get_social_profile, update_social_profiles
from pecha_api.users.user_response_models import UserInfoRequest, SocialMediaProfile
from pecha_api.users.users_models import Users, SocialMediaAccount
from pecha_api.users.users_enums import SocialProfile
from unittest.mock import patch, MagicMock
from fastapi import HTTPException, UploadFile
from pecha_api.users.users_service import upload_user_image
import io
import PIL.Image


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

    with patch("pecha_api.users.users_service.validate_token", return_value={"email": "john.doe@example.com"}), \
            patch("pecha_api.users.users_service.get_user_by_email", return_value=user):
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

    with patch("pecha_api.users.users_service.validate_token", return_value={"email": "john.doe@example.com"}), \
            patch("pecha_api.users.users_service.get_user_by_email", return_value=user):
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

    with patch("pecha_api.users.users_service.validate_token", return_value={"email": None}):
        try:
            get_user_info(token)
        except HTTPException as e:
            assert e.status_code == status.HTTP_401_UNAUTHORIZED
            assert e.detail == 'Invalid or no token found'


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

    with patch("pecha_api.users.users_service.validate_token", return_value={"email": "john.doe@example.com"}), \
            patch("pecha_api.users.users_service.get_user_by_email", return_value=user), \
            patch("pecha_api.users.users_service.update_user") as mock_update_user:
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

    with patch("pecha_api.users.users_service.validate_token", return_value={"email": None}):
        try:
            update_user_info(token, user_info_request)
        except HTTPException as e:
            assert e.status_code == status.HTTP_401_UNAUTHORIZED
            assert e.detail == 'Invalid or no token found'


def test_update_user_info_500_db_error():
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

    with patch("pecha_api.users.users_service.validate_token", return_value={"email": "john.doe@example.com"}), \
            patch("pecha_api.users.users_service.get_user_by_email", return_value=user), \
            patch("pecha_api.users.users_service.update_user", side_effect=Exception("Db Error")):
        try:
            update_user_info(token, user_info_request)
        except HTTPException as e:
            assert e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert e.detail == 'Internal Server Error'


def test_upload_user_image_success():
    token = "valid_token"
    file_content = io.BytesIO(b"fake_image_data")

    file = UploadFile(filename="test.jpg", file=file_content)

    with patch("pecha_api.users.users_service.validate_and_extract_user_details", return_value=MagicMock(id="user_id")), \
            patch("pecha_api.image_utils.ImageUtils.validate_and_compress_image", return_value=file_content), \
            patch("pecha_api.users.users_service.delete_file") as mock_delete_file, \
            patch("pecha_api.users.users_service.update_user") as mock_update_user, \
            patch("pecha_api.users.users_service.upload_bytes", return_value="s3_key"), \
            patch("pecha_api.users.users_service.generate_presigned_upload_url",
                  return_value="http://example.com/presigned_url"):
        response = upload_user_image(token, file)
        mock_update_user.assert_called_once()
        mock_delete_file.assert_called_once_with(file_path="images/profile_images/user_id.jpg")
        assert response == "http://example.com/presigned_url"


def test_upload_user_image_invalid_token():
    token = "invalid_token"
    file_content = io.BytesIO(b"fake_image_data")
    file = UploadFile(filename="test.jpg", file=file_content)

    with patch("pecha_api.users.users_service.validate_and_extract_user_details",
               side_effect=HTTPException(status_code=401, detail="Invalid or no token found")):
        try:
            upload_user_image(token, file)
        except HTTPException as e:
            assert e.status_code == status.HTTP_401_UNAUTHORIZED
            assert e.detail == 'Invalid or no token found'


def test_validate_and_compress_image_success():
    file_content = io.BytesIO(b"fake_image_data")
    file = UploadFile(filename="test.jpg", file=file_content)

    with patch("pecha_api.image_utils.get_int", side_effect=[5, 75]), \
            patch("PIL.Image.open") as mock_open:
        mock_image = MagicMock()
        mock_image.mode = 'RGB'  # Set the mode to RGB
        mock_open.return_value = mock_image
        mock_image.save = MagicMock()
        image_utils = ImageUtils()
        compressed_image = image_utils.validate_and_compress_image(file=file, content_type="image/jpeg")
        assert isinstance(compressed_image, io.BytesIO)
        mock_image.save.assert_called_once_with(compressed_image, format="JPEG", quality=75)


def test_validate_and_compress_image_invalid_file_type():
    file_content = io.BytesIO(b"fake_image_data")
    file = UploadFile(filename="test.txt", file=file_content)
    try:
        image_utils = ImageUtils()
        image_utils.validate_and_compress_image(file=file, content_type="text/plain")
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST
        assert e.detail == 'Only image files are allowed'


def test_validate_and_compress_image_file_too_large():
    file_content = io.BytesIO(b"fake_image_data" * 1024 * 1024 * 6)  # 6 MB
    file = UploadFile(filename="test.jpg", file=file_content)

    with patch("pecha_api.users.users_service.get_int", return_value=5), \
            pytest.raises(HTTPException) as exc_info:
        image_utils = ImageUtils()
        image_utils.validate_and_compress_image(file=file, content_type="image/jpeg")
    assert exc_info.value.status_code == 413
    assert exc_info.value.detail == "File size exceeds 5MB limit"


def test_validate_and_compress_image_processing_failure():
    file_content = io.BytesIO(b"fake_image_data")
    file = UploadFile(filename="test.jpg", file=file_content)

    with patch("pecha_api.users.users_service.get_int", side_effect=[5, 75]), \
            patch("pecha_api.users.users_service.Image.open", side_effect=Exception("Processing error")), \
            pytest.raises(HTTPException) as exc_info:
        image_utils = ImageUtils()
        image_utils.validate_and_compress_image(file=file, content_type="image/jpeg")
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Failed to process the image"


def test_validate_and_extract_user_details_invalid_token():
    token = "invalid_token"

    with patch("pecha_api.users.users_service.validate_token", return_value={"email": None}):
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_user_details(token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid or no token found"


def test_validate_and_extract_user_details_expired_signature():
    token = "expired_token"

    with patch("pecha_api.users.users_service.validate_token", side_effect=ExpiredSignatureError):
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_user_details(token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid or no token found"


def test_validate_and_extract_user_details_jose_expired_signature():
    token = "expired_token"

    with patch("pecha_api.users.users_service.validate_token", side_effect=jose.ExpiredSignatureError):
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_user_details(token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid or no token found"


def test_validate_and_extract_user_details_jwt_claims_error():
    token = "invalid_claims_token"

    with patch("pecha_api.users.users_service.validate_token", side_effect=JWTClaimsError):
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_user_details(token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid or no token found"


def test_validate_and_extract_user_details_value_error():
    token = "value_error_token"

    with patch("pecha_api.users.users_service.validate_token", side_effect=ValueError("Invalid or no token found")):
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_user_details(token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid or no token found"


def test_verify_admin_access_true():
    token = "valid_admin_token"
    user = Users(
        firstname="Admin",
        lastname="User",
        username="adminuser",
        email="admin.user@example.com",
        title="Admin",
        organization="ExampleOrg",
        education="BSc, MSc",
        avatar_url="http://example.com/avatar.jpg",
        about_me="About Admin",
        social_media_accounts=[],
        is_admin=True
    )

    with patch("pecha_api.users.users_service.validate_token", return_value={"email": "admin.user@example.com"}), \
            patch("pecha_api.users.users_service.get_user_by_email", return_value=user):
        assert verify_admin_access(token) is True


def test_verify_admin_access_false():
    token = "valid_non_admin_token"
    user = Users(
        firstname="Regular",
        lastname="User",
        username="regularuser",
        email="regular.user@example.com",
        title="User",
        organization="ExampleOrg",
        education="BSc, MSc",
        avatar_url="http://example.com/avatar.jpg",
        about_me="About User",
        social_media_accounts=[],
        is_admin=False
    )

    with patch("pecha_api.users.users_service.validate_and_extract_user_details", return_value=user):
        assert verify_admin_access(token) is False


def test_verify_admin_access_no_attribute_false():
    token = "valid_non_admin_token"
    user = Users(
        firstname="Regular",
        lastname="User",
        username="regularuser",
        email="regular.user@example.com",
        title="User",
        organization="ExampleOrg",
        education="BSc, MSc",
        avatar_url="http://example.com/avatar.jpg",
        about_me="About User",
        social_media_accounts=[]
    )

    with patch("pecha_api.users.users_service.validate_and_extract_user_details", return_value=user):
        assert verify_admin_access(token) is False


def test_get_social_profile_valid():
    assert get_social_profile("EMAIL") == SocialProfile.EMAIL
    assert get_social_profile("LinkedIn") == SocialProfile.LINKEDIN
    assert get_social_profile("X_COM") == SocialProfile.X_COM
    assert get_social_profile("FACEBOOK") == SocialProfile.FACEBOOK
    assert get_social_profile("YOUTUBE") == SocialProfile.YOUTUBE


def test_get_social_profile_invalid():
    with pytest.raises(ValueError) as exc_info:
        get_social_profile("INVALID_PROFILE")
    assert str(exc_info.value) == "'INVALID_PROFILE' is not a valid SocialProfile"


def test_extract_s3_key_valid_url():
    presigned_url = "https://example-bucket.s3.amazonaws.com/images/profile_images/user_id.jpg"
    assert Utils.extract_s3_key(presigned_url) == "images/profile_images/user_id.jpg"


def test_extract_s3_key_empty_url():
    assert Utils.extract_s3_key("") == ""


def test_extract_s3_key_invalid_url():
    presigned_url = "https://example-bucket.s3.amazonaws.com/"
    assert Utils.extract_s3_key(presigned_url) == ""


def test_update_social_profiles():
    user = Users(
        id="user_id",
        social_media_accounts=[
            SocialMediaAccount(platform_name="EMAIL", profile_url="john.doe@gmail.com")
        ]
    )
    social_profiles = [
        SocialMediaProfile(account=SocialProfile.EMAIL, url="john.doe@newemail.com"),
        SocialMediaProfile(account=SocialProfile.LINKEDIN, url="http://linkedin.com/in/johndoe")
    ]

    update_social_profiles(user, social_profiles)

    assert len(user.social_media_accounts) == 2
    assert user.social_media_accounts[0].platform_name == "EMAIL"
    assert user.social_media_accounts[0].profile_url == "john.doe@newemail.com"
    assert user.social_media_accounts[1].platform_name == "LINKEDIN"
    assert user.social_media_accounts[1].profile_url == "http://linkedin.com/in/johndoe"

import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import UploadFile, HTTPException
from starlette import status
import os

from pecha_api.app import api
from pecha_api.plans.image_upload.media_response_models import MediaUploadResponse
from pecha_api.plans.response_message import (
    IMAGE_UPLOAD_SUCCESS,
    INVALID_FILE_FORMAT,
    FILE_TOO_LARGE,
    UNEXPECTED_ERROR_UPLOAD,
    AUTHOR_NOT_FOUND
)
from pecha_api.plans.authors.plan_author_model import Author

mock_success_response = MediaUploadResponse(
    url="https://s3.amazonaws.com/bucket/images/plan_images/uuid/test_image.jpg",
    key="images/plan_images/uuid/test_image.jpg",
    path="images/plan_images/uuid",
    message=IMAGE_UPLOAD_SUCCESS
)

mock_author = Author(
    id=1,
    first_name="Test",
    last_name="Author",
    email="test@example.com",
    image_url="https://example.com/image.jpg"
)

@pytest.fixture(autouse=True)
def mock_validate_author():
    with patch("pecha_api.plans.image_upload.media_services.validate_and_extract_author_details") as mock_func:
        mock_func.return_value = mock_author
        yield mock_func

@pytest.fixture
def mock_upload_service():
    with patch("pecha_api.plans.image_upload.media_views.upload_media_file") as mock_func:
        mock_func.return_value = mock_success_response
        yield mock_func
        
@pytest.fixture
def client():
    from pecha_api.plans.image_upload.media_views import oauth2_scheme
    
    original_dependency = api.dependency_overrides.copy()
    
    def get_token_override():
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
    
    api.dependency_overrides[oauth2_scheme] = get_token_override
    
    test_client = TestClient(api)
    
    yield test_client
    
    api.dependency_overrides = original_dependency


@pytest.fixture
def client_no_auth():
    original_dependency = api.dependency_overrides.copy()
    
    test_client = TestClient(api)
    
    yield test_client
    
    api.dependency_overrides = original_dependency


def create_test_image_file(filename: str = "test_image.jpg", content: bytes = b"fake_image_content", content_type: str = "image/jpeg"):
    return ("file", (filename, content, content_type))


def test_upload_media_success(client, mock_upload_service):
    files = [create_test_image_file()]
    headers = {"Authorization": "Bearer valid_token"}
    params = {"plan_id": "test_plan_123"}
    
    response = client.post("/cms/media/upload", files=files, headers=headers, params=params)
    
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["url"] == mock_success_response.url
    assert response_data["key"] == mock_success_response.key
    assert response_data["message"] == IMAGE_UPLOAD_SUCCESS


def test_upload_media_missing_authorization(client_no_auth):
    files = [create_test_image_file()]
    params = {"plan_id": "test_plan_123"}
    
    response = client_no_auth.post("/cms/media/upload", files=files, params=params)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_upload_media_invalid_token(client, mock_validate_author):
    mock_validate_author.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=AUTHOR_NOT_FOUND
    )
    
    files = [create_test_image_file()]
    headers = {"Authorization": "Bearer invalid_token"}
    params = {"plan_id": "test_plan_123"}
    
    response = client.post("/cms/media/upload", files=files, headers=headers, params=params)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == AUTHOR_NOT_FOUND


def test_upload_media_missing_file(client, mock_upload_service):
    headers = {"Authorization": "Bearer valid_token"}
    
    response = client.post("/cms/media/upload", headers=headers)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_data = response.json()
    assert "field required" in str(response_data["detail"]).lower()


def test_upload_media_invalid_file_format(client):
    with patch("pecha_api.plans.image_upload.media_services.validate_file") as mock_validate_file:
        mock_validate_file.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_FILE_FORMAT
        )
    
        files = [create_test_image_file(filename="test.txt", content_type="text/plain")]
        headers = {"Authorization": "Bearer valid_token"}
        params = {"plan_id": "test_plan_123"}

        response = client.post("/cms/media/upload", files=files, headers=headers, params=params)
    
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == INVALID_FILE_FORMAT


def test_upload_media_file_too_large(client):
    with patch("pecha_api.plans.image_upload.media_services.validate_file") as mock_validate_file:
        mock_validate_file.side_effect = HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=FILE_TOO_LARGE
        )
        
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB content
        files = [create_test_image_file(content=large_content)]
        headers = {"Authorization": "Bearer valid_token"}
        params = {"plan_id": "test_plan_123"}

        response = client.post("/cms/media/upload", files=files, headers=headers, params=params)
        
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert response.json()["detail"] == FILE_TOO_LARGE


def test_upload_media_server_error(client):
    with patch("pecha_api.plans.image_upload.media_views.upload_media_file") as mock_upload:
        mock_upload.side_effect = HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR_UPLOAD
        )
        
        files = [create_test_image_file()]
        headers = {"Authorization": "Bearer valid_token"}
        params = {"plan_id": "test_plan_123"}

        response = client.post("/cms/media/upload", files=files, headers=headers, params=params)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == UNEXPECTED_ERROR_UPLOAD


def test_upload_media_different_image_formats(client):
    mock_response = MediaUploadResponse(
        url="https://s3.amazonaws.com/bucket/images/plan_images/uuid/test_image.png",
        key="images/plan_images/uuid/test_image.png",
        path="images/plan_images/uuid",
        message=IMAGE_UPLOAD_SUCCESS
    )
    
    image_formats = [
        ("test.jpg", "image/jpeg"),
        ("test.png", "image/png"),
        ("test.webp", "image/webp")
    ]
    
    with patch("pecha_api.plans.image_upload.media_views.upload_media_file", return_value=mock_response) as mock_upload:
        for filename, content_type in image_formats:
            files = [create_test_image_file(filename=filename, content_type=content_type)]
            headers = {"Authorization": "Bearer valid_token"}
            params = {"plan_id": "test_plan_123"}

            response = client.post("/cms/media/upload", files=files, headers=headers, params=params)
            
            assert response.status_code == status.HTTP_201_CREATED
            response_data = response.json()
            assert response_data["url"] == mock_response.url
            assert response_data["key"] == mock_response.key
            assert response_data["path"] == mock_response.path
            assert response_data["message"] == IMAGE_UPLOAD_SUCCESS


def test_upload_media_empty_file(client):
    files = [create_test_image_file(content=b"")]
    headers = {"Authorization": "Bearer valid_token"}
    params = {"plan_id": "test_plan_123"}

    with patch("pecha_api.plans.image_upload.media_views.upload_media_file", return_value=mock_success_response):
        response = client.post("/cms/media/upload", files=files, headers=headers, params=params)
        
        assert response.status_code == status.HTTP_201_CREATED


def test_upload_media_malformed_bearer_token(client_no_auth):
    files = [create_test_image_file()]
    headers = {"Authorization": "InvalidFormat token"}
    params = {"plan_id": "test_plan_123"}
    
    response = client_no_auth.post("/cms/media/upload", files=files, headers=headers, params=params)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_upload_media_filename_with_special_characters(client):
    with patch("pecha_api.plans.image_upload.media_views.upload_media_file", return_value=mock_success_response):
        files = [create_test_image_file(filename="test image with spaces & symbols!@#.jpg")]
        headers = {"Authorization": "Bearer valid_token"}
        params = {"plan_id": "test_plan_123"}

        response = client.post("/cms/media/upload", files=files, headers=headers, params=params)
        
        assert response.status_code == status.HTTP_201_CREATED


def test_upload_media_no_filename(client):
    files = [("file", (None, b"fake_image_content", "image/jpeg"))]
    headers = {"Authorization": "Bearer valid_token"}
    params = {"plan_id": "test_plan_123"}
    
    response = client.post("/cms/media/upload", files=files, headers=headers, params=params)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_media_response_structure(client):
    mock_response = MediaUploadResponse(
        url="https://s3.amazonaws.com/bucket/images/plan_images/uuid/test_image.jpg",
        key="images/plan_images/uuid/test_image.jpg",
        path="images/plan_images/uuid",
        message=IMAGE_UPLOAD_SUCCESS
    )
    
    with patch("pecha_api.plans.image_upload.media_views.upload_media_file", return_value=mock_response):
        files = [create_test_image_file()]
        headers = {"Authorization": "Bearer valid_token"}
        params = {"plan_id": "test_plan_123"}

        response = client.post("/cms/media/upload", files=files, headers=headers, params=params)
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        
        assert "url" in response_data
        assert "key" in response_data
        assert "message" in response_data
        
        assert response_data["url"].startswith("https://")
        assert "s3.amazonaws.com" in response_data["url"]
        
        assert "images" in response_data["key"]
        
        assert response_data["message"] == IMAGE_UPLOAD_SUCCESS
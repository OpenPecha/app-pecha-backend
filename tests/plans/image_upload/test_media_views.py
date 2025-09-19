import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import UploadFile, HTTPException
from starlette import status

from pecha_api.app import api
from pecha_api.plans.media.media_response_models import PlanUploadResponse
from pecha_api.plans.response_message import (
    IMAGE_UPLOAD_SUCCESS,
    INVALID_FILE_FORMAT,
    FILE_TOO_LARGE,
    UNEXPECTED_ERROR_UPLOAD,
    AUTHOR_NOT_FOUND
)
from pecha_api.plans.authors.plan_author_model import Author


# Test Data Constants
TEST_PLAN_ID = "test_plan_123"
VALID_TOKEN = "valid_token"
INVALID_TOKEN = "invalid_token"
TEST_BUCKET_URL = "https://s3.amazonaws.com/bucket"


class TestDataFactory:
    """Factory class for creating test data objects"""
    
    @staticmethod
    def create_mock_author(
        author_id: int = 1,
        first_name: str = "Test",
        last_name: str = "Author",
        email: str = "test@example.com",
        image_url: str = "https://example.com/image.jpg"
    ) -> Author:
        return Author(
            id=author_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            image_url=image_url
        )
    
    @staticmethod
    def create_mock_upload_response(
        filename: str = "test_image.jpg",
        plan_id: str = TEST_PLAN_ID,
        message: str = IMAGE_UPLOAD_SUCCESS
    ) -> PlanUploadResponse:
        uuid_part = "uuid"  # Simplified for testing
        return PlanUploadResponse(
            url=f"{TEST_BUCKET_URL}/images/plan_images/{plan_id}/{uuid_part}/{filename}",
            key=f"images/plan_images/{plan_id}/{uuid_part}/{filename}",
            path=f"images/plan_images/{plan_id}/{uuid_part}",
            message=message
        )
    
    @staticmethod
    def create_test_file(
        filename: str = "test_image.jpg",
        content: bytes = b"fake_image_content",
        content_type: str = "image/jpeg"
    ) -> tuple:
        return ("file", (filename, content, content_type))


# Fixtures
@pytest.fixture
def mock_author():
    """Provides a mock author object"""
    return TestDataFactory.create_mock_author()


@pytest.fixture
def mock_success_response():
    """Provides a mock successful upload response"""
    return TestDataFactory.create_mock_upload_response()


@pytest.fixture(autouse=True)
def mock_validate_author(mock_author):
    """Auto-used fixture to mock author validation"""
    with patch("pecha_api.plans.media.media_services.validate_and_extract_author_details") as mock_func:
        mock_func.return_value = mock_author
        yield mock_func


@pytest.fixture
def mock_upload_service(mock_success_response):
    """Mock the upload service with success response"""
    with patch("pecha_api.plans.media.media_views.upload_plan_image") as mock_func:
        mock_func.return_value = mock_success_response
        yield mock_func


@pytest.fixture
def authenticated_client():
    """Test client with authentication override"""
    from pecha_api.plans.media.media_views import oauth2_scheme
    
    original_dependency = api.dependency_overrides.copy()
    
    def get_token_override():
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=VALID_TOKEN)
    
    api.dependency_overrides[oauth2_scheme] = get_token_override
    test_client = TestClient(api)
    
    yield test_client
    
    api.dependency_overrides = original_dependency


@pytest.fixture
def unauthenticated_client():
    """Test client without authentication"""
    original_dependency = api.dependency_overrides.copy()
    test_client = TestClient(api)
    
    yield test_client
    
    api.dependency_overrides = original_dependency


# Test Classes for Better Organization
class TestMediaUploadSuccess:
    """Test cases for successful media upload scenarios"""
    
    def test_upload_image_success(self, authenticated_client, mock_upload_service):
        """Test successful image upload with valid data"""
        files = [TestDataFactory.create_test_file()]
        headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
        params = {"plan_id": TEST_PLAN_ID}
        
        response = authenticated_client.post("/cms/media/upload", files=files, headers=headers, params=params)
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["message"] == IMAGE_UPLOAD_SUCCESS
        assert "url" in response_data
        assert "key" in response_data
        assert "path" in response_data
    
    def test_upload_different_image_formats(self, authenticated_client, mock_success_response):
        """Test upload with different supported image formats"""
        image_formats = [
            ("test.jpg", "image/jpeg"),
            ("test.png", "image/png"),
            ("test.webp", "image/webp"),
            ("test.gif", "image/gif")
        ]
        
        with patch("pecha_api.plans.media.media_views.upload_plan_image", return_value=mock_success_response):
            for filename, content_type in image_formats:
                files = [TestDataFactory.create_test_file(filename=filename, content_type=content_type)]
                headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
                params = {"plan_id": TEST_PLAN_ID}

                response = authenticated_client.post("/cms/media/upload", files=files, headers=headers, params=params)
                
                assert response.status_code == status.HTTP_201_CREATED, f"Failed for format: {content_type}"
    
    def test_upload_without_plan_id(self, authenticated_client, mock_upload_service):
        """Test upload without plan_id parameter"""
        files = [TestDataFactory.create_test_file()]
        headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
        
        response = authenticated_client.post("/cms/media/upload", files=files, headers=headers)
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_upload_with_special_characters_in_filename(self, authenticated_client, mock_upload_service):
        """Test upload with special characters in filename"""
        files = [TestDataFactory.create_test_file(filename="test image with spaces & symbols!@#.jpg")]
        headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
        params = {"plan_id": TEST_PLAN_ID}

        response = authenticated_client.post("/cms/media/upload", files=files, headers=headers, params=params)
        
        assert response.status_code == status.HTTP_201_CREATED


class TestMediaUploadAuthentication:
    """Test cases for authentication-related scenarios"""
    
    def test_upload_without_authorization_header(self, unauthenticated_client):
        """Test upload request without Authorization header"""
        files = [TestDataFactory.create_test_file()]
        params = {"plan_id": TEST_PLAN_ID}
        
        response = unauthenticated_client.post("/cms/media/upload", files=files, params=params)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_upload_with_invalid_token(self, authenticated_client, mock_validate_author):
        """Test upload with invalid authentication token"""
        mock_validate_author.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=AUTHOR_NOT_FOUND
        )
        
        files = [TestDataFactory.create_test_file()]
        headers = {"Authorization": f"Bearer {INVALID_TOKEN}"}
        params = {"plan_id": TEST_PLAN_ID}
        
        response = authenticated_client.post("/cms/media/upload", files=files, headers=headers, params=params)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == AUTHOR_NOT_FOUND
    
    def test_upload_with_malformed_bearer_token(self, unauthenticated_client):
        """Test upload with malformed Authorization header"""
        files = [TestDataFactory.create_test_file()]
        headers = {"Authorization": "InvalidFormat token"}
        params = {"plan_id": TEST_PLAN_ID}
        
        response = unauthenticated_client.post("/cms/media/upload", files=files, headers=headers, params=params)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestMediaUploadValidation:
    """Test cases for file validation scenarios"""
    
    def test_upload_missing_file(self, authenticated_client):
        """Test upload request without file"""
        headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
        params = {"plan_id": TEST_PLAN_ID}
        
        response = authenticated_client.post("/cms/media/upload", headers=headers, params=params)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        response_data = response.json()
        assert "field required" in str(response_data["detail"]).lower()
    
    def test_upload_file_without_filename(self, authenticated_client):
        """Test upload with file that has no filename"""
        files = [("file", (None, b"fake_image_content", "image/jpeg"))]
        headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
        params = {"plan_id": TEST_PLAN_ID}
        
        response = authenticated_client.post("/cms/media/upload", files=files, headers=headers, params=params)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_upload_invalid_file_format(self, authenticated_client):
        """Test upload with invalid file format"""
        with patch("pecha_api.plans.media.media_services.validate_file") as mock_validate_file:
            mock_validate_file.side_effect = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID_FILE_FORMAT
            )
        
            files = [TestDataFactory.create_test_file(filename="test.txt", content_type="text/plain")]
            headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
            params = {"plan_id": TEST_PLAN_ID}

            response = authenticated_client.post("/cms/media/upload", files=files, headers=headers, params=params)
        
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["detail"] == INVALID_FILE_FORMAT
    
    def test_upload_file_too_large(self, authenticated_client):
        """Test upload with file exceeding size limit"""
        with patch("pecha_api.plans.media.media_services.validate_file") as mock_validate_file:
            mock_validate_file.side_effect = HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=FILE_TOO_LARGE
            )
            
            large_content = b"x" * (6 * 1024 * 1024)  # 6MB content
            files = [TestDataFactory.create_test_file(content=large_content)]
            headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
            params = {"plan_id": TEST_PLAN_ID}

            response = authenticated_client.post("/cms/media/upload", files=files, headers=headers, params=params)
            
            assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            assert response.json()["detail"] == FILE_TOO_LARGE
    
    def test_upload_empty_file(self, authenticated_client, mock_upload_service):
        """Test upload with empty file content"""
        files = [TestDataFactory.create_test_file(content=b"")]
        headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
        params = {"plan_id": TEST_PLAN_ID}

        response = authenticated_client.post("/cms/media/upload", files=files, headers=headers, params=params)
        
        # Empty files should still be processed successfully if they pass validation
        assert response.status_code == status.HTTP_201_CREATED


class TestMediaUploadErrorHandling:
    """Test cases for error handling scenarios"""
    
    def test_upload_server_error(self, authenticated_client):
        """Test upload when server encounters internal error"""
        with patch("pecha_api.plans.media.media_views.upload_plan_image") as mock_upload:
            mock_upload.side_effect = HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=UNEXPECTED_ERROR_UPLOAD
            )
            
            files = [TestDataFactory.create_test_file()]
            headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
            params = {"plan_id": TEST_PLAN_ID}

            response = authenticated_client.post("/cms/media/upload", files=files, headers=headers, params=params)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == UNEXPECTED_ERROR_UPLOAD
    
    def test_upload_service_unavailable(self, authenticated_client):
        """Test upload when upload service is unavailable"""
        with patch("pecha_api.plans.media.media_views.upload_plan_image") as mock_upload:
            mock_upload.side_effect = HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Upload service temporarily unavailable"
            )
            
            files = [TestDataFactory.create_test_file()]
            headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
            params = {"plan_id": TEST_PLAN_ID}

            response = authenticated_client.post("/cms/media/upload", files=files, headers=headers, params=params)
            
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


class TestMediaUploadResponseStructure:
    """Test cases for response structure validation"""
    
    def test_successful_upload_response_structure(self, authenticated_client, mock_success_response):
        """Test that successful upload returns correct response structure"""
        with patch("pecha_api.plans.media.media_views.upload_plan_image", return_value=mock_success_response):
            files = [TestDataFactory.create_test_file()]
            headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
            params = {"plan_id": TEST_PLAN_ID}

            response = authenticated_client.post("/cms/media/upload", files=files, headers=headers, params=params)
            
            assert response.status_code == status.HTTP_201_CREATED
            response_data = response.json()
            
            # Verify all required fields are present
            required_fields = ["url", "key", "path", "message"]
            for field in required_fields:
                assert field in response_data, f"Missing required field: {field}"
            
            # Verify field formats
            assert response_data["url"].startswith("https://"), "URL should use HTTPS"
            assert TEST_BUCKET_URL in response_data["url"], "URL should contain bucket name"
            assert "images" in response_data["key"], "Key should contain images path"
            assert response_data["message"] == IMAGE_UPLOAD_SUCCESS
    
    def test_response_url_format(self, authenticated_client, mock_success_response):
        """Test that response URL follows expected format"""
        with patch("pecha_api.plans.media.media_views.upload_plan_image", return_value=mock_success_response):
            files = [TestDataFactory.create_test_file(filename="test-image.jpg")]
            headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
            params = {"plan_id": TEST_PLAN_ID}

            response = authenticated_client.post("/cms/media/upload", files=files, headers=headers, params=params)
            
            response_data = response.json()
            url = response_data["url"]
            
            # Verify URL structure
            assert url.startswith("https://"), "URL should use HTTPS protocol"
            assert "s3.amazonaws.com" in url, "URL should contain S3 domain"
            assert "images/plan_images" in url, "URL should contain correct path structure"
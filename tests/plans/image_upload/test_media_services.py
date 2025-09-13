import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi import UploadFile, HTTPException
from starlette import status

from pecha_api.plans.image_upload.media_response_models import MediaUploadResponse

IMAGE_UPLOAD_SUCCESS = "Image uploaded successfully"
INVALID_FILE_FORMAT = "Invalid file format. Only JPEG, PNG, and WebP images are allowed. Maximum size: 5MB"
FILE_TOO_LARGE = "File size exceeds 5MB limit"
UNEXPECTED_ERROR_UPLOAD = "An unexpected error occurred during upload"
AUTHOR_NOT_FOUND = "Author not found"

IMAGE_UTILS_PATH = "pecha_api.plans.image_upload.media_services.ImageUtils"
UPLOAD_BYTES_PATH = "pecha_api.plans.image_upload.media_services.upload_bytes"
GENERATE_URL_PATH = "pecha_api.plans.image_upload.media_services.generate_presigned_access_url"
VALIDATE_AUTHOR_PATH = "pecha_api.plans.image_upload.media_services.validate_and_extract_author_details"
UUID_PATH = "pecha_api.plans.image_upload.media_services.uuid.uuid4"
GET_CONFIG_PATH = "pecha_api.plans.image_upload.media_services.get"
GET_INT_CONFIG_PATH = "pecha_api.plans.image_upload.media_services.get_int"

class Author:
    def __init__(self, id, first_name, last_name, email, image_url):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.image_url = image_url

@pytest.fixture
def mock_upload_file():
    file = MagicMock(spec=UploadFile)
    file.filename = "test_image.jpg"
    file.content_type = "image/jpeg"
    file.size = 1024 * 1024  # 1MB
    file.file = io.BytesIO(b"fake image content")
    return file

@pytest.fixture
def mock_author():
    return Author(
        id=1,
        first_name="Test",
        last_name="Author",
        email="test@example.com",
        image_url="https://example.com/image.jpg"
    )

# Configuration values for tests
TEST_CONFIG = {
    "ALLOWED_EXTENSIONS": [".jpg", ".jpeg", ".png", ".webp"],
    "AWS_BUCKET_NAME": "test-bucket",
    "MAX_FILE_SIZE": 5 * 1024 * 1024  # 5MB
}

def create_mock_patches():
    patches = {}
    
    patches['get_config'] = patch(GET_CONFIG_PATH)
    patches['get_int_config'] = patch(GET_INT_CONFIG_PATH)
    
    patches['image_utils'] = patch(IMAGE_UTILS_PATH)
    patches['upload_bytes'] = patch(UPLOAD_BYTES_PATH)
    patches['presigned_url'] = patch(GENERATE_URL_PATH)
    patches['validate_author'] = patch(VALIDATE_AUTHOR_PATH)
    patches['uuid'] = patch(UUID_PATH)
    
    return patches

def setup_successful_mocks(patches):
    mocks = {}
    
    for name, patch_obj in patches.items():
        mocks[name] = patch_obj.start()
    
    mocks['get_config'].side_effect = lambda key: TEST_CONFIG.get(key)
    mocks['get_int_config'].side_effect = lambda key: TEST_CONFIG.get(key)
    
    mocks['image_utils'].return_value.validate_and_compress_image.return_value = io.BytesIO(b"compressed_image_content")
    
    mocks['upload_bytes'].return_value = "images/plan_images/uuid123/test_image.jpg"
    
    mocks['presigned_url'].return_value = "https://s3.amazonaws.com/test-bucket/images/plan_images/uuid123/test_image.jpg"
    
    mocks['validate_author'].return_value = Author(
        id=1,
        first_name="Test",
        last_name="Author",
        email="test@example.com",
        image_url="https://example.com/image.jpg"
    )
    
    mocks['uuid'].return_value = "uuid123"
    
    return mocks

def cleanup_patches(patches):
    for patch_obj in patches.values():
        patch_obj.stop()


class TestValidateFile:
    def test_valid_file(self, mock_upload_file):
        with patch(GET_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)), \
             patch(GET_INT_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)):
            from pecha_api.plans.image_upload.media_services import validate_file
            validate_file(mock_upload_file)  # Should not raise exception

    def test_invalid_extension(self, mock_upload_file):
        mock_upload_file.filename = "test_document.pdf"
        
        with patch(GET_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)), \
             patch(GET_INT_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)):
            from pecha_api.plans.image_upload.media_services import validate_file
            with pytest.raises(HTTPException) as exc_info:
                validate_file(mock_upload_file)
                
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == INVALID_FILE_FORMAT

    def test_file_too_large(self, mock_upload_file):
        mock_upload_file.size = 6 * 1024 * 1024  
        
        with patch(GET_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)), \
             patch(GET_INT_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)):
            from pecha_api.plans.image_upload.media_services import validate_file
            with pytest.raises(HTTPException) as exc_info:
                validate_file(mock_upload_file)
                
            assert exc_info.value.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            assert exc_info.value.detail == FILE_TOO_LARGE

    def test_no_filename(self, mock_upload_file):
        mock_upload_file.filename = None
        
        with patch(GET_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)), \
             patch(GET_INT_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)):
            from pecha_api.plans.image_upload.media_services import validate_file
            with pytest.raises(HTTPException) as exc_info:
                validate_file(mock_upload_file)
                
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == INVALID_FILE_FORMAT

    @pytest.mark.parametrize("extension", [".jpg", ".jpeg", ".png", ".webp"])
    def test_different_image_formats(self, mock_upload_file, extension):
        mock_upload_file.filename = f"test_image{extension}"
        
        with patch(GET_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)), \
             patch(GET_INT_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)):
            from pecha_api.plans.image_upload.media_services import validate_file
            validate_file(mock_upload_file) 

    def test_case_insensitive_extension(self, mock_upload_file):
        mock_upload_file.filename = "test_image.JPG"  
        
        with patch(GET_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)), \
             patch(GET_INT_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)):
            from pecha_api.plans.image_upload.media_services import validate_file
            validate_file(mock_upload_file) 
        
    def test_integer_comparison_for_file_size(self, mock_upload_file):
        mock_upload_file.size = 5 * 1024 * 1024  
        
        with patch(GET_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)) as mock_get_config, \
             patch(GET_INT_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)) as mock_get_int_config:
            from pecha_api.plans.image_upload.media_services import validate_file
            validate_file(mock_upload_file)  # Should not raise exception
            
            mock_get_int_config.assert_called_with("MAX_FILE_SIZE")


class TestUploadMediaFile:
    
    def _assert_successful_upload_response(self, result, expected_path_fragment):
        assert isinstance(result, MediaUploadResponse)
        assert result.url == "https://s3.amazonaws.com/test-bucket/images/plan_images/uuid123/test_image.jpg"
        assert expected_path_fragment in result.path
        assert result.message == IMAGE_UPLOAD_SUCCESS
    
    def _assert_upload_dependencies_called(self, mocks):
        mocks['validate_author'].assert_called_once_with(token="valid_token")
        mocks['image_utils'].return_value.validate_and_compress_image.assert_called_once()
        mocks['upload_bytes'].assert_called_once()
        mocks['presigned_url'].assert_called_once()
    
    def test_successful_upload(self, mock_upload_file):
        patches = create_mock_patches()
        mocks = setup_successful_mocks(patches)
        
        try:
            from pecha_api.plans.image_upload.media_services import upload_media_file
            
            result = upload_media_file(
                token="valid_token",
                plan_id=None,
                file=mock_upload_file,
                path="images/plan_images"
            )
            
            self._assert_upload_dependencies_called(mocks)
            
            upload_args = mocks['upload_bytes'].call_args[1]
            assert upload_args.get("bucket_name") == "test-bucket"
            assert "images/plan_images/uuid123" in upload_args.get("s3_key")
            
            self._assert_successful_upload_response(result, "images/plan_images/uuid123")
            
        finally:
            cleanup_patches(patches)

    def test_upload_with_plan_id(self, mock_upload_file):
        patches = create_mock_patches()
        mocks = setup_successful_mocks(patches)
        
        try:
            from pecha_api.plans.image_upload.media_services import upload_media_file
            
            plan_id = "plan123"
            
            result = upload_media_file(
                token="valid_token",
                plan_id=plan_id,
                file=mock_upload_file,
                path="images/plan_images"
            )
            
            upload_args = mocks['upload_bytes'].call_args[1]
            s3_key = upload_args.get("s3_key")
            assert f"images/plan_images/{plan_id}/uuid123" in s3_key
            assert plan_id in result.path
            
        finally:
            cleanup_patches(patches)

    def test_custom_path(self, mock_upload_file):
        patches = create_mock_patches()
        mocks = setup_successful_mocks(patches)
        
        try:
            from pecha_api.plans.image_upload.media_services import upload_media_file
            
            custom_path = "images/custom_folder"
            result = upload_media_file(
                token="valid_token",
                plan_id=None,
                file=mock_upload_file,
                path=custom_path
            )
            
            upload_args = mocks['upload_bytes'].call_args[1]
            s3_key = upload_args.get("s3_key")
            assert custom_path in s3_key
            assert custom_path in result.path
            
        finally:
            cleanup_patches(patches)

    def test_auth_failure(self, mock_upload_file):
        with patch(VALIDATE_AUTHOR_PATH) as mock_validate_author:
            mock_validate_author.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=AUTHOR_NOT_FOUND
            )
            
            from pecha_api.plans.image_upload.media_services import upload_media_file
            with pytest.raises(HTTPException) as exc_info:
                upload_media_file(
                    token="invalid_token",
                    plan_id=None,
                    file=mock_upload_file
                )
                
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert exc_info.value.detail == AUTHOR_NOT_FOUND

    def test_validation_failure(self, mock_upload_file):
        mock_upload_file.filename = "test_document.pdf" 
        
        with patch(GET_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)), \
             patch(GET_INT_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)), \
             patch(VALIDATE_AUTHOR_PATH):
            from pecha_api.plans.image_upload.media_services import upload_media_file
            with pytest.raises(HTTPException) as exc_info:
                upload_media_file(
                    token="valid_token",
                    plan_id=None,
                    file=mock_upload_file
                )
                
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == INVALID_FILE_FORMAT

    def test_image_compression_failure(self, mock_upload_file):
        with patch(GET_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)), \
             patch(GET_INT_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)), \
             patch(VALIDATE_AUTHOR_PATH), \
             patch(IMAGE_UTILS_PATH) as mock_class:
            mock_instance = mock_class.return_value
            mock_instance.validate_and_compress_image.side_effect = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process the image"
            )
            
            from pecha_api.plans.image_upload.media_services import upload_media_file
            with pytest.raises(HTTPException) as exc_info:
                upload_media_file(
                    token="valid_token",
                    plan_id=None,
                    file=mock_upload_file
                )
                
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == "Failed to process the image"
    
    def test_s3_upload_failure(self, mock_upload_file):
        with patch(GET_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)), \
             patch(GET_INT_CONFIG_PATH, side_effect=lambda key: TEST_CONFIG.get(key)), \
             patch(VALIDATE_AUTHOR_PATH), \
             patch(IMAGE_UTILS_PATH), \
             patch(UPLOAD_BYTES_PATH) as mock_upload:
            mock_upload.side_effect = Exception("S3 upload failed")
            
            from pecha_api.plans.image_upload.media_services import upload_media_file
            with pytest.raises(HTTPException) as exc_info:
                upload_media_file(
                    token="valid_token",
                    plan_id=None,
                    file=mock_upload_file
                )
                
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert exc_info.value.detail == UNEXPECTED_ERROR_UPLOAD

    @pytest.mark.parametrize("filename,description", [
        ("test image with spaces & symbols!@#.jpg", "special characters"),
        ("test_file_with_very_long_name_that_exceeds_normal_limits_but_should_still_work.jpg", "long filename")
    ])
    def test_edge_case_filenames(self, mock_upload_file, filename, description):
        patches = create_mock_patches()
        mocks = setup_successful_mocks(patches)
        
        try:
            mock_upload_file.filename = filename
            
            from pecha_api.plans.image_upload.media_services import upload_media_file
            result = upload_media_file(
                token="valid_token",
                plan_id=None,
                file=mock_upload_file
            )
            
            assert isinstance(result, MediaUploadResponse)
            assert result.message == IMAGE_UPLOAD_SUCCESS
            
        finally:
            cleanup_patches(patches)
        
    def test_empty_file_content(self, mock_upload_file):
        patches = create_mock_patches()
        mocks = setup_successful_mocks(patches)
        
        try:
            mock_upload_file.file = io.BytesIO(b"") 
            
            from pecha_api.plans.image_upload.media_services import upload_media_file
            result = upload_media_file(
                token="valid_token",
                plan_id=None,
                file=mock_upload_file
            )
            
            assert isinstance(result, MediaUploadResponse)
            assert result.message == IMAGE_UPLOAD_SUCCESS
            
        finally:
            cleanup_patches(patches)
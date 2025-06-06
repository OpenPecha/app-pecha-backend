import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi import UploadFile
from pecha_api.sheets.sheets_service import upload_sheet_image_request
from pecha_api.config import get

def test_upload_sheet_image_success():
    # Create a mock file
    file_content = io.BytesIO(b"fake_image_data")
    file = UploadFile(filename="test.jpg", file=file_content, content_type="image/jpeg")

    # Mock the necessary dependencies
    with patch("pecha_api.utils.Utils.validate_and_compress_image", return_value=file_content) as mock_validate, \
         patch("pecha_api.uploads.S3_utils.delete_file") as mock_delete_file, \
         patch("pecha_api.uploads.S3_utils.upload_bytes", return_value="s3_key") as mock_upload_bytes, \
         patch("pecha_api.uploads.S3_utils.generate_presigned_upload_url", return_value="https://app-pecha-backend.s3.amazonaws.com/images/sheet_images/WhatsApp%20Image%202025-06-03%20at%205.18.23%20PM%20%281%29..jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA5FCD6NLK3T7GINFJ%2F20250606%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20250606T043736Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=84890c179ae69f545a5b77821f5b5603ea8e73b25addc8340ddbd64a9db2339e") as mock_presigned_url:
        
        # Call the function
        response = upload_sheet_image_request(file=file)

        # Verify the response
        assert response == {"url": "https://app-pecha-backend.s3.amazonaws.com/images/sheet_images/WhatsApp%20Image%202025-06-03%20at%205.18.23%20PM%20%281%29..jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA5FCD6NLK3T7GINFJ%2F20250606%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20250606T043736Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=84890c179ae69f545a5b77821f5b5603ea8e73b25addc8340ddbd64a9db2339e"}

        # Verify that all the mocked functions were called with correct arguments
        mock_validate.assert_called_once_with(file=file, content_type="image/jpeg")
        mock_delete_file.assert_called_once_with(file_path="images/sheet_images/test.jpg")
        mock_upload_bytes.assert_called_once_with(
            bucket_name=get("AWS_BUCKET_NAME"),
            s3_key="images/sheet_images/test.jpg",
            file=file_content,
            content_type="image/jpeg"
        )
        mock_presigned_url.assert_called_once_with(
            bucket_name=get("AWS_BUCKET_NAME"),
            s3_key="s3_key"
        )

def test_upload_sheet_image_invalid_file():
    # Create a mock file with invalid content type
    file_content = io.BytesIO(b"fake_text_data")
    file = UploadFile(filename="test.txt", file=file_content, content_type="text/plain")

    # Mock the validate_and_compress_image to raise an exception for invalid file
    with patch("pecha_api.utils.Utils.validate_and_compress_image", side_effect=Exception("Only image files are allowed.")):
        with pytest.raises(Exception, match="Only image files are allowed."):
            upload_sheet_image_request(file=file)

import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi import UploadFile, HTTPException, status
from pecha_api.sheets.sheets_service import upload_sheet_image_request
from pecha_api.config import get
from pecha_api.error_contants import ErrorConstants
from pecha_api.sheets.sheets_response_models import SheetIdRequest
from pecha_api.image_utils import ImageUtils



def test_validate_and_compress_image_success():
    file_content = io.BytesIO(b"fake_image_data")
    file = UploadFile(filename="test.jpg", file=file_content)

    with patch("pecha_api.image_utils.get_int", side_effect=[5, 75]), \
            patch("PIL.Image.open") as mock_open:
        mock_image = MagicMock()
        mock_image.mode = 'RGB'  # Set the mode to RGB
        mock_open.return_value = mock_image
        mock_image.save = MagicMock()

        compressed_image = ImageUtils.validate_and_compress_image(file=file, content_type="image/jpeg")
        assert isinstance(compressed_image, io.BytesIO)
        mock_image.save.assert_called_once_with(compressed_image, format="JPEG", quality=75)


def test_validate_and_compress_image_invalid_file_type():
    file_content = io.BytesIO(b"fake_image_data")
    file = UploadFile(filename="test.txt", file=file_content)
    try:
        ImageUtils.validate_and_compress_image(file=file, content_type="text/plain")
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST
        assert e.detail == 'Only image files are allowed'


def test_validate_and_compress_image_file_too_large():
    file_content = io.BytesIO(b"fake_image_data" * 1024 * 1024 * 6)  # 6 MB
    file = UploadFile(filename="test.jpg", file=file_content)

    with patch("pecha_api.users.users_service.get_int", return_value=5), \
            pytest.raises(HTTPException) as exc_info:
        ImageUtils.validate_and_compress_image(file=file, content_type="image/jpeg")
    assert exc_info.value.status_code == 413
    assert exc_info.value.detail == "File size exceeds 5MB limit"


def test_validate_and_compress_image_processing_failure():
    file_content = io.BytesIO(b"fake_image_data")
    file = UploadFile(filename="test.jpg", file=file_content)

    with patch("pecha_api.users.users_service.get_int", side_effect=[5, 75]), \
            patch("pecha_api.users.users_service.Image.open", side_effect=Exception("Processing error")), \
            pytest.raises(HTTPException) as exc_info:
        ImageUtils.validate_and_compress_image(file=file, content_type="image/jpeg")
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Failed to process the image"
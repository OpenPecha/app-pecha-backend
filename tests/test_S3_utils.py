import pytest
from unittest.mock import patch, MagicMock
from fastapi import UploadFile
from io import BytesIO
from pecha_api.uploads.S3_utils import upload_file, upload_bytes, generate_presigned_upload_url, delete_file


@pytest.fixture
def mock_s3_client():
    with patch("pecha_api.uploads.S3_utils.s3_client") as mock:
        yield mock


@pytest.fixture
def upload_file_mock():
    file = MagicMock(spec=UploadFile)
    file.file = BytesIO(b"test data")
    file.content_type = "text/plain"
    return file


def test_upload_file_success(mock_s3_client, upload_file_mock):
    mock_s3_client.upload_fileobj.return_value = None
    result = upload_file("test-bucket", "test-key", upload_file_mock)
    assert result == "test-key"


def test_upload_file_client_error(mock_s3_client, upload_file_mock):
    mock_s3_client.upload_fileobj.side_effect = Exception("ClientError")
    with pytest.raises(Exception):
        upload_file("test-bucket", "test-key", upload_file_mock)


def test_upload_bytes_success(mock_s3_client):
    file = BytesIO(b"test data")
    result = upload_bytes("test-bucket", "test-key", file, "text/plain")
    assert result == "test-key"


def test_upload_bytes_invalid_file(mock_s3_client):
    with pytest.raises(Exception):
        upload_bytes("test-bucket", "test-key", "invalid file", "text/plain")


def test_generate_presigned_upload_url_success(mock_s3_client):
    mock_s3_client.generate_presigned_url.return_value = "http://example.com"
    result = generate_presigned_upload_url("test-bucket", "test-key", "text/plain")
    assert result == "http://example.com"


def test_generate_presigned_upload_url_client_error(mock_s3_client):
    mock_s3_client.generate_presigned_url.side_effect = Exception("ClientError")
    with pytest.raises(Exception):
        generate_presigned_upload_url("test-bucket", "test-key", "text/plain")


def test_delete_file_success(mock_s3_client):
    mock_s3_client.delete_object.return_value = None
    result = delete_file("test-key")
    assert result is True


def test_delete_file_client_error(mock_s3_client):
    mock_s3_client.delete_object.side_effect = mock_s3_client.exceptions.ClientError(
        {"Error": {"Code": "NoSuchKey"}}, "DeleteObject"
    )
    result = delete_file("test-key")
    assert result is True


def test_delete_file_unexpected_error(mock_s3_client):
    mock_s3_client.delete_object.side_effect = Exception("UnexpectedError")
    with pytest.raises(Exception):
        delete_file("test-key")

import io
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import UploadFile, HTTPException, status
from pecha_api.config import get
from pecha_api.error_contants import ErrorConstants
from pecha_api.sheets.sheets_response_models import SheetIdRequest
from pecha_api.image_utils import ImageUtils

from pecha_api.sheets.sheets_response_models import (
    CreateSheetRequest,
    Source,
    Content,
    Media
)
from pecha_api.texts.segments.segments_enum import SegmentType
from pecha_api.texts.texts_response_models import (
    TableOfContent,
    Section,
    TextSegment,
    UpdateTextRequest
)
from pecha_api.sheets.sheets_service import (
    create_new_sheet,
    update_sheet_by_id,
    get_sheets
)
from pecha_api.users.users_models import Users
from pecha_api.texts.segments.segments_response_models import (
    SegmentDTO, 
    SegmentResponse
)
from pecha_api.texts.texts_enums import TextType


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


@pytest.mark.asyncio
async def test_create_new_sheet_success():
    mock_source = [
        Source(
            position=1,
            type=SegmentType.SOURCE,
            content="source_segment_id"
        ),
        Content(
            position=2,
            type=SegmentType.CONTENT,
            content="content"
        ),
        Media(
            position=3,
            type=SegmentType.IMAGE,
            content="media_url"
        )
    ]
    mock_create_sheet_request = CreateSheetRequest(
        title="sheet_title",
        source=mock_source
    )
    mock_token = "valid_token"
    mock_user_details = type("User",(), {
        "username": "test_user",
    })
    mock_group_response = type("GroupDTO", (), {
        "id": "group_id",
        "type": "sheet"
    })
    mock_text_response = type("TextDTO", (), {
        "id": "text_id",
        "title": "sheet_title",
        "group_id": "group_id",
        "type": "sheet",
        "is_published": True,
        "created_date": "2021-01-01",
        "updated_date": "2021-01-01",
        "published_date": "2021-01-01",
        "published_by": "test_user"
    })
    mock_segment_response = SegmentResponse(
        segments=[
            SegmentDTO(
                id="segment_id_2",
                text_id="text_id",
                content="content",
                type=SegmentType.CONTENT
            ),
            SegmentDTO(
                id="segment_id_3",
                text_id="text_id",
                content="media_url",
                type=SegmentType.IMAGE
            )
        ]
    )
    mock_table_of_content_response = TableOfContent(
        id="table_of_content_id",
        text_id="text_id",
        sections=[
            Section(
                id="section_id",
                section_number=1,
                segments=[
                    TextSegment(
                        segment_id="segment_id_1",
                        segment_number=1
                    ),
                    TextSegment(
                        segment_id="segment_id_2",
                        segment_number=2
                    ),
                    TextSegment(
                        segment_id="segment_id_3",
                        segment_number=3
                    )
                ]
            )
        ]
    )
    with patch("pecha_api.sheets.sheets_service.create_new_group", new_callable=AsyncMock, return_value=mock_group_response), \
        patch("pecha_api.sheets.sheets_service.create_new_text", new_callable=AsyncMock, return_value=mock_text_response), \
        patch("pecha_api.sheets.sheets_service.validate_and_extract_user_details", return_value=mock_user_details), \
        patch("pecha_api.sheets.sheets_service.create_new_segment", new_callable=AsyncMock, return_value=mock_segment_response), \
        patch("pecha_api.sheets.sheets_service.create_table_of_content", new_callable=AsyncMock, return_value=mock_table_of_content_response):

        response = await create_new_sheet(
            create_sheet_request=mock_create_sheet_request,
            token=mock_token
        )

        assert response is not None
        assert response["sheet_id"] == "text_id"

@pytest.mark.asyncio
async def test_create_sheet_invalid_token():
    mock_create_sheet_request = CreateSheetRequest(
        title="sheet_title",
        source=[]
    )
    with pytest.raises(HTTPException) as exc_info:
        await create_new_sheet(
            create_sheet_request=mock_create_sheet_request,
            token="invalid_token"
        )
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

@pytest.mark.asyncio
async def test_update_sheet_success():
    mock_source = [
        Source(
            position=1,
            type=SegmentType.SOURCE,
            content="source_segment_id"
        ),
        Content(
            position=2,
            type=SegmentType.CONTENT,
            content="content"
        ),
        Media(
            position=3,
            type=SegmentType.IMAGE,
            content="media_url"
        )
    ]
    mock_segment_response = SegmentResponse(
        segments=[
            SegmentDTO(
                id="segment_id_2",
                text_id="text_id",
                content="content",
                type=SegmentType.CONTENT
            ),
            SegmentDTO(
                id="segment_id_3",
                text_id="text_id",
                content="media_url",
                type=SegmentType.IMAGE
            )
        ]
    )
    mock_update_sheet_request = CreateSheetRequest(
        title="updated_sheet_title",
        source=mock_source,
        is_published=True
    )
    with patch("pecha_api.sheets.sheets_service.remove_segments_by_text_id", new_callable=AsyncMock), \
        patch("pecha_api.sheets.sheets_service.validate_user_exists", return_value=True), \
        patch("pecha_api.sheets.sheets_service.remove_table_of_content_by_text_id", new_callable=AsyncMock), \
        patch("pecha_api.sheets.sheets_service.update_text_details", new_callable=AsyncMock), \
        patch("pecha_api.sheets.sheets_service.create_new_segment", new_callable=AsyncMock, return_value=mock_segment_response), \
        patch("pecha_api.sheets.sheets_service.create_table_of_content", new_callable=AsyncMock):

        response = await update_sheet_by_id(
            sheet_id="text_id",
            update_sheet_request=mock_update_sheet_request,
            token="valid_token"
        )

        assert response is not None
        assert response["sheet_id"] == "text_id"

@pytest.mark.asyncio
async def test_update_sheet_invalid_token():
    mock_update_sheet_request = CreateSheetRequest(
        title="updated_sheet_title",
        source=[]
    )
    with pytest.raises(HTTPException) as exc_info:
        await update_sheet_by_id(
            sheet_id="text_id",
            update_sheet_request=mock_update_sheet_request,
            token="invalid_token"
        )
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

@pytest.mark.asyncio
async def test_get_sheets_with_default_parameters():
    #Test get_sheets function with default parameters
    mock_sheets = [
        type("TextDTO", (), {
            "id": "sheet_id_1",
            "title": "Sheet 1",
            "language": "en",
            "group_id": "group_id_1",
            "type": "sheet",
            "is_published": True,
            "created_date": "2024-01-01T00:00:00Z",
            "updated_date": "2024-01-01T00:00:00Z",
            "published_date": "2024-01-01T00:00:00Z",
            "published_by": "test_user",
            "categories": [],
            "views": 0
        })(),
        type("TextDTO", (), {
            "id": "sheet_id_2",
            "title": "Sheet 2",
            "language": "bo",
            "group_id": "group_id_2",
            "type": "sheet",
            "is_published": True,
            "created_date": "2024-01-02T00:00:00Z",
            "updated_date": "2024-01-02T00:00:00Z",
            "published_date": "2024-01-02T00:00:00Z",
            "published_by": "test_user",
            "categories": [],
            "views": 0
        })()
    ]
    
    with patch("pecha_api.sheets.sheets_service.get_texts_by_text_type", new_callable=AsyncMock, return_value=mock_sheets) as mock_get_texts:
        result = await get_sheets()
        
        # Verify the function was called with correct default parameters
        mock_get_texts.assert_called_once_with(
            is_published=True,
            text_type=TextType.SHEET.value,
            skip=0,
            limit=10
        )
        
        # Verify the result
        assert result == mock_sheets
        assert len(result) == 2
        assert result[0].id == "sheet_id_1"
        assert result[1].id == "sheet_id_2"

@pytest.mark.asyncio
async def test_get_sheets_with_custom_parameters():
    #Test get_sheets function with custom parameters
    mock_sheets = [
        type("TextDTO", (), {
            "id": "sheet_id_3",
            "title": "Unpublished Sheet",
            "language": "en",
            "group_id": "group_id_3",
            "type": "sheet",
            "is_published": False,
            "created_date": "2024-01-03T00:00:00Z",
            "updated_date": "2024-01-03T00:00:00Z",
            "published_date": "",
            "published_by": "test_user",
            "categories": [],
            "views": 0
        })()
    ]
    
    with patch("pecha_api.sheets.sheets_service.get_texts_by_text_type", new_callable=AsyncMock, return_value=mock_sheets) as mock_get_texts:
        result = await get_sheets(is_published=True, skip=5, limit=20)
        
        # Verify the function was called with correct custom parameters
        mock_get_texts.assert_called_once_with(
            is_published=True,
            text_type=TextType.SHEET.value,
            skip=5,
            limit=20
        )
        
        # Verify the result
        assert result == mock_sheets
        assert len(result) == 1
        assert result[0].is_published == False

@pytest.mark.asyncio
async def test_get_sheets_with_none_published_parameter():
    #Test get_sheets function with False as is_published parameter
    mock_sheets = []
    
    with patch("pecha_api.sheets.sheets_service.get_texts_by_text_type", new_callable=AsyncMock, return_value=mock_sheets) as mock_get_texts:
        result = await get_sheets(is_published=False, skip=0, limit=5)
        
        # Verify the function was called with None for is_published
        mock_get_texts.assert_called_once_with(
            is_published=False,
            text_type=TextType.SHEET.value,
            skip=0,
            limit=5
        )
        
        # Verify the result
        assert result == mock_sheets
        assert len(result) == 0

@pytest.mark.asyncio
async def test_get_sheets_empty_result():
    #Test get_sheets function when no sheets are found
    mock_sheets = []
    
    with patch("pecha_api.sheets.sheets_service.get_texts_by_text_type", new_callable=AsyncMock, return_value=mock_sheets) as mock_get_texts:
        result = await get_sheets()
        
        # Verify the function was called with default parameters
        mock_get_texts.assert_called_once_with(
            is_published=True,
            text_type=TextType.SHEET.value,
            skip=0,
            limit=10
        )
        
        # Verify the result is empty
        assert result == []
        assert len(result) == 0

@pytest.mark.asyncio
async def test_get_sheets_large_dataset():
    #Test get_sheets function with a large dataset
    # Create a list of 15 mock sheets
    mock_sheets = [
        type("TextDTO", (), {
            "id": f"sheet_id_{i}",
            "title": f"Sheet {i}",
            "language": "en",
            "group_id": f"group_id_{i}",
            "type": "sheet",
            "is_published": True,
            "created_date": f"2024-01-{i:02d}T00:00:00Z",
            "updated_date": f"2024-01-{i:02d}T00:00:00Z",
            "published_date": f"2024-01-{i:02d}T00:00:00Z",
            "published_by": "test_user",
            "categories": [],
            "views": i
        })()
        for i in range(1, 16)
    ]
    
    with patch("pecha_api.sheets.sheets_service.get_texts_by_text_type", new_callable=AsyncMock, return_value=mock_sheets) as mock_get_texts:
        result = await get_sheets(skip=10, limit=15)
        
        # Verify the function was called with pagination parameters
        mock_get_texts.assert_called_once_with(
            is_published=True,
            text_type=TextType.SHEET.value,
            skip=10,
            limit=15
        )
        
        # Verify the result
        assert result == mock_sheets
        assert len(result) == 15
        assert result[0].id == "sheet_id_1"
        assert result[-1].id == "sheet_id_15"

@pytest.mark.asyncio
async def test_get_sheets_passes_correct_text_type():
    #Test that get_sheets always passes the correct TextType.SHEET value
    mock_sheets = []
    
    with patch("pecha_api.sheets.sheets_service.get_texts_by_text_type", new_callable=AsyncMock, return_value=mock_sheets) as mock_get_texts:
        await get_sheets()
        
        # Verify that the text_type parameter is always TextType.SHEET.value
        call_args = mock_get_texts.call_args
        assert call_args[1]['text_type'] == TextType.SHEET.value
        
        # Make sure it's not any other text type
        assert call_args[1]['text_type'] != TextType.COMMENTARY.value
        assert call_args[1]['text_type'] != "commentary"
        assert call_args[1]['text_type'] != "version"
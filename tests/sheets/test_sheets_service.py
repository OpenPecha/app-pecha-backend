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
    SheetIdResponse,
    SheetDetailDTO,
    SheetSection
    SheetModel,
    Publisher
)
from pecha_api.texts.segments.segments_enum import SegmentType
from pecha_api.texts.texts_response_models import (
    TableOfContent,
    Section,
    TextSegment,
    TextDTO,
    TextSegment,
    TableOfContentResponse
)
from pecha_api.texts.texts_enums import TextType
from pecha_api.sheets.sheets_service import (
    create_new_sheet,
    update_sheet_by_id,
    get_sheet_by_id,
    delete_sheet_by_id,
    get_sheets_with_filters,
    _create_publisher_object,
    _create_sheet_model
)
from pecha_api.users.users_models import Users
from pecha_api.texts.segments.segments_response_models import (
    SegmentDTO, 
    SegmentResponse
)
from pecha_api.users.user_response_models import UserInfoResponse
from pecha_api.texts.texts_enums import TextType
from pecha_api.texts.texts_models import Text


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
        Source(
            position=2,
            type=SegmentType.CONTENT,
            content="content"
        ),
        Source(
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
        "email": "test_user@gmail.com",
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
        assert isinstance(response, SheetIdResponse)
        assert response.sheet_id == "text_id"

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
        Source(
            position=2,
            type=SegmentType.CONTENT,
            content="content"
        ),
        Source(
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
        assert isinstance(response, SheetIdResponse)
        assert response.sheet_id == "text_id"

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
async def test_get_sheet_by_id_success():
    sheet_id = "text_id"
    mock_sheet_details = TextDTO(
        id=sheet_id,
        title="sheet_title",
        language="language",
        group_id="group_id",
        type=TextType.SHEET,
        is_published=True,
        created_date="2021-01-01",
        updated_date="2021-01-01",
        published_date="2021-01-01",
        published_by="test_user",
        categories=[],
        views=10
    )
    mock_user_details = UserInfoResponse(
        firstname="firstname",
        lastname="lastname",
        username="username",
        email="test_user@gmail.com",
        educations=[],
        followers=0,
        following=0,
        social_profiles=[]
    )
    mock_table_of_content_response = TableOfContentResponse(
        text_detail=mock_sheet_details,
        contents=[
            TableOfContent(
                text_id=sheet_id,
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
                            )
                        ]
                    )
                ]
            )
        ]
    )
    segment_dict = {
        "segment_id_1": SegmentDTO(
            id="segment_id_1",
            text_id="text_id",
            content="content",
            type=SegmentType.CONTENT,
        ),
        "segment_id_2": SegmentDTO(
            id="segment_id_2",
            text_id="text_id",
            content="content",
            type=SegmentType.IMAGE,
        )
    }
    with patch("pecha_api.sheets.sheets_service.TextUtils.get_text_details_by_id", new_callable=AsyncMock, return_value=mock_sheet_details), \
        patch("pecha_api.sheets.sheets_service.fetch_user_by_email", new_callable=MagicMock, return_value=mock_user_details), \
        patch("pecha_api.sheets.sheets_service.get_segments_details_by_ids", new_callable=AsyncMock, return_value=segment_dict), \
        patch("pecha_api.sheets.sheets_service.get_table_of_contents_by_text_id", new_callable=AsyncMock, return_value=mock_table_of_content_response):

        response = await get_sheet_by_id(sheet_id=sheet_id, skip=0, limit=10)

        assert response is not None
        assert isinstance(response, SheetDetailDTO)
        assert response.id == sheet_id
        assert response.sheet_title == "sheet_title"
        assert response.publisher is not None
        assert isinstance(response.content, SheetSection)
        assert response.content is not None
        

@pytest.mark.asyncio
async def test_get_sheet_by_id_invalid_sheet_id():
    sheet_id="invalid_sheet_id"
    with patch("pecha_api.texts.texts_utils.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await get_sheet_by_id(sheet_id=sheet_id, skip=0, limit=10)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_delete_sheet_success():
    mock_sheet_id = "text_id"
    mock_token = "valid_token"
    text_details = TextDTO(
        id="sheet_id",
        title="sheet_title",
        language="language",
        group_id="group_id",
        type=TextType.SHEET,
        is_published=True,
        created_date="2021-01-01",
        updated_date="2021-01-01",
        published_date="2021-01-01",
        published_by="test_user@gmail.com",
        categories=[],
        views=10
    )
    mock_user_details = UserInfoResponse(
        firstname="firstname",
        lastname="lastname",
        username="username",
        email="test_user@gmail.com",
        educations=[],
        followers=0,
        following=0,
        social_profiles=[]
    )
    with patch("pecha_api.sheets.sheets_service.validate_user_exists", return_value=True), \
        patch("pecha_api.sheets.sheets_service.TextUtils.get_text_details_by_id", new_callable=AsyncMock, return_value=text_details), \
        patch("pecha_api.sheets.sheets_service.get_user_info", new_callable=MagicMock, return_value=mock_user_details), \
        patch("pecha_api.sheets.sheets_service.delete_group_by_group_id", new_callable=AsyncMock), \
        patch("pecha_api.sheets.sheets_service.remove_segments_by_text_id", new_callable=AsyncMock), \
        patch("pecha_api.sheets.sheets_service.remove_table_of_content_by_text_id", new_callable=AsyncMock), \
        patch("pecha_api.sheets.sheets_service.delete_text_by_text_id", new_callable=AsyncMock):

        response = await delete_sheet_by_id(
            sheet_id=mock_sheet_id,
            token=mock_token
        )

        assert response is None
    
@pytest.mark.asyncio
async def test_delete_sheet_invalid_token():
    with patch("pecha_api.sheets.sheets_service.validate_user_exists", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await delete_sheet_by_id(
                sheet_id="text_id",
                token="invalid_token"
            )
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

@pytest.mark.asyncio
async def test_delete_sheet_invalid_sheet_id():
    with patch("pecha_api.sheets.sheets_service.validate_user_exists", return_value=True), \
        patch("pecha_api.texts.texts_utils.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await delete_sheet_by_id(
                sheet_id="invalid_sheet_id",
                token="valid_token"
            )
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE







# Test cases for get_sheets_with_filters function
@pytest.mark.asyncio
async def test_get_sheets_with_filters_community_page_all_published():
    #Test get_sheets_with_filters for community page - show all published sheets
    mock_user_details = type("User", (), {
        "email": "current_user@gmail.com",
    })
    
    mock_text = type("Text", (), {
        "id": "text_id",
        "title": "Test Sheet",
        "published_date": "2021-01-01",
        "views": 100,
        "published_by": "test_publisher",
        "language": "en"
    })
    
    with patch("pecha_api.sheets.sheets_service.validate_and_extract_user_details", return_value=mock_user_details), \
         patch("pecha_api.sheets.sheets_service.Text.get_sheets_filtered", new_callable=AsyncMock, return_value=[mock_text]), \
         patch("pecha_api.sheets.sheets_service._create_sheet_model", return_value=SheetModel(
             id="text_id",
             title="Test Sheet",
             summary="",
             published_date="2021-01-01",
             time_passed="",
             views="100",
             likes=[],
             publisher=Publisher(id="pub_id", name="Test Publisher"),
             language="en"
         )):
        
        result = await get_sheets_with_filters(
            token="valid_token",
            language="en",
            email=None,
            skip=0,
            limit=10
        )
        
        assert len(result) == 1
        assert result[0].id == "text_id"
        assert result[0].title == "Test Sheet"

@pytest.mark.asyncio
async def test_get_sheets_with_filters_user_own_sheets():
    #Test get_sheets_with_filters for user's own sheets - show both published and unpublished
    mock_user_details = type("User", (), {
        "email": "current_user@gmail.com",
    })
    
    mock_texts = [
        type("Text", (), {
            "id": "text_id_1",
            "title": "Published Sheet",
            "published_date": "2021-01-01",
            "views": 100,
            "published_by": "current_user",
            "language": "en"
        }),
        type("Text", (), {
            "id": "text_id_2",
            "title": "Unpublished Sheet",
            "published_date": "2021-01-02",
            "views": 50,
            "published_by": "current_user",
            "language": "en"
        })
    ]
    
    with patch("pecha_api.sheets.sheets_service.validate_and_extract_user_details", return_value=mock_user_details), \
         patch("pecha_api.sheets.sheets_service.get_username_by_email", return_value="current_user"), \
         patch("pecha_api.sheets.sheets_service.Text.get_sheets_filtered", new_callable=AsyncMock, return_value=mock_texts), \
         patch("pecha_api.sheets.sheets_service._create_sheet_model", side_effect=lambda text: SheetModel(
             id=text.id,
             title=text.title,
             summary="",
             published_date=text.published_date,
             time_passed="",
             views=str(text.views),
             likes=[],
             publisher=Publisher(id="pub_id", name="Current User"),
             language=text.language
         )):
        
        result = await get_sheets_with_filters(
            token="valid_token",
            language="en",
            email="current_user@gmail.com",
            skip=0,
            limit=10
        )
        
        assert len(result) == 2
        assert result[0].id == "text_id_1"
        assert result[1].id == "text_id_2"

@pytest.mark.asyncio
async def test_get_sheets_with_filters_other_user_sheets():
    #Test get_sheets_with_filters for other user's sheets - show only published
    mock_user_details = type("User", (), {
        "email": "current_user@gmail.com",
    })
    
    mock_text = type("Text", (), {
        "id": "text_id",
        "title": "Other User's Sheet",
        "published_date": "2021-01-01",
        "views": 100,
        "published_by": "other_user",
        "language": "en"
    })
    
    with patch("pecha_api.sheets.sheets_service.validate_and_extract_user_details", return_value=mock_user_details), \
         patch("pecha_api.sheets.sheets_service.get_username_by_email", return_value="other_user"), \
         patch("pecha_api.sheets.sheets_service.Text.get_sheets_filtered", new_callable=AsyncMock, return_value=[mock_text]), \
         patch("pecha_api.sheets.sheets_service._create_sheet_model", return_value=SheetModel(
             id="text_id",
             title="Other User's Sheet",
             summary="",
             published_date="2021-01-01",
             time_passed="",
             views="100",
             likes=[],
             publisher=Publisher(id="pub_id", name="Other User"),
             language="en"
         )):
        
        result = await get_sheets_with_filters(
            token="valid_token",
            language="en",
            email="other_user@gmail.com",
            skip=0,
            limit=10
        )
        
        assert len(result) == 1
        assert result[0].id == "text_id"
        assert result[0].title == "Other User's Sheet"

@pytest.mark.asyncio
async def test_get_sheets_with_filters_user_not_found():
    #Test get_sheets_with_filters when email user doesn't exist
    mock_user_details = type("User", (), {
        "email": "current_user@gmail.com",
    })
    
    with patch("pecha_api.sheets.sheets_service.validate_and_extract_user_details", return_value=mock_user_details), \
         patch("pecha_api.sheets.sheets_service.get_username_by_email", return_value=None):
        
        with pytest.raises(HTTPException) as exc_info:
            await get_sheets_with_filters(
                token="valid_token",
                language="en",
                email="nonexistent@gmail.com",
                skip=0,
                limit=10
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_sheets_with_filters_invalid_token():
    #Test get_sheets_with_filters with invalid token
    with patch("pecha_api.sheets.sheets_service.validate_and_extract_user_details", side_effect=HTTPException(status_code=401, detail="Invalid token")):
        
        with pytest.raises(HTTPException) as exc_info:
            await get_sheets_with_filters(
                token="invalid_token",
                language="en",
                email=None,
                skip=0,
                limit=10
            )
        
        assert exc_info.value.status_code == 401

# Test cases for _create_publisher_object function
def test_create_publisher_object_with_user_profile():
    #Test _create_publisher_object when user profile exists
    mock_user_profile = {
        "id": "user_123",
        "firstname": "John",
        "lastname": "Doe",
        "username": "johndoe",
        "avatar_url": "https://example.com/avatar.jpg"
    }
    
    with patch("pecha_api.sheets.sheets_service.get_publisher_info_by_username", return_value=mock_user_profile):
        result = _create_publisher_object("johndoe")
        
        assert isinstance(result, Publisher)
        assert result.id == "user_123"
        assert result.name == "John Doe"
        assert result.profile_url is None
        assert result.image_url == "https://example.com/avatar.jpg"

def test_create_publisher_object_with_partial_user_profile():
    #Test _create_publisher_object when user profile has missing names
    mock_user_profile = {
        "id": "user_123",
        "username": "johndoe",
        "avatar_url": "https://example.com/avatar.jpg"
    }
    
    with patch("pecha_api.sheets.sheets_service.get_publisher_info_by_username", return_value=mock_user_profile):
        result = _create_publisher_object("johndoe")
        
        assert isinstance(result, Publisher)
        assert result.id == "user_123"
        assert result.name == "johndoe"  # Falls back to username
        assert result.profile_url is None
        assert result.image_url == "https://example.com/avatar.jpg"


# Test cases for _create_sheet_model function
def test_create_sheet_model_success():
    #Test _create_sheet_model with valid Text object
    mock_text = type("Text", (), {
        "id": "sheet_123",
        "title": "Test Sheet Title",
        "published_date": "2021-01-01T00:00:00Z",
        "views": 150,
        "published_by": "test_user",
        "language": "en"
    })
    
    mock_publisher = Publisher(
        id="user_123",
        name="Test User",
        profile_url=None,
        image_url="https://example.com/avatar.jpg"
    )
    
    with patch("pecha_api.sheets.sheets_service._create_publisher_object", return_value=mock_publisher):
        result = _create_sheet_model(mock_text)
        
        assert isinstance(result, SheetModel)
        assert result.id == "sheet_123"
        assert result.title == "Test Sheet Title"
        assert result.summary == ""
        assert result.published_date == "2021-01-01T00:00:00Z"
        assert result.time_passed == ""
        assert result.views == "150"
        assert result.likes == []
        assert result.publisher == mock_publisher
        assert result.language == "en"

def test_create_sheet_model_with_none_language():
    """Test _create_sheet_model when language is None"""
    mock_text = type("Text", (), {
        "id": "sheet_123",
        "title": "Test Sheet Title",
        "published_date": "2021-01-01T00:00:00Z",
        "views": 0,
        "published_by": "test_user",
        "language": None
    })
    
    mock_publisher = Publisher(
        id="user_123",
        name="Test User",
        profile_url=None,
        image_url=None
    )
    
    with patch("pecha_api.sheets.sheets_service._create_publisher_object", return_value=mock_publisher):
        result = _create_sheet_model(mock_text)
        
        assert isinstance(result, SheetModel)
        assert result.id == "sheet_123"
        assert result.title == "Test Sheet Title"
        assert result.views == "0"
        assert result.language is None
        assert result.publisher == mock_publisher

def test_create_sheet_model_calls_create_publisher_object():
    #Test that _create_sheet_model properly calls _create_publisher_object
    mock_text = type("Text", (), {
        "id": "sheet_123",
        "title": "Test Sheet Title",
        "published_date": "2021-01-01T00:00:00Z",
        "views": 100,
        "published_by": "test_publisher_username",
        "language": "en"
    })
    
    mock_publisher = Publisher(
        id="user_123",
        name="Test Publisher",
        profile_url=None,
        image_url=None
    )
    
    with patch("pecha_api.sheets.sheets_service._create_publisher_object", return_value=mock_publisher) as mock_create_publisher:
        result = _create_sheet_model(mock_text)
        
        # Verify that _create_publisher_object was called with the correct username
        mock_create_publisher.assert_called_once_with("test_publisher_username")
        assert result.publisher == mock_publisher
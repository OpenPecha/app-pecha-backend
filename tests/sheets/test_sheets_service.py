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
    SheetSection,
    SheetDTO,
    Publisher,
    SheetDTOResponse,
    SheetDTO
)
from pecha_api.texts.segments.segments_enum import SegmentType
from pecha_api.texts.texts_response_models import (
    TableOfContent,
    Section,
    TextSegment,
    TextDTO,
    TextSegment,
    TableOfContentResponse,
    TextDTOResponse,
    TextDTO
)
from pecha_api.texts.texts_enums import TextType
from pecha_api.sheets.sheets_service import (
    create_new_sheet,
    update_sheet_by_id,
    get_sheet_by_id,
    delete_sheet_by_id,
    fetch_sheets
)

from pecha_api.texts.segments.segments_response_models import (
    SegmentDTO, 
    SegmentResponse
)
from pecha_api.users.user_response_models import UserInfoResponse
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
        Source(
            position=2,
            type=SegmentType.CONTENT,
            content="content"
        ),
        Source(
            position=3,
            type=SegmentType.IMAGE,
            content="image_url"
        )
    ]
    mock_create_sheet_request = CreateSheetRequest(
        title="sheet_title",
        source=mock_source,
        is_published=True
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
                id="segment_id_1",
                text_id="text_id",
                content="source_segment_id",
                type=SegmentType.SOURCE
            ),
            SegmentDTO(
                id="segment_id_2",
                text_id="text_id",
                content="content",
                type=SegmentType.CONTENT
            ),
            SegmentDTO(
                id="segment_id_3",
                text_id="text_id",
                content="image_url",
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
            content="image_url"
        )
    ]
    mock_segment_response = SegmentResponse(
        segments=[
            SegmentDTO(
                id="segment_id_1",
                text_id="text_id",
                content="source_segment_id",
                type=SegmentType.SOURCE
            ),
            SegmentDTO(
                id="segment_id_2",
                text_id="text_id",
                content="content",
                type=SegmentType.CONTENT
            ),
            SegmentDTO(
                id="segment_id_3",
                text_id="text_id",
                content="image_url",
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
    mock_table_of_content_response = TableOfContent(
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
    with patch("pecha_api.sheets.sheets_service.fetch_user_by_email", new_callable=MagicMock, return_value=mock_user_details), \
        patch("pecha_api.sheets.sheets_service.get_segments_details_by_ids", new_callable=AsyncMock, return_value=segment_dict), \
        patch("pecha_api.sheets.sheets_service.get_table_of_content_by_sheet_id", new_callable=AsyncMock, return_value=mock_table_of_content_response), \
        patch("pecha_api.sheets.sheets_service.generate_presigned_upload_url", new_callable=MagicMock, return_value="image_url"), \
        patch("pecha_api.sheets.sheets_service.TextUtils.get_text_details_by_id", new_callable=AsyncMock, return_value=mock_sheet_details):

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
async def test_get_sheet_by_id_table_of_content_not_found():
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
        patch("pecha_api.sheets.sheets_service.get_table_of_content_by_sheet_id", new_callable=AsyncMock, return_value=None):

        with pytest.raises(HTTPException) as exc_info:
            await get_sheet_by_id(sheet_id=sheet_id, skip=0, limit=10)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.TABLE_OF_CONTENT_NOT_FOUND_MESSAGE

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
        patch("pecha_api.sheets.sheets_service.get_user_info", new_callable=AsyncMock, return_value=mock_user_details), \
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







# Test cases for fetch_sheets function
@pytest.mark.asyncio
async def test_fetch_sheets_community_page_all_published():
    mock_user = UserInfoResponse(
        firstname="firstname",
        lastname="lastname",
        username="username",
        email="test_user@gmail.com",
        educations=[],
        avatar_url="avatar_url",
        social_profiles=[],
        followers=0,
        following=0,
    )
    mock_sheets = _generate_mock_sheets_response_()
    
    with patch("pecha_api.sheets.sheets_service.get_sheet", new_callable=AsyncMock, return_value=mock_sheets), \
        patch("pecha_api.sheets.sheets_service.Utils.time_passed", return_value="time passed"), \
        patch("pecha_api.sheets.sheets_service.fetch_user_by_email", new_callable=MagicMock, return_value=mock_user):
        
        result = await fetch_sheets(
            token="valid_token",
            language="en",
            email=None,
            skip=0,
            limit=10
        )
        
        assert result is not None
        assert isinstance(result, SheetDTOResponse)
        assert result.sheets is not None
        assert len(result.sheets) == 5
        assert isinstance(result.sheets[0], SheetDTO)
        assert result.sheets[0].id == "sheet_id_1"
        assert result.sheets[-1].id == "sheet_id_5"

@pytest.mark.asyncio
async def test_fetch_sheets_user_own_sheets():
    #Test fetch_sheets for user's own sheets - show both published and unpublished
    mock_user_details = type("User", (), {
        "email": "mock_user@gmail.com",
    })
    mock_publisher_details = UserInfoResponse(
        firstname="firstname",
        lastname="lastname",
        username="username",
        email="mock_user@gmail.com",
        educations=[],
        followers=0,
        following=0,
        social_profiles=[]
    )
    mock_sheets = _generate_mock_sheets_response_()
    for i in range(len(mock_sheets)):
        mock_sheets[i].published_by = "mock_user@gmail.com"
    
    with patch("pecha_api.sheets.sheets_service.validate_and_extract_user_details", return_value=mock_user_details), \
        patch("pecha_api.sheets.sheets_service.Utils.time_passed", return_value="time passed"), \
        patch("pecha_api.sheets.sheets_service.fetch_user_by_email", new_callable=MagicMock, return_value=mock_publisher_details), \
        patch("pecha_api.sheets.sheets_service.get_sheet", new_callable=AsyncMock, return_value=mock_sheets):
        
        result = await fetch_sheets(
            token="valid_token",
            email="mock_user@gmail.com",
            skip=0,
            limit=10
        )
        
        assert result is not None
        assert isinstance(result, SheetDTOResponse)
        assert result.sheets is not None
        assert len(result.sheets) == 5
        assert isinstance(result.sheets[0], SheetDTO)
        assert result.sheets[0].id == "sheet_id_1"
        assert result.sheets[-1].id == "sheet_id_5"

@pytest.mark.asyncio
async def test_fetch_sheets_user_viewing_other_users_sheets_status_logged_in():
    #Test fetch_sheets for user viewing other user's sheets - show only published
    mock_user_details = type("User", (), {
        "email": "mock_user@gmail.com",
    })
    mock_publisher_details = UserInfoResponse(
        firstname="firstname",
        lastname="lastname",
        username="username",
        email="other_user@gmail.com",
        educations=[],
        followers=0,
        following=0,
        social_profiles=[]
    )
    mock_sheets = _generate_mock_sheets_response_()
    for i in range(len(mock_sheets)):
        mock_sheets[i].published_by = "other_user@gmail.com"
    
    with patch("pecha_api.sheets.sheets_service.validate_and_extract_user_details", return_value=mock_user_details), \
        patch("pecha_api.sheets.sheets_service.Utils.time_passed", return_value="time passed"), \
        patch("pecha_api.sheets.sheets_service.fetch_user_by_email", new_callable=MagicMock, return_value=mock_publisher_details), \
        patch("pecha_api.sheets.sheets_service.get_sheet", new_callable=AsyncMock, return_value=mock_sheets):
        
        result = await fetch_sheets(
            token="valid_token",
            language="en",
            email="test_user@gmail.com",
            skip=0,
            limit=10
        )
        
        assert result is not None
        assert isinstance(result, SheetDTOResponse)
        assert result.sheets is not None
        assert len(result.sheets) == 5
        assert isinstance(result.sheets[0], SheetDTO)
        assert result.sheets[0].id == "sheet_id_1"
        assert result.sheets[-1].id == "sheet_id_5"

@pytest.mark.asyncio
async def test_fetch_sheets_invalid_token():
    #Test fetch_sheets with invalid token
    with patch("pecha_api.sheets.sheets_service.validate_and_extract_user_details", side_effect=HTTPException(status_code=401, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)), \
        patch("pecha_api.sheets.sheets_service.Utils.time_passed", return_value="time passed"):
        with pytest.raises(HTTPException) as exc_info:
            await fetch_sheets(
                token="invalid_token",
                language="en",
                email="test@example.com",
                skip=0,
                limit=10
            )
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE


def _generate_mock_sheets_response_():
    return [
            TextDTO(
                id=f"sheet_id_{i}",
                title="Test Sheet",
                language="en",
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
            for i in range(1,6)
        ]
    
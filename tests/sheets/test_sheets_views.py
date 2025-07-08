import pytest
from unittest.mock import patch, AsyncMock


from pecha_api.sheets.sheets_views import (
    create_sheet,
    get_sheet
)
from pecha_api.sheets.sheets_response_models import (
    CreateSheetRequest,
    SheetDetailDTO,
    SheetSection,
    Publisher
)

from pecha_api.texts.texts_response_models import TableOfContent, Section, TextSegment

@pytest.mark.asyncio
async def test_create_sheet_success():
    mock_source = []
    mock_create_sheet_request = CreateSheetRequest(
        title="sheet_title",
        source=mock_source
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
    
    with patch("pecha_api.sheets.sheets_views.create_new_sheet", new_callable=AsyncMock, return_value=mock_table_of_content_response):

        response = await create_sheet(
            create_sheet_request=mock_create_sheet_request,
            authentication_credential=type("HTTPAuthorizationCredentials", (), {"credentials": "valid_token"})()
        )

        assert response is not None
        assert isinstance(response, TableOfContent)
        assert response.id == "table_of_content_id"
        assert response.text_id == "text_id"


@pytest.mark.asyncio
async def test_get_sheet_success():
    sheet_id = "test_sheet_id"
    skip = 0
    limit = 10
    
    mock_sheet_detail = SheetDetailDTO(
        id=sheet_id,
        sheet_title="Test Sheet Title",
        created_date="2024-01-01T00:00:00Z",
        publisher=Publisher(
            name="Test User",
            username="testuser",
            email="test@example.com"
        ),
        content=SheetSection(
            section_number=1,
            segments=[]
        ),
        skip=skip,
        limit=limit,
        total=1
    )
    
    with patch("pecha_api.sheets.sheets_views.get_sheet_by_id", new_callable=AsyncMock, return_value=mock_sheet_detail):
        response = await get_sheet(
            sheet_id=sheet_id,
            skip=skip,
            limit=limit
        )
        
        assert response is not None
        assert isinstance(response, SheetDetailDTO)
        assert response.id == sheet_id
        assert response.sheet_title == "Test Sheet Title"
        assert response.publisher.name == "Test User"
        assert response.publisher.email == "test@example.com"
        assert response.skip == skip
        assert response.limit == limit
        assert response.total == 1


@pytest.mark.asyncio
async def test_get_sheet_with_custom_pagination():
    sheet_id = "test_sheet_id"
    skip = 5
    limit = 20
    
    mock_sheet_detail = SheetDetailDTO(
        id=sheet_id,
        sheet_title="Test Sheet Title",
        created_date="2024-01-01T00:00:00Z",
        publisher=Publisher(
            name="Test User",
            username="testuser",
            email="test@example.com"
        ),
        content=SheetSection(
            section_number=1,
            segments=[]
        ),
        skip=skip,
        limit=limit,
        total=1
    )
    
    with patch("pecha_api.sheets.sheets_views.get_sheet_by_id", new_callable=AsyncMock, return_value=mock_sheet_detail) as mock_service:
        response = await get_sheet(
            sheet_id=sheet_id,
            skip=skip,
            limit=limit
        )
        
        # Verify the service function was called with correct parameters
        mock_service.assert_called_once_with(sheet_id=sheet_id, skip=skip, limit=limit)
        
        assert response is not None
        assert isinstance(response, SheetDetailDTO)
        assert response.id == sheet_id
        assert response.skip == skip
        assert response.limit == limit
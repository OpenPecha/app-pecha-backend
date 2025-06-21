import pytest
from unittest.mock import patch, AsyncMock


from pecha_api.sheets.sheets_views import (
    create_sheet
)
from pecha_api.sheets.sheets_response_models import (
    CreateSheetRequest,
    Source,
    Content,
    Media
)
from pecha_api.texts.segments.segments_enum import SegmentType

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
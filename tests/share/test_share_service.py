from unittest.mock import patch, AsyncMock
import pytest

from pecha_api.share.share_service import (
    generate_short_url
)
from pecha_api.share.share_response_models import (
    ShortUrlResponse,
    ShareRequest
)
from pecha_api.texts.segments.segments_service import SegmentDTO
from pecha_api.texts.texts_response_models import TextDTO
from pecha_api.texts.segments.segments_enum import SegmentType

@pytest.mark.asyncio
async def test_generate_short_url_with_logo():
    share_request = ShareRequest(
        logo=True,
        url="https://pecha.io/share/123",
    )
    mock_short_url_response = ShortUrlResponse(
        shortUrl="https://pecha.io/share/123"
    )
    with patch("pecha_api.share.share_service.get_short_url", new_callable=AsyncMock) as mock_short_url:
        mock_short_url.return_value = mock_short_url_response
        
        response = await generate_short_url(share_request=share_request)
        
        assert response is not None
        assert isinstance(response, ShortUrlResponse)
        assert response.shortUrl == "https://pecha.io/share/123"

@pytest.mark.asyncio
async def test_generate_short_url_for_segment_content_success():
    share_request = ShareRequest(
        url="https://pecha.io/share/123",
        segment_id="id_1",
        language="en",
    )
    mock_short_url_response = ShortUrlResponse(
        shortUrl="https://pecha.io/share/123"
    )
    mock_segment_details = SegmentDTO(
        id="id_1",
        text_id="text_1",
        content="content_1",
        mapping=[],
        type=SegmentType.SOURCE
    )
    mock_text_detail = TextDTO(
        id="text_1",
        title="title_1",
        language="en",
        type="version",
        group_id="group_1",
        is_published=True,
        created_date="2021-01-01",
        updated_date="2021-01-01",
        published_date="2021-01-01",
        published_by="user_1",
        categories=[],
        views=0
    )
    with patch("pecha_api.share.share_service.get_short_url", new_callable=AsyncMock, return_value=mock_short_url_response),\
        patch("pecha_api.share.share_service.SegmentUtils.validate_segment_exists", new_callable=AsyncMock, return_value=True),\
        patch("pecha_api.share.share_service.get_segment_details_by_id", new_callable=AsyncMock, return_value=mock_segment_details),\
        patch("pecha_api.share.share_service.TextUtils.get_text_detail_by_id", new_callable=AsyncMock, return_value=mock_text_detail):
        
        response = await generate_short_url(share_request=share_request)
        
        assert response is not None
        assert isinstance(response, ShortUrlResponse)
        assert response.shortUrl == "https://pecha.io/share/123"
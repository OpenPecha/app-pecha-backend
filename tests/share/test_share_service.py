from unittest.mock import patch, AsyncMock
import pytest

from pecha_api.share.share_service import (
    generate_short_url,
    _generate_short_url_payload_,
    _generate_url_
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

def test_generate_short_url_payload_with_provided_url():
    share_request = ShareRequest(
        url="https://pecha.io/share/123",
        segment_id="seg_123",
        language="en",
        logo=True,
        tags="tag1,tag2"
    )
    og_description = "Test description"
    
    with patch("pecha_api.share.share_service.get") as mock_get:
        mock_get.return_value = "https://backend.example.com"
        
        payload = _generate_short_url_payload_(share_request, og_description)
        
        assert payload["url"] == "https://pecha.io/share/123"
        assert payload["og_title"] == "PECHA"
        assert payload["og_description"] == "Test description"
        assert payload["og_image"] == "https://backend.example.com/share/image?segment_id=seg_123&language=en&logo=True"
        assert payload["tags"] == "tag1,tag2"

def test_generate_short_url_payload_without_url():
    share_request = ShareRequest(
        segment_id="seg_123",
        content_id="content_456",
        text_id="text_789",
        content_index=1,
        language="en",
        logo=False,
        tags="tag1"
    )
    og_description = "Test description"
    
    with patch("pecha_api.share.share_service.get") as mock_get:
        mock_get.return_value = "https://backend.example.com"
        
        payload = _generate_short_url_payload_(share_request, og_description)
        
        expected_url = "https://webuddhist.com/chapter?segment_id=seg_123&contentId=content_456&text_id=text_789&contentIndex=1"
        assert payload["url"] == expected_url
        assert payload["og_title"] == "PECHA"
        assert payload["og_description"] == "Test description"
        assert payload["og_image"] == "https://backend.example.com/share/image?segment_id=seg_123&language=en&logo=False"
        assert payload["tags"] == "tag1"

def test_generate_url():
    segment_id = "seg_123"
    content_id = "content_456"
    text_id = "text_789"
    content_index = 2
    
    # Use correct positional argument order: content_id, text_id, content_index, segment_id
    result = _generate_url_(content_id, text_id, content_index, segment_id)
    
    expected_url = "https://webuddhist.com/chapter?segment_id=seg_123&contentId=content_456&text_id=text_789&contentIndex=2"
    assert result == expected_url
from unittest.mock import patch, AsyncMock
import pytest

from pecha_api.share.share_service import (
    generate_short_url
)
from pecha_api.share.share_response_models import (
    ShortUrlResponse,
    ShareRequest
)

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
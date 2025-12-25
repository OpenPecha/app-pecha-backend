import pytest
from unittest.mock import patch, AsyncMock, Mock
from fastapi import HTTPException
import httpx

from pecha_api.cataloger.cataloger_service import get_cataloged_texts
from pecha_api.constants import Constants


@pytest.fixture
def mock_api_url():
    return "https://api.openpecha.org/texts"


@pytest.fixture
def mock_multiple_texts_data():
    return [
        {
            "id": "text_1",
            "title": {"bo": "བོད་ཡིག", "en": "Tibetan Text"},
            "language": "bo",
        },
        {
            "id": "text_2",
            "title": {"bo": "བོད་ཡིག", "en": "Tibetan Text"},
            "language": "bo",
        },
    ]


@pytest.fixture
def mock_single_text_data():
    return [
        {
            "id": "text_1",
            "title": {"bo": "བོད་ཡིག", "en": "Tibetan Text"},
            "language": "bo",
        },
    ]


@pytest.mark.asyncio
async def test_get_cataloged_texts_success(mock_api_url, mock_multiple_texts_data):
    mock_http_response = Mock()
    mock_http_response.json.return_value = mock_multiple_texts_data
    mock_http_response.raise_for_status = Mock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_http_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "pecha_api.cataloger.cataloger_service.get", return_value=mock_api_url
    ), patch("httpx.AsyncClient", return_value=mock_client):

        response = await get_cataloged_texts(search=None, skip=0, limit=10)

        assert len(response.texts) == 2
        assert response.texts[0].text_id == "text_1"
        assert response.texts[0].status is False

        mock_client.get.assert_called_once_with(
            mock_api_url,
            params={"type": Constants.TEXT_TYPE, "offset": 0, "limit": 10},
        )


@pytest.mark.asyncio
async def test_get_cataloged_texts_with_search(mock_api_url, mock_single_text_data):
    mock_http_response = Mock()
    mock_http_response.json.return_value = mock_single_text_data
    mock_http_response.raise_for_status = Mock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_http_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "pecha_api.cataloger.cataloger_service.get", return_value=mock_api_url
    ), patch("httpx.AsyncClient", return_value=mock_client):

        response = await get_cataloged_texts(search="Tibetan", skip=0, limit=10)

        assert len(response.texts) == 1
        assert response.texts[0].text_id == "text_1"

        mock_client.get.assert_called_once_with(
            mock_api_url,
            params={
                "type": Constants.TEXT_TYPE,
                "offset": 0,
                "limit": 10,
                "title": "Tibetan",
            },
        )


@pytest.mark.asyncio
async def test_get_cataloged_texts_http_error(mock_api_url):
    mock_http_response = Mock()
    mock_http_response.status_code = 500
    mock_http_response.text = "Internal Server Error"

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(
        side_effect=httpx.HTTPStatusError(
            "Server error", request=Mock(), response=mock_http_response
        )
    )
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "pecha_api.cataloger.cataloger_service.get", return_value=mock_api_url
    ), patch("httpx.AsyncClient", return_value=mock_client):

        with pytest.raises(HTTPException) as exc_info:
            await get_cataloged_texts(search=None, skip=0, limit=10)

        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_cataloged_texts_request_error(mock_api_url):
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.RequestError("Connection failed"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "pecha_api.cataloger.cataloger_service.get", return_value=mock_api_url
    ), patch("httpx.AsyncClient", return_value=mock_client):

        with pytest.raises(HTTPException) as exc_info:
            await get_cataloged_texts(search=None, skip=0, limit=10)

        assert exc_info.value.status_code == 500
        assert "Failed to connect" in exc_info.value.detail

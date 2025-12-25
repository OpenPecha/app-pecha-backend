import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from starlette import status
from pecha_api.app import api
from pecha_api.cataloger.cataloger_response_model import (
    CatalogedTextsResponse,
    CatalogedTexts,
)

@pytest.fixture
def mock_single_text_response():
    return CatalogedTextsResponse(
        texts=[
            CatalogedTexts(
                text_id="text_1",
                title={"bo": "བོད་ཡིག", "en": "Tibetan Text"},
                language="bo",
                status=False,
            )
        ]
    )


@pytest.fixture
def mock_empty_response():
    return CatalogedTextsResponse(texts=[])


@pytest.mark.asyncio
async def test_read_cataloged_texts_default_params(mocker, mock_single_text_response):
    mock_get_cataloged_texts = mocker.patch(
        "pecha_api.cataloger.cataloger_views.get_cataloged_texts",
        new_callable=AsyncMock,
        return_value=mock_single_text_response,
    )

    async with AsyncClient(
        transport=ASGITransport(app=api), base_url="http://test"
    ) as ac:
        response = await ac.get("/cataloger/texts")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["texts"]) == 1
    assert data["texts"][0]["text_id"] == "text_1"
    mock_get_cataloged_texts.assert_called_once_with(search=None, skip=0, limit=10)


@pytest.mark.asyncio
async def test_read_cataloged_texts_with_params(mocker, mock_empty_response):
    mock_get_cataloged_texts = mocker.patch(
        "pecha_api.cataloger.cataloger_views.get_cataloged_texts",
        new_callable=AsyncMock,
        return_value=mock_empty_response,
    )

    async with AsyncClient(
        transport=ASGITransport(app=api), base_url="http://test"
    ) as ac:
        response = await ac.get("/cataloger/texts?skip=20&limit=5")

    assert response.status_code == status.HTTP_200_OK
    mock_get_cataloged_texts.assert_called_once_with(search=None, skip=20, limit=5)


@pytest.mark.asyncio
async def test_read_cataloged_texts_with_search(mocker, mock_single_text_response):
    mock_get_cataloged_texts = mocker.patch(
        "pecha_api.cataloger.cataloger_views.get_cataloged_texts",
        new_callable=AsyncMock,
        return_value=mock_single_text_response,
    )

    async with AsyncClient(
        transport=ASGITransport(app=api), base_url="http://test"
    ) as ac:
        response = await ac.get("/cataloger/texts?search=Tibetan")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["texts"]) == 1
    assert data["texts"][0]["text_id"] == "text_1"
    mock_get_cataloged_texts.assert_called_once_with(search="Tibetan", skip=0, limit=10)


@pytest.mark.asyncio
async def test_read_cataloged_texts_invalid_params():
    async with AsyncClient(
        transport=ASGITransport(app=api), base_url="http://test"
    ) as ac:
        response = await ac.get("/cataloger/texts?skip=-1")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

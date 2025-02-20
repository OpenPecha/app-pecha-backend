from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from pecha_api.app import api

client = TestClient(api)


@pytest.mark.asyncio
async def test_read_topics_without_parent(mocker):
    mock_response = {"topics": [{"id": "1", "title": "Parent Topic"}]}
    mock_get_topics = mocker.patch('pecha_api.topics.topics_views.get_topics',
                                   new_callable=AsyncMock,
                                   return_value=mock_response)
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get("/topics?skip=0&limit=10")
    assert response.status_code == 200
    assert response.json() == mock_response
    mock_get_topics.assert_called_once_with(parent_id=None, search=None, language=None, skip=0, limit=10)


@pytest.mark.asyncio
async def test_read_topics_with_parent(mocker):
    mock_response = {"topics": [{"id": "1", "title": "Parent Topic"}]}
    mock_get_topics = mocker.patch('pecha_api.topics.topics_views.get_topics',
                                   new_callable=AsyncMock,
                                   return_value=mock_response)
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get("/topics?parent_id=1&skip=0&limit=10")
    assert response.status_code == 200
    assert response.json() == mock_response
    mock_get_topics.assert_called_once_with(parent_id="1", search=None, language=None, skip=0, limit=10)


@pytest.mark.asyncio
async def test_read_topics_language_en(mocker):
    mock_response = {"topics": [{"id": "1", "title": "Parent Topic"}]}
    mock_get_topics = mocker.patch('pecha_api.topics.topics_views.get_topics',
                                   new_callable=AsyncMock,
                                   return_value=mock_response)
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get("/topics?language=en&skip=0&limit=10")
    assert response.status_code == 200
    assert response.json() == mock_response
    mock_get_topics.assert_called_once_with(parent_id=None, search=None, language="en", skip=0, limit=10)

@pytest.mark.asyncio
async def test_read_topics_language_bo(mocker):
    mock_response = {"topics": [{"id": "1", "title": "Parent Topic"}]}
    mock_get_topics = mocker.patch('pecha_api.topics.topics_views.get_topics',
                                   new_callable=AsyncMock,
                                   return_value=mock_response)
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get("/topics?language=bo&skip=0&limit=10")
    assert response.status_code == 200
    assert response.json() == mock_response
    mock_get_topics.assert_called_once_with(parent_id=None, search=None, language="bo", skip=0, limit=10)


@pytest.mark.asyncio
async def test_read_topics_pagination(mocker):
    mock_response = {"topics": [{"id": "11", "title": "Parent Topic"}]}
    mock_get_topics = mocker.patch('pecha_api.topics.topics_views.get_topics',
                                   new_callable=AsyncMock,
                                   return_value=mock_response)
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.get("/topics?language=en&skip=1&limit=10")
    assert response.status_code == 200
    assert response.json() == mock_response
    mock_get_topics.assert_called_once_with(parent_id=None, search=None, language="en", skip=1, limit=10)


@pytest.mark.asyncio
async def test_create_topic_success(mocker):
    mock_response = {"id": "1", "title": "New Topic"}
    mocker.patch('pecha_api.topics.topics_views.create_new_topic',
                 new_callable=AsyncMock,
                 return_value=mock_response)
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.post("/topics",
                                 json={"titles": {"en": "En New Topic", "bo": "Bo New Topic"}, "parent_id": "12345",
                                       "default_language": "en"},
                                 headers={"Authorization": "Bearer test_token"})
    assert response.status_code == 201
    assert response.json() == mock_response


@pytest.mark.asyncio
async def test_create_topic_forbidden(mocker):
    mock_response = {"detail": "Not authenticated"}
    mock_create_new_topic = mocker.patch('pecha_api.topics.topics_views.create_new_topic',
                                         new_callable=AsyncMock,
                                         return_value=mock_response)
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
        response = await ac.post("/topics",
                                 json={"titles": {"en": "En New Topic", "bo": "Bo New Topic"}, "parent_id": "12345",
                                       "default_language": "en"})
    assert response.status_code == 403
    assert response.json() == mock_response
    mock_create_new_topic.assert_not_called()

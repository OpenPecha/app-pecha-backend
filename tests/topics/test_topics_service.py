from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from pecha_api.topics.topics_service import get_topics, create_new_topic
from pecha_api.topics.topics_response_models import TopicsResponse, TopicModel, CreateTopicRequest


@pytest.mark.asyncio
async def test_get_topics_without_parent():
    with patch('pecha_api.topics.topics_service.get_child_count', new_callable=AsyncMock, return_value=2), \
            patch('pecha_api.topics.topics_service.get_topics_by_parent',
                  new_callable=AsyncMock) as mock_get_topics_by_parent, \
            patch('pecha_api.config.get', new_callable=AsyncMock, return_value="en"):
        mock_get_topics_by_parent.return_value = [
            AsyncMock(id="id_1", titles={"en": "Topic English", "bo": "Topic Tibetan"}, parent_id=None,
                      default_language="en",has_sub_child=False),
            AsyncMock(id="id_2", titles={"en": "Topic English 2", "bo": "Topic Tibetan 2"}, parent_id=None,
                      default_language="en",has_sub_child=True)
        ]
        response = await get_topics(language=None, parent_id=None, skip=0, limit=10)
        assert response == TopicsResponse(
            parent=None,
            topics=[TopicModel(id="id_1", title="Topic English",has_child=False), TopicModel(id="id_2", title="Topic English 2",has_child=True)],
            total=2, skip=0, limit=10
        )


@pytest.mark.asyncio
async def test_get_topics_with_parent():
    with patch('pecha_api.topics.topics_service.get_child_count', new_callable=AsyncMock, return_value=1), \
            patch('pecha_api.topics.topics_service.get_topics_by_parent',
                  new_callable=AsyncMock) as mock_get_topics_by_parent, \
            patch('pecha_api.topics.topics_service.get_topic_by_id',new_callable=AsyncMock) as mock_get_topic_by_id, \
            patch('pecha_api.config.get', return_value="en"):
        mock_get_topics_by_parent.return_value = [
            AsyncMock(id="id_1", titles={"en": "Topic English", "bo": "Topic Tibetan"}, parent_id=None,
                      default_language="en",has_sub_child=False)
        ]
        mock_get_topic_by_id.return_value = AsyncMock(id="id_3",
                                                titles={"en": "Topic English Parent", "bo": "Topic Tibetan Parent"},
                                                parent_id=None,
                                                default_language="en",
                                                has_sub_child=False
                                                )

        response = await get_topics(language=None, parent_id="1", skip=0, limit=10)
        assert response == TopicsResponse(parent=TopicModel(id="id_3", title="Topic English Parent",has_child=False),topics=[TopicModel(id="id_1", title="Topic English",has_child=False)], total=1, skip=0,
                                          limit=10)


@pytest.mark.asyncio
async def test_get_topics_language_en():
    with patch('pecha_api.topics.topics_service.get_child_count', new_callable=AsyncMock, return_value=1), \
            patch('pecha_api.topics.topics_service.get_topics_by_parent',
                  new_callable=AsyncMock) as mock_get_topics_by_parent:
        mock_get_topics_by_parent.return_value = [
            AsyncMock(id="id_1", titles={"en": "Topic English", "bo": "Topic Tibetan"}, parent_id=None,
                      default_language="en",has_sub_child=False)
        ]
        response = await get_topics(language="en", parent_id=None, skip=0, limit=10)
        assert response == TopicsResponse(parent=None,topics=[TopicModel(id="id_1", title="Topic English",has_child=False)], total=1, skip=0,
                                          limit=10)


@pytest.mark.asyncio
async def test_get_topics_language_bo():
    with patch('pecha_api.topics.topics_service.get_child_count', new_callable=AsyncMock, return_value=1), \
            patch('pecha_api.topics.topics_service.get_topics_by_parent',
                  new_callable=AsyncMock) as mock_get_topics_by_parent:
        mock_get_topics_by_parent.return_value = [
            AsyncMock(id="id_1", titles={"en": "Topic English", "bo": "Topic Tibetan"}, parent_id=None,
                      default_language="en",has_sub_child=False)
        ]
        response = await get_topics(language="bo", parent_id=None, skip=0, limit=10)
        assert response == TopicsResponse(parent=None,topics=[TopicModel(id="id_1", title="Topic Tibetan",has_child=False)], total=1, skip=0,
                                          limit=10)


@pytest.mark.asyncio
async def test_get_topics_pagination():
    with patch('pecha_api.topics.topics_service.get_child_count', return_value=1), \
            patch('pecha_api.topics.topics_service.get_topics_by_parent',
                  new_callable=AsyncMock) as mock_get_topics_by_parent, \
            patch('pecha_api.config.get', return_value="en"):
        mock_get_topics_by_parent.return_value = [
            AsyncMock(id="id_1", titles={"en": "Topic English", "bo": "Topic Tibetan"}, parent_id=None,
                      default_language="en",has_sub_child=False)
        ]
        response = await get_topics(language=None, parent_id=None, skip=0, limit=1)
        assert response == TopicsResponse(parent=None,topics=[TopicModel(id="id_1", title="Topic English",has_child=False)], total=1, skip=0,
                                          limit=1)


@pytest.mark.asyncio
async def test_create_new_topic_success():
    with patch('pecha_api.topics.topics_service.verify_admin_access', return_value=True), \
            patch('pecha_api.topics.topics_service.create_topic',
                  new_callable=AsyncMock) as mock_create_topic, \
            patch('pecha_api.config.get', return_value="en"):
        mock_create_topic.return_value = AsyncMock(id="id_1", titles={"en": "New Topic English", "bo": "New Topic Tibetan"}, parent_id=None,
                      default_language="en",has_sub_child=False)
        create_topic_request = CreateTopicRequest(titles={"en": "Topic English", "bo": "Topic Tibetan"}, parent_id=None,
                                                  default_language="en")
        response = await create_new_topic(create_topic_request=create_topic_request, token="valid_token", language=None)
        assert response == TopicModel(id="id_1", title="New Topic English",has_child=False)


@pytest.mark.asyncio
async def test_create_new_topic_forbidden():
    with patch('pecha_api.topics.topics_service.verify_admin_access', return_value=False):

        create_topic_request = CreateTopicRequest(titles={"en": "Topic English", "bo": "Topic Tibetan"}, parent_id=None,
                                              default_language="en")
        with pytest.raises(HTTPException) as excinfo:
            await create_new_topic(create_topic_request=create_topic_request, token="invalid_token", language=None)
        assert excinfo.value.status_code == 403
        assert excinfo.value.detail == "Admin access required"

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from pecha_api.topics.topics_service import get_topics, create_new_topic
from pecha_api.topics.topics_response_models import TopicsResponse, TopicModel, CreateTopicRequest


@pytest.mark.asyncio
async def test_get_topics_without_parent():
    with patch('pecha_api.topics.topics_service.get_child_count', new_callable=AsyncMock, return_value=2), \
        patch('pecha_api.topics.topics_service.get_topics_cache', return_value=None), \
        patch('pecha_api.topics.topics_service.set_topics_cache', return_value=None), \
            patch('pecha_api.topics.topics_service.get_topics_by_parent',
                  new_callable=AsyncMock) as mock_get_topics_by_parent, \
            patch('pecha_api.config.get', new_callable=AsyncMock, return_value="en"):
        mock_get_topics_by_parent.return_value = [
            AsyncMock(id="id_1", titles={"en": "Happiness", "bo": "བདེ་སྐྱིད།"}, parent_id=None,
                      default_language="en",has_sub_child=False),
            AsyncMock(id="id_2", titles={"en": "Kindness", "bo": "བྱམས་སེམས།"}, parent_id=None,
                      default_language="en",has_sub_child=True)
        ]
        response = await get_topics(language=None, search=None, parent_id=None, hierarchy=True, skip=0, limit=10)
        assert response == TopicsResponse(
            parent=None,
            topics=[TopicModel(id="id_1", title="Happiness",has_child=False), TopicModel(id="id_2", title="Kindness",has_child=True)],
            total=2, skip=0, limit=10
        )


@pytest.mark.asyncio
async def test_get_topics_with_parent():
    with patch('pecha_api.topics.topics_service.get_child_count', new_callable=AsyncMock, return_value=1), \
            patch('pecha_api.topics.topics_service.get_topics_by_parent',
                  new_callable=AsyncMock) as mock_get_topics_by_parent, \
            patch('pecha_api.topics.topics_service.get_topic_by_id',new_callable=AsyncMock) as mock_get_topic_by_id, \
            patch('pecha_api.topics.topics_service.get_topics_cache', return_value=None), \
        patch('pecha_api.topics.topics_service.set_topics_cache', return_value=None), \
            patch('pecha_api.config.get', return_value="en"):
        mock_get_topics_by_parent.return_value = [
            AsyncMock(id="id_1", titles={"en": "The power of loving kindness", "bo": "བྱམས་སེམས་ཀྱི་ནུས་པ།"}, parent_id=None,
                      default_language="en",has_sub_child=False)
        ]
        mock_get_topic_by_id.return_value = AsyncMock(id="id_3",
                                                titles={"en": "Kindness", "bo": "བྱམས་སེམས"},
                                                parent_id=None,
                                                default_language="en",
                                                has_sub_child=True
                                                )

        response = await get_topics(language=None,search=None, parent_id="id_3", hierarchy=True, skip=0, limit=10)
        assert response == TopicsResponse(parent=TopicModel(id="id_3", title="Kindness",has_child=True),topics=[TopicModel(id="id_1", title="The power of loving kindness",has_child=False)], total=1, skip=0,

                                          limit=10)


@pytest.mark.asyncio
async def test_get_topics_language_en():
    with patch('pecha_api.topics.topics_service.get_child_count', new_callable=AsyncMock, return_value=1), \
        patch('pecha_api.topics.topics_service.get_topics_cache', return_value=None), \
        patch('pecha_api.topics.topics_service.set_topics_cache', return_value=None), \
            patch('pecha_api.topics.topics_service.get_topics_by_parent',
                  new_callable=AsyncMock) as mock_get_topics_by_parent:
        mock_get_topics_by_parent.return_value = [
            AsyncMock(id="id_1", titles={"en": "Happiness", "bo": "བདེ་སྐྱིད།"}, parent_id=None,
                      default_language="en",has_sub_child=True)
        ]
        response = await get_topics(language="en", search=None,parent_id=None, hierarchy=True, skip=0, limit=10)
        assert response == TopicsResponse(parent=None,topics=[TopicModel(id="id_1", title="Happiness",has_child=True)], total=1, skip=0,

                                          limit=10)


@pytest.mark.asyncio
async def test_get_topics_language_bo():
    with patch('pecha_api.topics.topics_service.get_child_count', new_callable=AsyncMock, return_value=1), \
        patch('pecha_api.topics.topics_service.get_topics_cache', return_value=None), \
        patch('pecha_api.topics.topics_service.set_topics_cache', return_value=None), \
            patch('pecha_api.topics.topics_service.get_topics_by_parent',
                  new_callable=AsyncMock) as mock_get_topics_by_parent:
        mock_get_topics_by_parent.return_value = [
            AsyncMock(id="id_1", titles={"en": "Happiness", "bo": "བདེ་སྐྱིད"}, parent_id=None,
                      default_language="en",has_sub_child=True)
        ]

        response = await get_topics(language="bo",search=None, parent_id=None, hierarchy=True,  skip=0, limit=10)
        assert response == TopicsResponse(parent=None,topics=[TopicModel(id="id_1", title="བདེ་སྐྱིད",has_child=True)], total=1, skip=0,

                                          limit=10)


@pytest.mark.asyncio
async def test_get_topics_pagination():
    with patch('pecha_api.topics.topics_service.get_child_count', return_value=1), \
        patch('pecha_api.topics.topics_service.get_topics_cache', return_value=None), \
        patch('pecha_api.topics.topics_service.set_topics_cache', return_value=None), \
            patch('pecha_api.topics.topics_service.get_topics_by_parent',
                  new_callable=AsyncMock) as mock_get_topics_by_parent, \
            patch('pecha_api.config.get', return_value="en"):
        mock_get_topics_by_parent.return_value = [
            AsyncMock(id="id_1", titles={"en": "Happiness", "bo": "བདེ་སྐྱིད།"}, parent_id=None,
                      default_language="en",has_sub_child=True)
        ]

        response = await get_topics(language=None, search=None,parent_id=None,hierarchy=True,  skip=0, limit=1)
        assert response == TopicsResponse(parent=None,topics=[TopicModel(id="id_1", title="Happiness",has_child=True)], total=1, skip=0,

                                          limit=1)


@pytest.mark.asyncio
async def test_create_new_topic_success():
    with patch('pecha_api.topics.topics_service.verify_admin_access', return_value=True), \
            patch('pecha_api.topics.topics_service.create_topic',
                  new_callable=AsyncMock) as mock_create_topic, \
            patch('pecha_api.config.get', return_value="en"):
        mock_create_topic.return_value = AsyncMock(id="id_1", titles={"en": "Happiness", "bo": "བདེ་སྐྱིད།"}, parent_id=None,
                      default_language="en",has_sub_child=False)
        create_topic_request = CreateTopicRequest(titles={"en": "Happiness", "bo": "བདེ་སྐྱིད།"}, parent_id=None,
                                                  default_language="en")
        response = await create_new_topic(create_topic_request=create_topic_request, token="valid_token", language=None)

        assert response == TopicModel(id="id_1", title="Happiness",has_child=False)



@pytest.mark.asyncio
async def test_create_new_topic_forbidden():
    with patch('pecha_api.topics.topics_service.verify_admin_access', return_value=False):

        create_topic_request = CreateTopicRequest(titles={"en": "Happiness", "bo": "བདེ་སྐྱིད།"}, parent_id=None,
                                              default_language="en")
        with pytest.raises(HTTPException) as excinfo:
            await create_new_topic(create_topic_request=create_topic_request, token="invalid_token", language=None)
        assert excinfo.value.status_code == 403
        assert excinfo.value.detail == "Admin access required"

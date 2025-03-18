from unittest.mock import AsyncMock, patch

import pytest
from pecha_api.texts.texts_service import create_new_text
from pecha_api.texts.texts_response_models import CreateTextRequest, TextModel, Text
from pecha_api.texts.texts_service import get_texts_by_category


@pytest.mark.asyncio
async def test_get_text_by_category():
    mock_texts_by_category = [
                {
                    "id": "uuid.v4",
                    "title": "The Way of the Bodhisattva",
                    "language": "en",
                    "type": "root_text",
                    "is_published": True,
                    "created_date": "2021-09-01T00:00:00.000Z",
                    "updated_date": "2021-09-01T00:00:00.000Z",
                    "published_date": "2021-09-01T00:00:00.000Z",
                    "published_by": "buddhist_tab"
                },
                {
                    "id": "uuid.v4",
                    "title": "Commentary on the difficult points of The Way of Bodhisattvas",
                    "language": "en",
                    "type": "commentary",
                    "is_published": True,
                    "created_date": "2021-09-01T00:00:00.000Z",
                    "updated_date": "2021-09-01T00:00:00.000Z",
                    "published_date": "2021-09-01T00:00:00.000Z",
                    "published_by": "buddhist_tab"
                },
                {
                    "id": "uuid.v4",
                    "title": "Khenpo Kunpel's commentary on the Bodhicaryavatara",
                    "language": "en",
                    "type": "commentary",
                    "is_published": True,
                    "created_date": "2021-09-01T00:00:00.000Z",
                    "updated_date": "2021-09-01T00:00:00.000Z",
                    "published_date": "2021-09-01T00:00:00.000Z",
                    "published_by": "buddhist_tab"
                }
            ]
    with patch('pecha_api.texts.texts_service.get_texts_by_category', new_callable=AsyncMock) as mock_get_texts_by_category:
        mock_get_texts_by_category.return_value = mock_texts_by_category
    response = await get_texts_by_category(category="bod", language="en", skip=0, limit=10)
    text_list = [
        Text(
            id=text["id"],
            title=text["title"],
            language=text["language"],
            type=text["type"],
            is_published=text["is_published"],
            created_date=text["created_date"],
            updated_date=text["updated_date"],
            published_date=text["published_date"],
            published_by=text["published_by"]
        )
        for text in response
    ]
    assert text_list == [
        Text(
            id="uuid.v4",
            title="The Way of the Bodhisattva",
            language="en",
            type="root_text",
            is_published=True,
            created_date="2021-09-01T00:00:00.000Z",
            updated_date="2021-09-01T00:00:00.000Z",
            published_date="2021-09-01T00:00:00.000Z",
            published_by="buddhist_tab"
        ),
        Text(
            id="uuid.v4",
            title="Commentary on the difficult points of The Way of Bodhisattvas",
            language="en",
            type="commentary",
            is_published=True,
            created_date="2021-09-01T00:00:00.000Z",
            updated_date="2021-09-01T00:00:00.000Z",
            published_date="2021-09-01T00:00:00.000Z",
            published_by="buddhist_tab"
        ),
        Text(
            id="uuid.v4",
            title="Khenpo Kunpel's commentary on the Bodhicaryavatara",
            language="en",
            type="commentary",
            is_published=True,
            created_date="2021-09-01T00:00:00.000Z",
            updated_date="2021-09-01T00:00:00.000Z",
            published_date="2021-09-01T00:00:00.000Z",
            published_by="buddhist_tab"
        )
    ]


@pytest.mark.asyncio
async def test_create_new_root_text():
    with patch('pecha_api.texts.texts_service.verify_admin_access', return_value=True), \
        patch('pecha_api.texts.texts_service.create_text', new_callable=AsyncMock) as mock_create_text:
        mock_create_text.return_value = AsyncMock(id="efb26a06-f373-450b-ba57-e7a8d4dd5b64", title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།", language="bo", parent_id=None, is_published=True, \
                                                 created_date="2025-03-16 04:40:54.757652", updated_date="2025-03-16 04:40:54.757652", published_date="2025-03-16 04:40:54.757652", \
                                                 published_by="pecha", type="root_text", categories=[])
        response = await create_new_text(
            create_text_request=CreateTextRequest(
                title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
                language="bo",
                parent_id=None,
                published_by="pecha",
                type="root_text",
                categories=[]
            ),
            token="admin"
        )
        assert response == TextModel(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
            language="bo",
            type="root_text",
            is_published=True,
            created_date="2025-03-16 04:40:54.757652",
            updated_date="2025-03-16 04:40:54.757652",
            published_date="2025-03-16 04:40:54.757652",
            published_by="pecha",
            categories=[],
            parent_id=None
        )
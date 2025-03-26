from unittest.mock import AsyncMock, patch
import uuid

from pecha_api.terms.terms_response_models import TermsModel
import pytest
from pecha_api.texts.texts_service import create_new_text
from pecha_api.texts.texts_response_models import CreateTextRequest, TextModel, Text
from pecha_api.texts.texts_service import get_text_by_term_or_category, TextsCategoryResponse

@pytest.mark.asyncio
async def test_get_text_by_category():
    mock_term = AsyncMock(id="id_1", titles={"bo": "སྤྱོད་འཇུག"}, descriptions={"bo": "དུས་རབས་ ༨ པའི་ནང་སློབ་དཔོན་ཞི་བ་ལྷས་མཛད་པའི་རྩ་བ་དང་དེའི་འགྲེལ་བ་སོགས།"}, slug="bodhicaryavatara", has_sub_child=False)
    mock_texts_by_category = [
                Text(
                    id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
                    title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
                    language="bo",
                    type="root_text",
                    is_published=True,
                    created_date="2025-03-20 09:26:16.571522",
                    updated_date="2025-03-20 09:26:16.571532",
                    published_date="2025-03-20 09:26:16.571536",
                    published_by="pecha"
                ),
                Text(
                    id="a48c0814-ce56-4ada-af31-f74b179b52a9",
                    title="སྤྱོད་འཇུག་དཀའ་འགྲེལ།",
                    language="bo",
                    type="commentary",
                    is_published=True,
                    created_date="2025-03-21 09:40:34.025024",
                    updated_date="2025-03-21 09:40:34.025035",
                    published_date="2025-03-21 09:40:34.025038",
                    published_by="pecha"
                ),
                Text(
                    id="3111b8b4-d14a-4644-b99b-24fb5723c9f4",
                    title="སྤྱོད་འཇུག་དོན་བསྡུས།",
                    language="bo",
                    type="commentary",
                    is_published=True,
                    created_date="2025-03-21 09:41:11.276584",
                    updated_date="2025-03-21 09:41:11.276595",
                    published_date="2025-03-21 09:41:11.276599",
                    published_by="pecha"
                )
            ]
        
    with patch('pecha_api.texts.texts_service.get_texts_by_category', new_callable=AsyncMock) as mock_get_texts_by_category, \
        patch('pecha_api.terms.terms_service.get_term_by_id', new_callable=AsyncMock) as mock_get_term:
        mock_get_texts_by_category.return_value = mock_texts_by_category
        mock_get_term.return_value = mock_term
        response = await get_text_by_term_or_category(text_id="", category="id_1", language="bo", skip=0, limit=10)
        assert response == TextsCategoryResponse(
            category=TermsModel(
                id="id_1",
                title="སྤྱོད་འཇུག",
                description="དུས་རབས་ ༨ པའི་ནང་སློབ་དཔོན་ཞི་བ་ལྷས་མཛད་པའི་རྩ་བ་དང་དེའི་འགྲེལ་བ་སོགས།",
                has_child=False,
                slug="bodhicaryavatara"
            ),
            texts=[
                    Text(
                    id=str(text.id),
                    title=text.title,
                    language=text.language,
                    type=text.type,
                    is_published=text.is_published,
                    created_date=text.created_date,
                    updated_date=text.updated_date,
                    published_date=text.published_date,
                    published_by=text.published_by
                )
                for text in mock_texts_by_category
            ],
            total=len(mock_texts_by_category),
            skip=0,
            limit=10
        )


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
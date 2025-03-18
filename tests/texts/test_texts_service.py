from unittest.mock import AsyncMock, patch

import pytest
from pecha_api.texts.texts_service import create_new_text
from pecha_api.texts.texts_response_models import CreateTextRequest, TextModel

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
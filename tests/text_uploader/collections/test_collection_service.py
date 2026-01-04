import pytest
from unittest.mock import AsyncMock, patch

from pecha_api.text_uploader.collections.collection_service import CollectionService
from pecha_api.text_uploader.constants import COLLECTION_LANGUAGES


@pytest.mark.asyncio
@pytest.mark.parametrize("parent_id", [None, "parent_1"])
async def test_get_collections_service_delegates_to_repository(parent_id: str | None):
    expected = [{"language": "en", "collections": [{"id": "c1"}]}]

    with patch(
        "pecha_api.text_uploader.collections.collection_service.get_collections",
        new_callable=AsyncMock,
        return_value=expected,
    ) as mock_get_collections:
        service = CollectionService()

        result = await service.get_collections_service(
            openpecha_api_url="https://openpecha.example",
            parent_id=parent_id,
        )

        assert result == expected
        mock_get_collections.assert_awaited_once_with(
            openpecha_api_url="https://openpecha.example",
            languages=COLLECTION_LANGUAGES,
            parent_id=parent_id,
        )



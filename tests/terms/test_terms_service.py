import pytest
from unittest.mock import patch, AsyncMock

from starlette import status

from pecha_api.collections.collections_service import get_all_collections, create_new_collection, update_existing_collection, delete_existing_collection
from pecha_api.collections.collections_response_models import CollectionModel, CollectionsResponse, CreateCollectionRequest, UpdateCollectionRequest
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_get_all_collections():
    with patch("pecha_api.collections.collections_service.verify_admin_access", return_value=True), \
            patch("pecha_api.collections.collections_service.get_collections_by_parent",
                  new_callable=AsyncMock) as mock_get_collections_by_parent, \
            patch("pecha_api.collections.collections_service.get_child_count", new_callable=AsyncMock, return_value=2):
        mock_get_collections_by_parent.return_value = [
            AsyncMock(id="id_1", titles={"en": "Term 1"}, slug="collection-1",parent_id=None, has_sub_child=False),
            AsyncMock(id="id_2", titles={"en": "Term 2"}, descriptions={"en": "Description 2"}, slug="collection-2",parent_id=None,has_sub_child=False)
        ]
        response = await get_all_collections(language="en",parent_id=None,skip=0,limit=10)
        assert isinstance(response, CollectionsResponse)
        assert len(response.collections) == 2
        assert response.collections[0].title == "Term 1"
        assert response.collections[1].has_child == False


@pytest.mark.asyncio
async def test_create_new_collection():
    with patch("pecha_api.collections.collections_service.verify_admin_access", return_value=True), \
            patch("pecha_api.collections.collections_service.create_collection", new_callable=AsyncMock) as mock_create_collection:
        mock_create_collection.return_value = AsyncMock(titles={"en": "New Term"}, descriptions={"en": "New Description"}, slug="new-collection",parent_id=None,has_sub_child=False)
        create_collection_request = CreateCollectionRequest(slug="new-collection", titles={"en": "New Term"}, descriptions={"en": "New Description"},parent_id=None)
        response = await create_new_collection(
            create_collection_request=create_collection_request,
            token="valid_token",
            language="en"
        )
        assert isinstance(response, CollectionModel)
        assert response.title == "New Term"
        assert response.slug == "new-collection"
        assert response.description == "New Description"
        assert response.has_child == False


@pytest.mark.asyncio
async def test_update_existing_collection():
    with patch("pecha_api.collections.collections_service.verify_admin_access", return_value=True), \
            patch("pecha_api.collections.collections_service.update_collection_titles",
                  new_callable=AsyncMock) as mock_update_collection_titles:
        mock_update_collection_titles.return_value = AsyncMock(titles={"en": "Updated Term"}, descriptions={"en": "Description 1"}, slug="updated-collection",parent_id=None)
        update_collection_request = UpdateCollectionRequest(titles={"en": "Updated Term"}, descriptions={"en": "New Description"})
        response = await update_existing_collection(collection_id="1", update_collection_request=update_collection_request, token="valid_token",
                                              language="en")
        assert isinstance(response, TermsModel)
        assert response.title == "Updated Term"


@pytest.mark.asyncio
async def test_delete_existing_collection():
    with patch("pecha_api.collections.collections_service.verify_admin_access", return_value=True), \
            patch("pecha_api.collections.collections_service.delete_collection", new_callable=AsyncMock) as mock_delete_collection:
        mock_delete_collection.return_value = "id_1"
        response = await delete_existing_collection(collection_id="id_1", token="valid_token")
        assert response == "id_1"


@pytest.mark.asyncio
async def test_create_new_collection_unauthorized():
    with patch("pecha_api.collections.collections_service.verify_admin_access", return_value=False):
        create_collection_request = CreateCollectionRequest(slug="new-collection", titles={"en": "New Term"},descriptions={"en": "New Description"},parent_id=None)
        try:
            await create_new_collection(create_collection_request=create_collection_request, token="invalid_token", language="en")
        except HTTPException as e:
            assert e.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
@patch("pecha_api.collections.collections_service.verify_admin_access", return_value=False)
async def test_update_existing_collection_unauthorized(mock_verify_admin_access):
    update_collection_request = UpdateCollectionRequest(titles={"en": "Updated Term"}, descriptions={"en": "Updated Descriptions"})
    try:
        await update_existing_collection(collection_id="1", update_collection_request=update_collection_request, token="invalid_token",
                                   language=None)
    except HTTPException as e:
        assert e.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
@patch("pecha_api.collections.collections_service.verify_admin_access", return_value=False)
async def test_delete_existing_collection_unauthorized(mock_verify_admin_access):
    try:
        await delete_existing_collection(collection_id="1", token="invalid_token")
    except HTTPException as e:
        assert e.status_code == status.HTTP_403_FORBIDDEN

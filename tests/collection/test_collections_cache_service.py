import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from pecha_api.collections.collections_cache_service import (
    get_collections_cache,
    set_collections_cache,
    get_collection_detail_cache,
    set_collection_detail_cache,
    delete_collection_cache
)
from pecha_api.collections.collections_response_models import (
    CollectionsResponse,
    CollectionModel,
    Pagination
)
from pecha_api.cache.cache_enums import CacheType


@pytest.mark.asyncio
async def test_get_collections_cache_empty_cache():
    #Test get_collections_cache when cache is empty/None.
    with patch("pecha_api.collections.collections_cache_service.get_cache_data", new_callable=AsyncMock, return_value=None):
        
        response = await get_collections_cache(
            parent_id="parent_id", 
            language="en", 
            skip=0, 
            limit=10, 
            cache_type=CacheType.COLLECTIONS
        )

        assert response is None


@pytest.mark.asyncio
async def test_get_collections_cache_success():
    #Test get_collections_cache when cache returns valid CollectionsResponse object.
    mock_collection = CollectionModel(
        id="collection_id",
        title="Test Collection",
        description="Test Description",
        language="en",
        slug="test-collection",
        has_child=False
    )
    
    mock_pagination = Pagination(total=1, skip=0, limit=10)
    
    mock_collections_response = CollectionsResponse(
        parent=None,
        pagination=mock_pagination,
        collections=[mock_collection]
    )

    with patch("pecha_api.collections.collections_cache_service.get_cache_data", new_callable=AsyncMock, return_value=mock_collections_response):
        
        response = await get_collections_cache(
            parent_id="parent_id", 
            language="en", 
            skip=0, 
            limit=10, 
            cache_type=CacheType.COLLECTIONS
        )

        assert response is not None
        assert isinstance(response, CollectionsResponse)
        assert len(response.collections) == 1
        assert response.collections[0].id == "collection_id"
        assert response.pagination.total == 1


@pytest.mark.asyncio
async def test_get_collections_cache_with_dict_response():
    #Test get_collections_cache when cache returns dict and needs conversion.
    mock_cache_dict = {
        "parent": None,
        "pagination": {"total": 1, "skip": 0, "limit": 10},
        "collections": [{
            "id": "collection_id",
            "title": "Test Collection",
            "description": "Test Description",
            "language": "en",
            "slug": "test-collection",
            "has_child": False
        }]
    }

    with patch("pecha_api.collections.collections_cache_service.get_cache_data", new_callable=AsyncMock, return_value=mock_cache_dict):
        
        response = await get_collections_cache(
            parent_id="parent_id", 
            language="en", 
            skip=0, 
            limit=10, 
            cache_type=CacheType.COLLECTIONS
        )

        assert response is not None
        assert isinstance(response, CollectionsResponse)
        assert len(response.collections) == 1
        assert response.collections[0].id == "collection_id"


@pytest.mark.asyncio
async def test_set_collections_cache_success():
    #Test set_collections_cache successfully sets cache.
    mock_collection = CollectionModel(
        id="collection_id",
        title="Test Collection",
        description="Test Description",
        language="en",
        slug="test-collection",
        has_child=False
    )
    
    mock_pagination = Pagination(total=1, skip=0, limit=10)
    
    mock_collections_response = CollectionsResponse(
        parent=None,
        pagination=mock_pagination,
        collections=[mock_collection]
    )

    with patch("pecha_api.collections.collections_cache_service.set_cache", new_callable=AsyncMock) as mock_set_cache, \
         patch("pecha_api.collections.collections_cache_service.config.get_int", return_value=1800) as mock_config:
        
        await set_collections_cache(
            parent_id="parent_id", 
            language="en", 
            skip=0, 
            limit=10, 
            data=mock_collections_response, 
            cache_type=CacheType.COLLECTIONS
        )

        mock_set_cache.assert_called_once()
        mock_config.assert_called_once_with("CACHE_COLLECTION_TIMEOUT")
        
        # Verify the call arguments
        call_args = mock_set_cache.call_args
        assert "hash_key" in call_args.kwargs
        assert call_args.kwargs["value"] == mock_collections_response
        assert call_args.kwargs["cache_time_out"] == 1800


@pytest.mark.asyncio
async def test_get_collection_detail_cache_empty_cache():
    #Test get_collection_detail_cache when cache is empty/None.
    with patch("pecha_api.collections.collections_cache_service.get_cache_data", new_callable=AsyncMock, return_value=None):
        
        response = await get_collection_detail_cache(
            collection_id="collection_id", 
            language="en", 
            cache_type=CacheType.COLLECTION_DETAIL
        )

        assert response is None


@pytest.mark.asyncio
async def test_get_collection_detail_cache_success():
    #Test get_collection_detail_cache when cache returns valid CollectionModel object.
    mock_collection = CollectionModel(
        id="collection_id",
        title="Test Collection",
        description="Test Description",
        language="en",
        slug="test-collection",
        has_child=True
    )

    with patch("pecha_api.collections.collections_cache_service.get_cache_data", new_callable=AsyncMock, return_value=mock_collection):
        
        response = await get_collection_detail_cache(
            collection_id="collection_id", 
            language="en", 
            cache_type=CacheType.COLLECTION_DETAIL
        )

        assert response is not None
        assert isinstance(response, CollectionModel)
        assert response.id == "collection_id"
        assert response.title == "Test Collection"
        assert response.has_child is True


@pytest.mark.asyncio
async def test_get_collection_detail_cache_with_dict_response():
    #Test get_collection_detail_cache when cache returns dict and needs conversion.
    mock_cache_dict = {
        "id": "collection_id",
        "title": "Test Collection",
        "description": "Test Description",
        "language": "en",
        "slug": "test-collection",
        "has_child": True
    }

    with patch("pecha_api.collections.collections_cache_service.get_cache_data", new_callable=AsyncMock, return_value=mock_cache_dict):
        
        response = await get_collection_detail_cache(
            collection_id="collection_id", 
            language="en", 
            cache_type=CacheType.COLLECTION_DETAIL
        )

        assert response is not None
        assert isinstance(response, CollectionModel)
        assert response.id == "collection_id"
        assert response.has_child is True


@pytest.mark.asyncio
async def test_set_collection_detail_cache_success():
    #Test set_collection_detail_cache successfully sets cache.
    mock_collection = CollectionModel(
        id="collection_id",
        title="Test Collection",
        description="Test Description",
        language="en",
        slug="test-collection",
        has_child=False
    )

    with patch("pecha_api.collections.collections_cache_service.set_cache", new_callable=AsyncMock) as mock_set_cache, \
         patch("pecha_api.collections.collections_cache_service.config.get_int", return_value=1800) as mock_config:
        
        await set_collection_detail_cache(
            collection_id="collection_id", 
            language="en", 
            data=mock_collection, 
            cache_type=CacheType.COLLECTION_DETAIL
        )

        mock_set_cache.assert_called_once()
        mock_config.assert_called_once_with("CACHE_COLLECTION_TIMEOUT")
        
        # Verify the call arguments
        call_args = mock_set_cache.call_args
        assert "hash_key" in call_args.kwargs
        assert call_args.kwargs["value"] == mock_collection
        assert call_args.kwargs["cache_time_out"] == 1800


@pytest.mark.asyncio
async def test_delete_collection_cache_success():
    #Test delete_collection_cache successfully clears cache.
    with patch("pecha_api.collections.collections_cache_service.clear_cache", new_callable=AsyncMock) as mock_clear_cache:
        
        await delete_collection_cache(
            collection_id="collection_id", 
            cache_type=CacheType.COLLECTION_DETAIL
        )

        mock_clear_cache.assert_called_once()
        
        # Verify the call arguments
        call_args = mock_clear_cache.call_args
        assert "hash_key" in call_args.kwargs


@pytest.mark.asyncio
async def test_get_collections_cache_hash_key_generation():
    #Test that correct hash key is generated for get_collections_cache.
    with patch("pecha_api.collections.collections_cache_service.get_cache_data", new_callable=AsyncMock, return_value=None) as mock_get_cache, \
         patch("pecha_api.collections.collections_cache_service.Utils.generate_hash_key", return_value="test_hash_key") as mock_generate_hash:
        
        await get_collections_cache(
            parent_id="parent_id", 
            language="en", 
            skip=0, 
            limit=10, 
            cache_type=CacheType.COLLECTIONS
        )

        mock_generate_hash.assert_called_once_with(payload=["parent_id", "en", 0, 10, CacheType.COLLECTIONS])
        mock_get_cache.assert_called_once_with(hash_key="test_hash_key")


@pytest.mark.asyncio
async def test_get_collection_detail_cache_hash_key_generation():
    #Test that correct hash key is generated for get_collection_detail_cache.
    with patch("pecha_api.collections.collections_cache_service.get_cache_data", new_callable=AsyncMock, return_value=None) as mock_get_cache, \
         patch("pecha_api.collections.collections_cache_service.Utils.generate_hash_key", return_value="test_hash_key") as mock_generate_hash:
        
        await get_collection_detail_cache(
            collection_id="collection_id", 
            language="en", 
            cache_type=CacheType.COLLECTION_DETAIL
        )

        mock_generate_hash.assert_called_once_with(payload=["collection_id", "en", CacheType.COLLECTION_DETAIL])
        mock_get_cache.assert_called_once_with(hash_key="test_hash_key")


@pytest.mark.asyncio
async def test_delete_collection_cache_hash_key_generation():
    #Test that correct hash key is generated for delete_collection_cache.
    with patch("pecha_api.collections.collections_cache_service.clear_cache", new_callable=AsyncMock) as mock_clear_cache, \
         patch("pecha_api.collections.collections_cache_service.Utils.generate_hash_key", return_value="test_hash_key") as mock_generate_hash:
        
        await delete_collection_cache(
            collection_id="collection_id", 
            cache_type=CacheType.COLLECTION_DETAIL
        )

        mock_generate_hash.assert_called_once_with(payload=["collection_id", CacheType.COLLECTION_DETAIL])
        mock_clear_cache.assert_called_once_with(hash_key="test_hash_key")


@pytest.mark.asyncio
async def test_collections_cache_with_none_parameters():
    #Test cache functions work correctly with None parameters.
    with patch("pecha_api.collections.collections_cache_service.get_cache_data", new_callable=AsyncMock, return_value=None) as mock_get_cache, \
         patch("pecha_api.collections.collections_cache_service.Utils.generate_hash_key", return_value="test_hash_key") as mock_generate_hash:
        
        # Test with None values
        await get_collections_cache(
            parent_id=None, 
            language=None, 
            skip=None, 
            limit=None, 
            cache_type=None
        )

        mock_generate_hash.assert_called_once_with(payload=[None, None, None, None, None])
        mock_get_cache.assert_called_once_with(hash_key="test_hash_key")


@pytest.mark.asyncio
async def test_set_collections_cache_with_none_data():
    #Test set_collections_cache handles None data correctly.
    with patch("pecha_api.collections.collections_cache_service.set_cache", new_callable=AsyncMock) as mock_set_cache, \
         patch("pecha_api.collections.collections_cache_service.config.get_int", return_value=1800) as mock_config:
        
        await set_collections_cache(
            parent_id="parent_id", 
            language="en", 
            skip=0, 
            limit=10, 
            data=None, 
            cache_type=CacheType.COLLECTIONS
        )

        mock_set_cache.assert_called_once()
        call_args = mock_set_cache.call_args
        assert call_args.kwargs["value"] is None
        assert call_args.kwargs["cache_time_out"] == 1800


@pytest.mark.asyncio
async def test_set_collection_detail_cache_with_none_data():
    #Test set_collection_detail_cache handles None data correctly.
    with patch("pecha_api.collections.collections_cache_service.set_cache", new_callable=AsyncMock) as mock_set_cache, \
         patch("pecha_api.collections.collections_cache_service.config.get_int", return_value=1800) as mock_config:
        
        await set_collection_detail_cache(
            collection_id="collection_id", 
            language="en", 
            data=None, 
            cache_type=CacheType.COLLECTION_DETAIL
        )

        mock_set_cache.assert_called_once()
        call_args = mock_set_cache.call_args
        assert call_args.kwargs["value"] is None
        assert call_args.kwargs["cache_time_out"] == 1800 
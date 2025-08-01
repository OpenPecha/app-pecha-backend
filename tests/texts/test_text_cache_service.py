import pytest
from unittest.mock import patch, Mock, AsyncMock

from pecha_api.texts.texts_cache_service import (
    get_text_details_cache,
    set_text_details_cache,
    get_text_by_text_id_or_collection_cache,
    set_text_by_text_id_or_collection_cache,
    get_table_of_contents_by_text_id_cache,
    set_table_of_contents_by_text_id_cache,
    get_text_versions_by_group_id_cache,
    set_text_versions_by_group_id_cache
)
from pecha_api.texts.texts_response_models import (
    DetailTableOfContent,
    DetailSection,
    DetailTextSegment,
    TextDTO,
    TableOfContent,
    Section,
    TextVersionResponse,
    TextsCategoryResponse
)
from pecha_api.collections.collections_response_models import CollectionModel

from pecha_api.cache.cache_enums import CacheType

@pytest.mark.asyncio
async def test_get_text_details_cache_empty_cache():
    with patch("pecha_api.texts.texts_cache_service.get_cache_data", new_callable=AsyncMock, return_value=None):
        
        response = await get_text_details_cache(text_id="text_id", content_id="content_id", version_id="version_id", skip=0, limit=10)

        assert response is None

@pytest.mark.asyncio
async def test_set_text_details_cache_success():
    mock_text_detail = DetailTableOfContent(
        id="id_1",
        text_id="text_id_1",
        sections=[
            DetailSection(
                id=f"id_{i}",
                title=f"section_{i}",
                section_number=i,
                parent_id="parent_id_1",
                segments=[
                    DetailTextSegment(
                        segment_id=f"segment_id_{i}",
                        segment_number=1,
                        content=f"content_{i}",
                        translation=None
                    )
                    for i in range(1,6)
                ],
                sections=[],
                created_date="2025-03-16 04:40:54.757652",
                updated_date="2025-03-16 04:40:54.757652",
                published_date="2025-03-16 04:40:54.757652"
            )
            for i in range(1,6)
        ]
    )

    with patch("pecha_api.texts.texts_cache_service.set_cache", new_callable=AsyncMock):

        await set_text_details_cache(text_id="text_id", content_id="content_id", version_id="version_id", skip=0, limit=10, data=mock_text_detail)


@pytest.mark.asyncio
async def test_get_text_details_cache_for_text_details_response():
    mock_cache_data = DetailTableOfContent(
        id="id_1",
        text_id="text_id_1",
        sections=[
            DetailSection(
                id=f"id_{i}",
                title=f"section_{i}",
                section_number=i,
                parent_id="parent_id_1",
                segments=[
                    DetailTextSegment(
                        segment_id=f"segment_id_{i}",
                        segment_number=1,
                        content=f"content_{i}",
                        translation=None
                    )
                    for i in range(1,6)
                ],
                sections=[],
                created_date="2025-03-16 04:40:54.757652",
                updated_date="2025-03-16 04:40:54.757652",
                published_date="2025-03-16 04:40:54.757652"
            )
            for i in range(1,6)
        ]
    )
    with patch("pecha_api.texts.texts_cache_service.get_cache_data", new_callable=AsyncMock, return_value=mock_cache_data):
        response = await get_text_details_cache(text_id="text_id", content_id="content_id", version_id="version_id", skip=0, limit=10)

        assert response is not None
        assert isinstance(response, DetailTableOfContent)
        assert response.id == "id_1"
        assert response.text_id == "text_id_1"
        assert len(response.sections) == 5
        assert response.sections[0].id == "id_1"

@pytest.mark.asyncio
async def test_set_text_details_cache_for_text_details_response():
    mock_cache_data = DetailTableOfContent(
        id="id_1",
        text_id="text_id_1",
        sections=[
            DetailSection(
                id=f"id_{i}",
                title=f"section_{i}",
                section_number=i,
                parent_id="parent_id_1",
                segments=[
                    DetailTextSegment(
                        segment_id=f"segment_id_{i}",
                        segment_number=1,
                        content=f"content_{i}",
                        translation=None
                    )
                    for i in range(1,6)
                ],
                sections=[],
                created_date="2025-03-16 04:40:54.757652",
                updated_date="2025-03-16 04:40:54.757652",
                published_date="2025-03-16 04:40:54.757652"
            )
            for i in range(1,6)
        ]
    )
    with patch("pecha_api.texts.texts_cache_service.set_cache", new_callable=AsyncMock):
        set_text_details_cache(text_id="text_id", content_id="content_id", version_id="version_id", skip=0, limit=10, data=mock_cache_data)

@pytest.mark.asyncio
async def test_get_text_by_text_id_or_collection_cache_empty_cache():
    with patch("pecha_api.texts.texts_cache_service.get_cache_data", new_callable=AsyncMock, return_value=None):
        response = await get_text_by_text_id_or_collection_cache(text_id="text_id", collection_id="collection_id", language="en", skip=0, limit=10)


        assert response is None

@pytest.mark.asyncio
async def test_get_text_by_text_id_or_collection_cache_for_text_by_text_id_or_collection_response():
    mock_cache_data = TextDTO(
        id="id_1",
        title="title_1",
        language="en",
        group_id="group_id_1",
        type="type_1",
        is_published=True,
        created_date="2025-03-16 04:40:54.757652",
        updated_date="2025-03-16 04:40:54.757652",
        published_date="2025-03-16 04:40:54.757652",
        published_by="published_by_1",
        categories=[],
        views=0
    )
    with patch("pecha_api.texts.texts_cache_service.get_cache_data", new_callable=AsyncMock, return_value=mock_cache_data):

        response = await get_text_by_text_id_or_collection_cache(text_id="text_id", collection_id="collection_id", language="en", skip=0, limit=10)


        assert response is not None
        assert isinstance(response, TextDTO)
        assert response.id == "id_1"

@pytest.mark.asyncio
async def test_set_text_by_text_id_or_collection_cache_for_text_by_text_id_or_collection_response():
    mock_cache_data = TextDTO(
        id="id_1",
        title="title_1",
        language="en",
        group_id="group_id_1",
        type="type_1",
        is_published=True,
        created_date="2025-03-16 04:40:54.757652",
        updated_date="2025-03-16 04:40:54.757652",
        published_date="2025-03-16 04:40:54.757652",
        published_by="published_by_1",
        categories=[],
        views=0
    )

    with patch("pecha_api.texts.texts_cache_service.set_text_by_text_id_or_collection_cache", new_callable=AsyncMock):
        set_text_by_text_id_or_collection_cache(text_id="text_id", collection_id="collection_id", language="en", skip=0, limit=10, data=mock_cache_data)

@pytest.mark.asyncio
async def test_get_table_of_contents_by_text_id_cache_empty_cache():
    with patch("pecha_api.texts.texts_cache_service.get_cache_data", new_callable=AsyncMock, return_value=None):
        response = await get_table_of_contents_by_text_id_cache(text_id="text_id")

        assert response is None

@pytest.mark.asyncio
async def test_get_table_of_contents_by_text_id_cache_for_table_of_contents_by_text_id_response():
    mock_cache_data = TableOfContent(
            id="table_of_content_id",
            text_id="text_id_1",
            sections=[
                Section(
                    id="id_1",
                    title="section_1",
                    section_number=1,
                    parent_id="id_1",
                    segments=[],
                    sections=[],
                    created_date="2025-03-16 04:40:54.757652",
                    updated_date="2025-03-16 04:40:54.757652",
                    published_date="2025-03-16 04:40:54.757652"
                )
            ]
        )

    with patch("pecha_api.texts.texts_cache_service.get_cache_data", new_callable=AsyncMock, return_value=mock_cache_data):

        response = await get_table_of_contents_by_text_id_cache(text_id="text_id")
        
        assert response is not None
        assert isinstance(response, TableOfContent)
        assert response.id == "table_of_content_id"
        assert response.text_id == "text_id_1"
        assert len(response.sections) == 1
        assert response.sections[0].id == "id_1"

@pytest.mark.asyncio
async def test_set_table_of_contents_by_text_id_cache_for_table_of_contents_by_text_id_response():
    mock_cache_data = TableOfContent(
            id="table_of_content_id",
            text_id="text_id_1",
            sections=[
                Section(
                    id="id_1",
                    title="section_1",
                    section_number=1,
                    parent_id="id_1",
                    segments=[],
                    sections=[],
                    created_date="2025-03-16 04:40:54.757652",
                    updated_date="2025-03-16 04:40:54.757652",
                    published_date="2025-03-16 04:40:54.757652"
                )
            ]
        )
    with patch("pecha_api.texts.texts_cache_service.set_cache", new_callable=AsyncMock):
        set_table_of_contents_by_text_id_cache(text_id="text_id", data=mock_cache_data)

@pytest.mark.asyncio
async def test_get_text_versions_by_group_id_cache_empty_cache():
    with patch("pecha_api.texts.texts_cache_service.get_cache_data", new_callable=AsyncMock, return_value=None):
        response = await get_text_versions_by_group_id_cache(text_id="text_id", language="en", skip=0, limit=10)

        assert response is None

@pytest.mark.asyncio
async def test_get_text_versions_by_group_id_cache_for_text_versions_by_group_id_response():
    mock_cache_data = TextVersionResponse(
        text=TextDTO(
            id="id_1",
            title="title_1",
            language="en",
            group_id="group_id_1",
            type="type_1",
            is_published=True,
            created_date="2025-03-16 04:40:54.757652",
            updated_date="2025-03-16 04:40:54.757652",
            published_date="2025-03-16 04:40:54.757652",
            published_by="published_by_1",
            categories=[],
            views=0
        ),
        versions=[]
    )
    with patch("pecha_api.texts.texts_cache_service.get_cache_data", new_callable=AsyncMock, return_value=mock_cache_data):
        response = await get_text_versions_by_group_id_cache(text_id="text_id", language="en", skip=0, limit=10)

        assert response is not None
        assert isinstance(response, TextVersionResponse)

@pytest.mark.asyncio
async def test_set_text_versions_by_group_id_cache_for_text_versions_by_group_id_response():
    mock_cache_data = TextVersionResponse(
        text=TextDTO(
            id="id_1",
            title="title_1",
            language="en",
            group_id="group_id_1",
            type="type_1",
            is_published=True,
            created_date="2025-03-16 04:40:54.757652",
            updated_date="2025-03-16 04:40:54.757652",
            published_date="2025-03-16 04:40:54.757652",
            published_by="published_by_1",
            categories=[],
            views=0
        ),
        versions=[]
    )
    with patch("pecha_api.texts.texts_cache_service.set_cache", new_callable=AsyncMock):
        set_text_versions_by_group_id_cache(text_id="text_id", language="en", skip=0, limit=10, data=mock_cache_data)


@pytest.mark.asyncio
async def test_set_text_by_text_id_or_collection_cache_success():
    mock_data = TextsCategoryResponse(
        collection=CollectionModel(
            id="id_1",
            title="title_1",
            description="description_1",
            language="en",
            slug="slug_1",
            has_child=False
        ),
        texts=[],
        total=0,
        skip=0,
        limit=10
    )

    with patch("pecha_api.texts.texts_cache_service.set_cache", new_callable=AsyncMock):

        await set_text_by_text_id_or_collection_cache(text_id="text_id", collection_id="collection_id", language="en", skip=0, limit=10, data=mock_data)

@pytest.mark.asyncio
async def test_set_table_of_contents_by_text_id_cache_success():
    mock_cache_data = TableOfContent(
            id="table_of_content_id",
            text_id="text_id_1",
            sections=[
                Section(
                    id="id_1",
                    title="section_1",
                    section_number=1,
                    parent_id="id_1",
                    segments=[],
                    sections=[],
                    created_date="2025-03-16 04:40:54.757652",
                    updated_date="2025-03-16 04:40:54.757652",
                    published_date="2025-03-16 04:40:54.757652"
                )
            ]
        )
    
    with patch("pecha_api.texts.texts_cache_service.set_cache", new_callable=AsyncMock):

        await set_table_of_contents_by_text_id_cache(text_id="text_id", language="en", skip=0, limit=10, data=mock_cache_data)

@pytest.mark.asyncio
async def test_set_text_versions_by_group_id_cache_success():
    mock_cache_data = TextVersionResponse(
        text=TextDTO(
            id="id_1",
            title="title_1",
            language="en",
            group_id="group_id_1",
            type="type_1",
            is_published=True,
            created_date="2025-03-16 04:40:54.757652",
            updated_date="2025-03-16 04:40:54.757652",
            published_date="2025-03-16 04:40:54.757652",
            published_by="published_by_1",
            categories=[],
            views=0
        ),
        versions=[]
    )

    with patch("pecha_api.texts.texts_cache_service.set_cache", new_callable=AsyncMock):

        await set_text_versions_by_group_id_cache(text_id="text_id", language="en", skip=0, limit=10, data=mock_cache_data)


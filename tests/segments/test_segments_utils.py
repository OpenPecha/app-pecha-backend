import pytest
from typing import Union
from unittest.mock import AsyncMock, patch
from uuid import UUID
from uuid import uuid4
from fastapi import HTTPException

from pecha_api.texts.segments.segments_utils import SegmentUtils


from pecha_api.texts.segments.segments_response_models import (
    MappingResponse,
    SegmentDTO,
    SegmentTranslation,
    SegmentCommentry,
    SegmentRootMapping,
    MappedSegmentDTO
)
from pecha_api.texts.texts_response_models import (
    TextDTO,
    DetailTableOfContent,
    Section,
    TextSegment,
    TableOfContent
)
from pecha_api.texts.segments.segments_enum import SegmentType

from pecha_api.texts.groups.groups_response_models import GroupDTO

@pytest.mark.asyncio
async def test_get_count_of_each_commentary_and_version_success():
    text_details = {
        "efb26a06-f373-450b-ba57-e7a8d4dd5b64": TextDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            title="title",
            language="language",
            group_id="group_id",
            type="commentary",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            views=0
        ),
        "efb26a06-f373-450b-ba57-e7a8d4dd5b65": TextDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b65",
            title="title",
            language="language",
            group_id="group_id",
            type="version",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            views=0
        ),
        "efb26a06-f373-450b-ba57-e7a8d4dd5b66": TextDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b66",
            title="title",
            language="language",
            group_id="group_id",
            type="commentary",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            views=0
        )
    }
    list_of_segment_paramenter = [
        SegmentDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            content="content",
            mapping=[],
            type=SegmentType.SOURCE
        ),
        SegmentDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b65",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b65",
            content="content",
            mapping=[],
            type=SegmentType.SOURCE
        ),
        SegmentDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b66",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b66",
            content="content",
            mapping=[],
            type=SegmentType.SOURCE
        )
    ]
    with patch("pecha_api.texts.segments.segments_utils.TextUtils.get_text_details_by_ids", new_callable=AsyncMock, return_value=text_details):
        result = await SegmentUtils.get_count_of_each_commentary_and_version(list_of_segment_paramenter, group_id="group_id")
        assert result["commentary"] == 2
        assert result["version"] == 1

@pytest.mark.asyncio
async def test_filter_segment_mapping_by_type_success():
    """Test filtering segments by commentary type returns correct SegmentCommentry objects."""
    text_details = {
        "efb26a06-f373-450b-ba57-e7a8d4dd5b64": TextDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            title="Commentary One",
            language="bo",
            group_id="group_id",
            type="commentary",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            views=0
        ),
        "efb26a06-f373-450b-ba57-e7a8d4dd5b65": TextDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b65",
            title="Version One",
            language="en",
            group_id="group_id",
            type="version",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            views=0
        ),
        "efb26a06-f373-450b-ba57-e7a8d4dd5b66": TextDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b66",
            title="Commentary Two",
            language="bo",
            group_id="group_id",
            type="commentary",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            views=0
        )
    }
    segments = [
        SegmentDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            content="commentary one content",
            mapping=[],
            type=SegmentType.SOURCE
        ),
        SegmentDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b65",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b65",
            content="version content",
            mapping=[],
            type=SegmentType.SOURCE
        ),
        SegmentDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b66",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b66",
            content="commentary two content",
            mapping=[],
            type=SegmentType.SOURCE
        )
    ]
    with patch("pecha_api.texts.segments.segments_utils.TextUtils.get_text_details_by_ids", new_callable=AsyncMock, return_value=text_details):
        response = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(segments, "commentary")
        
        # Should return 2 commentary results (filtering out the version)
        assert len(response) == 2
        assert isinstance(response[0], SegmentCommentry)
        assert isinstance(response[1], SegmentCommentry)
        
        # Verify first commentary
        assert response[0].text_id == "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
        assert response[0].title == "Commentary One"
        assert response[0].language == "bo"
        assert len(response[0].segments) == 1
        assert response[0].segments[0].segment_id == "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
        assert response[0].segments[0].content == "commentary one content"
        assert response[0].count == 1
        
        # Verify second commentary
        assert response[1].text_id == "efb26a06-f373-450b-ba57-e7a8d4dd5b66"
        assert response[1].title == "Commentary Two"
        assert response[1].language == "bo"
        assert len(response[1].segments) == 1
        assert response[1].segments[0].segment_id == "efb26a06-f373-450b-ba57-e7a8d4dd5b66"
        assert response[1].segments[0].content == "commentary two content"
        assert response[1].count == 1
        
@pytest.mark.asyncio
async def test_get_root_mapping_count_success():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    text_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    group_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b65"
    segment = SegmentDTO(
        id=segment_id,
        text_id=text_id,
        content="content",
        mapping=[
            MappingResponse(
                text_id=f"text_id_{i}",
                segments=[
                    f"segment_id_{i}"
                ]
            )
            for i in range(1,6)
        ],
        type=SegmentType.SOURCE
    )
    text_details = TextDTO(
        id=text_id,
        title="title",
        language="language",
        type="commentary",
        group_id=group_id,
        is_published=True,
        created_date="created_date",
        updated_date="updated_date",
        published_date="published_date",
        published_by="published_by",
        categories=["categories"],
        views=0
    )
    mock_group_details = GroupDTO(
        id=group_id,
        type="COMMENTARY"
    )
    with patch("pecha_api.texts.segments.segments_utils.get_segment_by_id", new_callable=AsyncMock, return_value=segment), \
        patch("pecha_api.texts.segments.segments_utils.TextUtils.get_text_details_by_id", new_callable=AsyncMock, return_value=text_details), \
        patch("pecha_api.texts.segments.segments_utils.get_group_details", new_callable=AsyncMock, return_value=mock_group_details):
        response = await SegmentUtils.get_root_mapping_count(segment_id=segment_id)
        assert response == 5
    
@pytest.mark.asyncio
async def test_get_segment_root_mapping_details_success():
    segments = [
        SegmentDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            text_id="text_id_1",
            content="content",
            mapping=[
                MappingResponse(
                    text_id="text_id_1",
                    segments=[
                        "segment_id_1"
                    ]
                )
            ],
            type=SegmentType.SOURCE
        )
    ]
    text_details = {
        "text_id_1": TextDTO(
            id="text_id_1",
            title="title",
            language="language",
            group_id="group_id",
            type="commentary",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            views=0
        )
    }
    with patch("pecha_api.texts.segments.segments_utils.TextUtils.get_text_details_by_ids", new_callable=AsyncMock, return_value=text_details):
        response = await SegmentUtils.get_segment_root_mapping_details(segments=segments)
        assert isinstance(response[0], SegmentRootMapping)
        assert response[0].text_id == "text_id_1"
        assert response[0].title == "title"
        assert response[0].language == "language"
        assert len(response[0].segments) == 1
        assert response[0].segments[0].segment_id == "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
        assert response[0].segments[0].content == "content"
          
@pytest.mark.asyncio
async def test_mapped_segment_content_for_table_of_content_without_version_id_success():
    table_of_content = TableOfContent(
        id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        text_id="5f3c2e9d-9b7a-4f5e-8e2a-6a8b7c9d4e0f",
        sections=[
            Section(
                id="123e4567-e89b-12d3-a456-426614174000",
                title="title",
                section_number=1,
                parent_id=None,
                segments=[
                    TextSegment(
                        segment_id="anju6a06-f373-a50b-ba57-e7a8d4dd5555",
                        segment_number=1
                    )
                ],
                sections=[],
                created_date="created_date",
                updated_date="updated_date",
                published_date="published_date"
            )
        ]
    )
    segment = SegmentDTO(
        id="anju6a06-f373-a50b-ba57-e7a8d4dd5555",
        text_id="4fae1b8e-9f2b-4d3c-8c6e-3a1b9e4d2f7c",
        content="content",
        mapping=[],
        type=SegmentType.SOURCE
    )
    related_mapped_segments = [
        SegmentDTO(
            id=str(uuid4()),
            text_id=str(uuid4()),
            content="content",
            mapping=[
                MappingResponse(
                    text_id="4fae1b8e-9f2b-4d3c-8c6e-3a1b9e4d2f7c",
                    segments=[
                        "anju6a06-f373-a50b-ba57-e7a8d4dd5555"
                    ]
                )
            ],
            type=SegmentType.SOURCE
        )
    ]
    with patch("pecha_api.texts.segments.segments_utils.get_segment_by_id", new_callable=AsyncMock, return_value=segment), \
        patch("pecha_api.texts.segments.segments_utils.get_related_mapped_segments", new_callable=AsyncMock, return_value=related_mapped_segments):
        response = await SegmentUtils.get_mapped_segment_content_for_table_of_content(table_of_content=table_of_content, version_id=None)
        assert isinstance(response, DetailTableOfContent)
        assert response.text_id == "5f3c2e9d-9b7a-4f5e-8e2a-6a8b7c9d4e0f"
        assert response.sections[0].title == "title"
        assert response.sections[0].section_number == 1
        assert response.sections[0].parent_id is None
        assert response.sections[0].segments[0].segment_id == "anju6a06-f373-a50b-ba57-e7a8d4dd5555"
        assert response.sections[0].segments[0].segment_number == 1
        assert response.sections[0].segments[0].content == "content"


@pytest.mark.asyncio
async def test_validate_segment_exists_invalid_uuid():
    with pytest.raises(HTTPException) as exc_info:
        await SegmentUtils.validate_segment_exists(segment_id="not-a-uuid")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_validate_segments_exists_invalid_uuid_in_list():
    with pytest.raises(HTTPException) as exc_info:
        await SegmentUtils.validate_segments_exists(segment_ids=["valid-uuid-wont-parse", "also-bad"])
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_root_mapping_count_group_type_text_returns_zero():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    text_id = "text-id-1"
    segment = SegmentDTO(
        id=segment_id,
        text_id=text_id,
        content="content",
        mapping=[
            MappingResponse(text_id="t1", segments=["s1", "s2"]),
        ],
        type=SegmentType.SOURCE,
    )
    text_details = TextDTO(
        id=text_id,
        title="title",
        language="en",
        type="commentary",
        group_id="g1",
        is_published=True,
        created_date="",
        updated_date="",
        published_date="",
        published_by="",
        categories=[],
        views=0,
    )
    group_detail = GroupDTO(id="g1", type="text")

    with patch("pecha_api.texts.segments.segments_utils.get_segment_by_id", new_callable=AsyncMock, return_value=segment), \
        patch("pecha_api.texts.segments.segments_utils.TextUtils.get_text_details_by_id", new_callable=AsyncMock, return_value=text_details), \
        patch("pecha_api.texts.segments.segments_utils.get_group_details", new_callable=AsyncMock, return_value=group_detail):
        count = await SegmentUtils.get_root_mapping_count(segment_id)
        assert count == 0


@pytest.mark.asyncio
async def test_filter_segment_mapping_by_type_commentary_merges_same_text_id():
    """
    Test that multiple segments from the same commentary text_id are merged into a single
    SegmentCommentry object with all segments included and correct count.
    """
    text_id = "commentary-text-1"
    segments = [
        SegmentDTO(
            id="seg-1",
            text_id=text_id,
            content="First segment content",
            mapping=[],
            type=SegmentType.SOURCE,
        ),
        SegmentDTO(
            id="seg-2",
            text_id=text_id,
            content="Second segment content",
            mapping=[],
            type=SegmentType.SOURCE,
        ),
    ]
    text_details = {
        text_id: TextDTO(
            id=text_id,
            title="Commentary Title",
            language="bo",
            type="commentary",
            group_id="g1",
            is_published=True,
            created_date="",
            updated_date="",
            published_date="",
            published_by="",
            categories=[],
            views=0,
        )
    }

    with patch("pecha_api.texts.segments.segments_utils.TextUtils.get_text_details_by_ids", new_callable=AsyncMock, return_value=text_details):
        result = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(segments, type="commentary")
        
        # Should return only 1 commentary (merged)
        assert len(result) == 1
        commentary = result[0]
        
        # Verify it's the correct type
        assert isinstance(commentary, SegmentCommentry)
        
        # Verify commentary details
        assert commentary.text_id == text_id
        assert commentary.title == "Commentary Title"
        assert commentary.language == "bo"
        
        # Verify both segments are merged into this commentary
        assert len(commentary.segments) == 2
        assert commentary.count == 2
        
        # Verify first segment
        assert commentary.segments[0].segment_id == "seg-1"
        assert commentary.segments[0].content == "First segment content"
        
        # Verify second segment
        assert commentary.segments[1].segment_id == "seg-2"
        assert commentary.segments[1].content == "Second segment content"


@pytest.mark.asyncio
async def test_filter_segment_mapping_by_type_no_matching_type():
    """Test that filtering returns empty list when no segments match the requested type."""
    text_id = "version-text-1"
    segments = [
        SegmentDTO(
            id="seg-1",
            text_id=text_id,
            content="Version content",
            mapping=[],
            type=SegmentType.SOURCE,
        ),
    ]
    text_details = {
        text_id: TextDTO(
            id=text_id,
            title="Version Title",
            language="en",
            type="version",
            group_id="g1",
            is_published=True,
            created_date="",
            updated_date="",
            published_date="",
            published_by="",
            categories=[],
            views=0,
        )
    }

    with patch("pecha_api.texts.segments.segments_utils.TextUtils.get_text_details_by_ids", new_callable=AsyncMock, return_value=text_details):
        # Request commentary but only version exists
        result = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(segments, type="commentary")
        
        # Should return empty list
        assert len(result) == 0
        assert result == []


@pytest.mark.asyncio
async def test_filter_segment_mapping_by_type_with_text_id_filter():
    """Test filtering by both type and specific text_id."""
    commentary_text_id_1 = "commentary-1"
    commentary_text_id_2 = "commentary-2"
    
    segments = [
        SegmentDTO(
            id="seg-1",
            text_id=commentary_text_id_1,
            content="Commentary 1 content",
            mapping=[],
            type=SegmentType.SOURCE,
        ),
        SegmentDTO(
            id="seg-2",
            text_id=commentary_text_id_2,
            content="Commentary 2 content",
            mapping=[],
            type=SegmentType.SOURCE,
        ),
    ]
    
    text_details = {
        commentary_text_id_1: TextDTO(
            id=commentary_text_id_1,
            title="Commentary One",
            language="bo",
            type="commentary",
            group_id="g1",
            is_published=True,
            created_date="",
            updated_date="",
            published_date="",
            published_by="",
            categories=[],
            views=0,
        ),
        commentary_text_id_2: TextDTO(
            id=commentary_text_id_2,
            title="Commentary Two",
            language="bo",
            type="commentary",
            group_id="g1",
            is_published=True,
            created_date="",
            updated_date="",
            published_date="",
            published_by="",
            categories=[],
            views=0,
        )
    }

    with patch("pecha_api.texts.segments.segments_utils.TextUtils.get_text_details_by_ids", new_callable=AsyncMock, return_value=text_details):
        # Filter by commentary type AND specific text_id
        result = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(
            segments, 
            type="commentary",
            text_id=commentary_text_id_1
        )
        
        # Should return only 1 commentary matching the text_id
        assert len(result) == 1
        assert isinstance(result[0], SegmentCommentry)
        assert result[0].text_id == commentary_text_id_1
        assert result[0].title == "Commentary One"
        assert len(result[0].segments) == 1
        assert result[0].segments[0].segment_id == "seg-1"


@pytest.mark.asyncio
async def test_filter_segment_mapping_by_type_multiple_segments_same_text_grouped():
    """Test that multiple segments from same text_id are properly grouped with correct count."""
    text_id = "commentary-grouped"
    
    segments = [
        SegmentDTO(
            id="seg-1",
            text_id=text_id,
            content="Content 1",
            mapping=[],
            type=SegmentType.SOURCE,
        ),
        SegmentDTO(
            id="seg-2",
            text_id=text_id,
            content="Content 2",
            mapping=[],
            type=SegmentType.SOURCE,
        ),
        SegmentDTO(
            id="seg-3",
            text_id=text_id,
            content="Content 3",
            mapping=[],
            type=SegmentType.SOURCE,
        ),
    ]
    
    text_details = {
        text_id: TextDTO(
            id=text_id,
            title="Grouped Commentary",
            language="bo",
            type="commentary",
            group_id="g1",
            is_published=True,
            created_date="",
            updated_date="",
            published_date="",
            published_by="",
            categories=[],
            views=0,
        )
    }

    with patch("pecha_api.texts.segments.segments_utils.TextUtils.get_text_details_by_ids", new_callable=AsyncMock, return_value=text_details):
        result = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(segments, type="commentary")
        
        # Should return 1 grouped commentary
        assert len(result) == 1
        commentary = result[0]
        
        # Verify all 3 segments are in the commentary
        assert len(commentary.segments) == 3
        assert commentary.count == 3
        
        # Verify segment IDs and content
        assert commentary.segments[0].segment_id == "seg-1"
        assert commentary.segments[0].content == "Content 1"
        assert commentary.segments[1].segment_id == "seg-2"
        assert commentary.segments[1].content == "Content 2"
        assert commentary.segments[2].segment_id == "seg-3"
        assert commentary.segments[2].content == "Content 3"


@pytest.mark.asyncio
async def test_mapped_segment_content_for_table_of_content_with_version_id_success():
    table_of_content = TableOfContent(
        id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        text_id="5f3c2e9d-9b7a-4f5e-8e2a-6a8b7c9d4e0f",
        sections=[
            Section(
                id="123e4567-e89b-12d3-a456-426614174000",
                title="title",
                section_number=1,
                parent_id=None,
                segments=[
                    TextSegment(
                        segment_id="root-seg-1",
                        segment_number=1
                    )
                ],
                sections=[],
                created_date="created_date",
                updated_date="updated_date",
                published_date="published_date"
            )
        ]
    )
    version_id = "version-text-1"

    # Root/source segment content
    root_segment = SegmentDTO(
        id="root-seg-1",
        text_id="root-text-1",
        content="source content",
        mapping=[],
        type=SegmentType.SOURCE
    )

    # Related mapped segments include a version mapped to the root segment
    related_mapped_segments = [
        SegmentDTO(
            id=str(uuid4()),
            text_id=version_id,
            content="translated content",
            mapping=[],
            type=SegmentType.SOURCE
        )
    ]

    # Text details for the version (used by filter and for language)
    version_text_detail = TextDTO(
        id=version_id,
        title="Version Title",
        language="en",
        type="version",
        group_id="group-id",
        is_published=True,
        created_date="created_date",
        updated_date="updated_date",
        published_date="published_date",
        published_by="published_by",
        categories=["cat"],
        views=0
    )

    with patch("pecha_api.texts.segments.segments_utils.get_segment_by_id", new_callable=AsyncMock, return_value=root_segment), \
        patch("pecha_api.texts.segments.segments_utils.get_related_mapped_segments", new_callable=AsyncMock, return_value=related_mapped_segments), \
        patch("pecha_api.texts.segments.segments_utils.TextUtils.get_text_details_by_ids", new_callable=AsyncMock, return_value={version_id: version_text_detail}), \
        patch("pecha_api.texts.segments.segments_utils.TextUtils.get_text_details_by_id", new_callable=AsyncMock, return_value=version_text_detail):
        response = await SegmentUtils.get_mapped_segment_content_for_table_of_content(table_of_content=table_of_content, version_id=version_id)

        assert isinstance(response, DetailTableOfContent)
        seg = response.sections[0].segments[0]
        assert seg.segment_id == "root-seg-1"
        assert seg.content == "source content"
        assert seg.translation is not None
        assert seg.translation.text_id == version_id
        assert seg.translation.language == "en"
        assert seg.translation.content == "translated content"


@pytest.mark.asyncio
async def test_validate_segment_exists_not_found_raises_404():
    with patch("pecha_api.texts.segments.segments_utils.check_segment_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await SegmentUtils.validate_segment_exists(segment_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64")
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_validate_segment_exists_success():
    with patch("pecha_api.texts.segments.segments_utils.check_segment_exists", new_callable=AsyncMock, return_value=True):
        assert await SegmentUtils.validate_segment_exists(segment_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64") is True


@pytest.mark.asyncio
async def test_validate_segments_exists_not_found_raises_404():
    with patch("pecha_api.texts.segments.segments_utils.check_all_segment_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await SegmentUtils.validate_segments_exists(segment_ids=[
                "efb26a06-f373-450b-ba57-e7a8d4dd5b64",
                "efb26a06-f373-450b-ba57-e7a8d4dd5b65",
            ])
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_validate_segments_exists_success():
    with patch("pecha_api.texts.segments.segments_utils.check_all_segment_exists", new_callable=AsyncMock, return_value=True):
        assert await SegmentUtils.validate_segments_exists(segment_ids=[
            "efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            "efb26a06-f373-450b-ba57-e7a8d4dd5b65",
        ]) is True


def test_apply_bophono_with_tibetan_text():
    """Test apply_bophono with Tibetan text input."""
    from unittest.mock import Mock
    
    # Mock the tokenizer and its tokens
    mock_token1 = type('Token', (), {'text': 'བཀྲ་ཤིས་'})()
    mock_token2 = type('Token', (), {'text': 'བདེ་ལེགས་'})()
    mock_tokens = [mock_token1, mock_token2]
    
    # Mock the converter
    mock_converter = Mock()
    mock_converter.get_api.side_effect = ['tra.shi', 'de.legs']
    
    with patch("pecha_api.texts.segments.segments_utils.WordTokenizer") as mock_tokenizer_class, \
         patch("pecha_api.texts.segments.segments_utils.bophono.UnicodeToApi") as mock_converter_class:
        
        # Setup mocks
        mock_tokenizer = Mock()
        mock_tokenizer.tokenize.return_value = mock_tokens
        mock_tokenizer_class.return_value = mock_tokenizer
        mock_converter_class.return_value = mock_converter
        
        # Test the method
        result = SegmentUtils.apply_bophono("བཀྲ་ཤིས་བདེ་ལེགས་")
        
        # Verify the result
        assert result == "tra.shi de.legs"
        
        # Verify method calls
        mock_tokenizer.tokenize.assert_called_once_with("བཀྲ་ཤིས་བདེ་ལེགས་")
        mock_converter_class.assert_called_once_with(schema="KVP", options={'aspirateLowTones': True})
        assert mock_converter.get_api.call_count == 2
        mock_converter.get_api.assert_any_call('བཀྲ་ཤིས་')
        mock_converter.get_api.assert_any_call('བདེ་ལེགས་')


def test_apply_bophono_with_empty_string():
    """Test apply_bophono with empty string input."""
    from unittest.mock import Mock
    
    mock_tokenizer = Mock()
    mock_tokenizer.tokenize.return_value = []
    mock_converter = Mock()
    
    with patch("pecha_api.texts.segments.segments_utils.WordTokenizer") as mock_tokenizer_class, \
         patch("pecha_api.texts.segments.segments_utils.bophono.UnicodeToApi") as mock_converter_class:
        
        mock_tokenizer_class.return_value = mock_tokenizer
        mock_converter_class.return_value = mock_converter
        
        result = SegmentUtils.apply_bophono("")
        
        assert result == ""
        mock_tokenizer.tokenize.assert_called_once_with("")
        mock_converter_class.assert_called_once_with(schema="KVP", options={'aspirateLowTones': True})
        mock_converter.get_api.assert_not_called()


def test_apply_bophono_with_single_word():
    """Test apply_bophono with single Tibetan word."""
    from unittest.mock import Mock
    
    mock_token = type('Token', (), {'text': 'ཨོཾ'})()
    mock_tokens = [mock_token]
    
    mock_tokenizer = Mock()
    mock_tokenizer.tokenize.return_value = mock_tokens
    mock_converter = Mock()
    mock_converter.get_api.return_value = 'om'
    
    with patch("pecha_api.texts.segments.segments_utils.WordTokenizer") as mock_tokenizer_class, \
         patch("pecha_api.texts.segments.segments_utils.bophono.UnicodeToApi") as mock_converter_class:
        
        mock_tokenizer_class.return_value = mock_tokenizer
        mock_converter_class.return_value = mock_converter
        
        result = SegmentUtils.apply_bophono("ཨོཾ")
        
        assert result == "om"
        mock_tokenizer.tokenize.assert_called_once_with("ཨོཾ")
        mock_converter.get_api.assert_called_once_with('ཨོཾ')


def test_apply_bophono_with_mixed_content():
    """Test apply_bophono with mixed Tibetan and punctuation."""
    from unittest.mock import Mock
    
    mock_token1 = type('Token', (), {'text': 'མཆོད་'})()
    mock_token2 = type('Token', (), {'text': '།'})()
    mock_token3 = type('Token', (), {'text': 'རྟེན་'})()
    mock_tokens = [mock_token1, mock_token2, mock_token3]
    
    mock_tokenizer = Mock()
    mock_tokenizer.tokenize.return_value = mock_tokens
    mock_converter = Mock()
    mock_converter.get_api.side_effect = ['chö', '།', 'ten']
    
    with patch("pecha_api.texts.segments.segments_utils.WordTokenizer") as mock_tokenizer_class, \
         patch("pecha_api.texts.segments.segments_utils.bophono.UnicodeToApi") as mock_converter_class:
        
        mock_tokenizer_class.return_value = mock_tokenizer
        mock_converter_class.return_value = mock_converter
        
        result = SegmentUtils.apply_bophono("མཆོད་། རྟེན་")
        
        assert result == "chö ། ten"
        mock_tokenizer.tokenize.assert_called_once_with("མཆོད་། རྟེན་")
        assert mock_converter.get_api.call_count == 3
        mock_converter.get_api.assert_any_call('མཆོད་')
        mock_converter.get_api.assert_any_call('།')
        mock_converter.get_api.assert_any_call('རྟེན་')


def test_apply_bophono_converter_options():
    """Test that apply_bophono uses correct converter options."""
    from unittest.mock import Mock
    
    mock_token = type('Token', (), {'text': 'དཀར་'})()
    mock_tokens = [mock_token]
    
    mock_tokenizer = Mock()
    mock_tokenizer.tokenize.return_value = mock_tokens
    mock_converter = Mock()
    mock_converter.get_api.return_value = 'kar'
    
    with patch("pecha_api.texts.segments.segments_utils.WordTokenizer") as mock_tokenizer_class, \
         patch("pecha_api.texts.segments.segments_utils.bophono.UnicodeToApi") as mock_converter_class:
        
        mock_tokenizer_class.return_value = mock_tokenizer
        mock_converter_class.return_value = mock_converter
        
        SegmentUtils.apply_bophono("དཀར་")
        
        # Verify that the converter was initialized with correct options
        mock_converter_class.assert_called_once_with(
            schema="KVP", 
            options={'aspirateLowTones': True}
        )


def test_apply_bophono_with_whitespace_only():
    """Test apply_bophono with whitespace-only input."""
    from unittest.mock import Mock
    
    mock_tokenizer = Mock()
    mock_tokenizer.tokenize.return_value = []
    mock_converter = Mock()
    
    with patch("pecha_api.texts.segments.segments_utils.WordTokenizer") as mock_tokenizer_class, \
         patch("pecha_api.texts.segments.segments_utils.bophono.UnicodeToApi") as mock_converter_class:
        
        mock_tokenizer_class.return_value = mock_tokenizer
        mock_converter_class.return_value = mock_converter
        
        result = SegmentUtils.apply_bophono("   ")
        
        assert result == ""
        mock_tokenizer.tokenize.assert_called_once_with("   ")
        mock_converter.get_api.assert_not_called()
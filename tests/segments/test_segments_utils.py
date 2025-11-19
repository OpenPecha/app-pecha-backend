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
        result = await SegmentUtils.get_count_of_each_commentary_and_version(list_of_segment_paramenter)
        assert result["commentary"] == 2
        assert result["version"] == 1

@pytest.mark.asyncio
async def test_filter_segment_mapping_by_type_success():
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
        response = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(list_of_segment_paramenter, "commentary")
        assert isinstance(response[0], SegmentCommentry)
        assert len(response) == 2
        assert response[0].text_id == "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
        assert response[0].title == "title"
        assert len(response[0].segments) == 1
        assert response[0].segments[0].segment_id == "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
        assert response[0].segments[0].content == "content"
        assert response[0].language == "language"
        assert response[0].count == 1
        
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
    segment = SegmentDTO(
        id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
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
    with patch("pecha_api.texts.segments.segments_utils.TextUtils.get_text_details_by_ids", new_callable=AsyncMock, return_value=text_details), \
        patch("pecha_api.texts.segments.segments_utils.get_segment_by_id", new_callable=AsyncMock, return_value=segment):
        response = await SegmentUtils.get_segment_root_mapping_details(segment=segment)
        assert isinstance(response[0], SegmentRootMapping)
        assert response[0].text_id == "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
        assert response[0].segment_id == "segment_id_1"
        assert response[0].title == "title"
        assert response[0].content == "content"
        assert response[0].language == "language"
          
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
    # two segments from same commentary text should merge content and increment count
    text_id = "commentary-text-1"
    segments = [
        SegmentDTO(
            id="seg-1",
            text_id=text_id,
            content="c1",
            mapping=[],
            type=SegmentType.SOURCE,
        ),
        SegmentDTO(
            id="seg-2",
            text_id=text_id,
            content="c2",
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
        assert len(result) == 1
        commentary = result[0]
        assert isinstance(commentary, SegmentCommentry)
        assert commentary.text_id == text_id
        assert commentary.title == "Commentary Title"
        assert commentary.language == "bo"
        assert len(commentary.segments) == 2
        assert commentary.segments[0].segment_id == "seg-1"
        assert commentary.segments[0].content == "c1"
        assert commentary.segments[1].segment_id == "seg-2"
        assert commentary.segments[1].content == "c2"
        assert commentary.count == 2

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
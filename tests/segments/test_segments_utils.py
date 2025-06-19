import pytest
from typing import Union
from unittest.mock import AsyncMock, patch
from uuid import UUID
from uuid import uuid4

from pecha_api.texts.segments.segments_utils import SegmentUtils


from pecha_api.texts.segments.segments_response_models import (
    MappingResponse,
    SegmentDTO,
    SegmentTranslation,
    SegmentCommentry,
    SegmentRootMapping
)
from pecha_api.texts.texts_response_models import (
    TextDTO,
    DetailTableOfContent,
    Section,
    TextSegment,
    TableOfContent
)
from pecha_api.texts.groups.groups_response_models import GroupDTO

@pytest.mark.asyncio
async def test_get_count_of_each_commentary_and_version_success():
    text_details = {
        "efb26a06-f373-450b-ba57-e7a8d4dd5b64": TextDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            title="title",
            language="language",
            type="commentary",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            parent_id="parent_id"
        ),
        "efb26a06-f373-450b-ba57-e7a8d4dd5b65": TextDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b65",
            title="title",
            language="language",
            type="version",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            parent_id="parent_id"
        ),
        "efb26a06-f373-450b-ba57-e7a8d4dd5b66": TextDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b66",
            title="title",
            language="language",
            type="commentary",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            parent_id="parent_id"
        )
    }
    list_of_segment_paramenter = [
        SegmentDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            content="content",
            mapping=[]
        ),
        SegmentDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b65",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b65",
            content="content",
            mapping=[]
        ),
        SegmentDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b66",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b66",
            content="content",
            mapping=[]
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
            type="commentary",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            parent_id="parent_id"
        ),
        "efb26a06-f373-450b-ba57-e7a8d4dd5b65": TextDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b65",
            title="title",
            language="language",
            type="version",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            parent_id="parent_id"
        ),
        "efb26a06-f373-450b-ba57-e7a8d4dd5b66": TextDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b66",
            title="title",
            language="language",
            type="commentary",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            parent_id="parent_id"
        )
    }
    list_of_segment_paramenter = [
        SegmentDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            content="content",
            mapping=[]
        ),
        SegmentDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b65",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b65",
            content="content",
            mapping=[]
        ),
        SegmentDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b66",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b66",
            content="content",
            mapping=[]
        )
    ]
    with patch("pecha_api.texts.segments.segments_utils.TextUtils.get_text_details_by_ids", new_callable=AsyncMock, return_value=text_details):
        response = await SegmentUtils.filter_segment_mapping_by_type_or_text_id(list_of_segment_paramenter, "commentary")
        assert isinstance(response[0], Union[SegmentCommentry, SegmentTranslation])
        assert response[0].text_id == "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
        assert response[0].title == "title"
        assert response[0].content == "content"
        assert response[0].language == "language"
        
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
        ]
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
        parent_id="parent_id"
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
        ]
    )  
    text_details = {
        "text_id_1": TextDTO(
            id="text_id_1",
            title="title",
            language="language",
            type="commentary",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            parent_id="parent_id"
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
        mapping=[]
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
            ]
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
import pytest
from typing import Union
from unittest.mock import AsyncMock, patch
from pecha_api.texts.segments.segments_utils import SegmentUtils

from pecha_api.texts.segments.segments_response_models import (
    MappingResponse,
    SegmentDTO,
    SegmentTranslation,
    SegmentCommentry
)
from pecha_api.texts.texts_response_models import (
    TextModel
)

@pytest.mark.asyncio
async def test_get_count_of_each_commentary_and_version_success():
    text_details = {
        "efb26a06-f373-450b-ba57-e7a8d4dd5b64": TextModel(
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
        "efb26a06-f373-450b-ba57-e7a8d4dd5b65": TextModel(
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
        "efb26a06-f373-450b-ba57-e7a8d4dd5b66": TextModel(
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
        "efb26a06-f373-450b-ba57-e7a8d4dd5b64": TextModel(
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
        "efb26a06-f373-450b-ba57-e7a8d4dd5b65": TextModel(
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
        "efb26a06-f373-450b-ba57-e7a8d4dd5b66": TextModel(
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
    segment = SegmentDTO(
        id=segment_id,
        text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
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
    with patch("pecha_api.texts.segments.segments_utils.get_segment_by_id", new_callable=AsyncMock, return_value=segment):
        response = await SegmentUtils.get_root_mapping_count(segment_id=segment_id)
        assert response == 5
    
        

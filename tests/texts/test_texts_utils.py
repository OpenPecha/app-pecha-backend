import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from pecha_api.texts.texts_utils import TextUtils
from pecha_api.error_contants import ErrorConstants

from pecha_api.texts.texts_response_models import (
    TextModel,
    TableOfContent,
    Section,
    TextSegment
)


@pytest.mark.asyncio
async def test_get_text_details_by_ids_success():
    text_details_dict = {
        "efb26a06-f373-450b-ba57-e7a8d4dd5b64": TextModel(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            title="title",
            language="language",
            type="type",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            parent_id="parent_id"
        )
    }
    with patch("pecha_api.texts.texts_utils.get_texts_by_ids", new_callable=AsyncMock, return_value=text_details_dict):
        response = await TextUtils.get_text_details_by_ids(text_ids=["efb26a06-f373-450b-ba57-e7a8d4dd5b64"])
        assert response.get("efb26a06-f373-450b-ba57-e7a8d4dd5b64") == text_details_dict.get("efb26a06-f373-450b-ba57-e7a8d4dd5b64")

@pytest.mark.asyncio
async def test_get_text_details_by_id_success():
    text_details = TextModel(
        id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        title="title",
        language="language",
        type="type",
        is_published=True,
        created_date="created_date",
        updated_date="updated_date",
        published_date="published_date",
        published_by="published_by",
        categories=["categories"],
        parent_id="parent_id"
    )
    with patch("pecha_api.texts.texts_utils.get_texts_by_id", new_callable=AsyncMock, return_value=text_details):
        response = await TextUtils.get_text_details_by_id(text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64")
        assert response.id == "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
        assert response.title == "title"
        assert response.language == "language"
        assert response.type == "type"
        assert response.is_published == True
        assert response.categories == ["categories"]
        assert response.parent_id == "parent_id"
        
@pytest.mark.asyncio
async def test_validate_text_exists_success():
    text_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch("pecha_api.texts.texts_utils.check_text_exists", new_callable=AsyncMock, return_value=True):
        response = await TextUtils.validate_text_exists(text_id=text_id)
        assert response == True

@pytest.mark.asyncio
async def test_validate_text_exists_invalid_text_id():
    text_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch("pecha_api.texts.texts_utils.check_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await TextUtils.validate_text_exists(text_id=text_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE
        
@pytest.mark.asyncio
async def test_validate_texts_exist_success():
    text_ids = ["efb26a06-f373-450b-ba57-e7a8d4dd5b64", "efb26a06-f373-450b-ba57-e7a8d4dd5b65"]
    with patch("pecha_api.texts.texts_utils.check_all_text_exists", new_callable=AsyncMock, return_value=True):
        response = await TextUtils.validate_texts_exist(text_ids=text_ids)
        assert response == True
        
@pytest.mark.asyncio
async def test_validate_texts_exist_invalid_text_id():
    text_ids = ["efb26a06-f373-450b-ba57-e7a8d4dd5b64", "efb26a06-f373-450b-ba57-e7a8d4dd5b65"]
    with patch("pecha_api.texts.texts_utils.check_all_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await TextUtils.validate_texts_exist(text_ids=text_ids)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_get_text_detail_by_id_success():
    text_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    text = TextModel(
        id=text_id,
        title="title",
        language="language",
        parent_id="parent_id",
        type="type",
        is_published=True,
        created_date="created_date",
        updated_date="updated_date",
        published_date="published_date",
        published_by="published_by",
        categories=["categories"]
    )
    with patch("pecha_api.texts.texts_utils.get_texts_by_id", new_callable=AsyncMock, return_value=text):
        response = await TextUtils.get_text_detail_by_id(text_id=text_id)
        assert response.id == text_id
        assert response.title == "title"
        assert response.language == "language"
        assert response.parent_id == "parent_id"
        assert response.type == "type"
        assert response.is_published == True
        assert response.created_date == "created_date"
        assert response.updated_date == "updated_date"
        assert response.published_date == "published_date"
        assert response.published_by == "published_by"
        assert response.categories == ["categories"]

@pytest.mark.asyncio
async def test_get_text_detail_by_id_empty_text_id():
    text_id = None
    with pytest.raises(HTTPException) as exc_info:
        await TextUtils.get_text_detail_by_id(text_id=text_id)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == ErrorConstants.TEXT_OR_TERM_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_get_text_detail_by_id_invalid_text_id():
    text_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch("pecha_api.texts.texts_utils.get_texts_by_id", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await TextUtils.get_text_detail_by_id(text_id=text_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_get_table_of_content_id_and_respective_section_by_segment_id_success():
    list_of_table_of_content = [
        TableOfContent(
            id="123e4567-e89b-12d3-a456-426614174000",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            sections=[
                Section(
                    id="123e4567-e89b-12d3-a456-426614174001",
                    title="title",
                    section_number=1,
                    parent_id="123e4567-e89b-12d3-a456-426614174000",
                    segments=[
                        TextSegment(
                            segment_id="123e4567-e89b-12d3-a456-426614174002",
                            segment_number=1
                        )
                    ],
                    created_date="created_date",
                    updated_date="updated_date",
                    published_date="published_date"
                )
            ]
        )
    ]
    with patch("pecha_api.texts.texts_utils.get_contents_by_id", new_callable=AsyncMock, return_value=list_of_table_of_content):
        response = await TextUtils.get_table_of_content_id_and_respective_section_by_segment_id(text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64", segment_id="123e4567-e89b-12d3-a456-426614174002")
        assert isinstance(response, TableOfContent)
        assert response.id == "123e4567-e89b-12d3-a456-426614174000"
        assert response.text_id == "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
        assert response.sections[0].id == "123e4567-e89b-12d3-a456-426614174001"
        assert response.sections[0].title == "title"
        assert response.sections[0].section_number == 1
        assert response.sections[0].parent_id == "123e4567-e89b-12d3-a456-426614174000"
        assert response.sections[0].segments[0].segment_id == "123e4567-e89b-12d3-a456-426614174002"
        assert response.sections[0].segments[0].segment_number == 1


@pytest.mark.asyncio
async def test_get_table_of_content_id_and_respective_section_by_segment_id_where_segment_id_not_found_in_table_of_content():
    list_of_table_of_content = [
        TableOfContent(
            id="123e4567-e89b-12d3-a456-426614174000",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            sections=[
                Section(
                    id="123e4567-e89b-12d3-a456-426614174001",
                    title="title",
                    section_number=1,
                    parent_id="123e4567-e89b-12d3-a456-426614174000",
                    segments=[
                        TextSegment(
                            segment_id="123e4567-e89b-12d3-a456-426614174002",
                            segment_number=1
                        )
                    ],
                    created_date="created_date",
                    updated_date="updated_date",
                    published_date="published_date"
                )
            ]
        )
    ]
    with patch("pecha_api.texts.texts_utils.get_contents_by_id", new_callable=AsyncMock, return_value=list_of_table_of_content):
        response = await TextUtils.get_table_of_content_id_and_respective_section_by_segment_id(text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64", segment_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64")
        assert response is None
        

        
    

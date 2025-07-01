import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from pecha_api.texts.texts_utils import TextUtils
from pecha_api.error_contants import ErrorConstants

from typing import List, Dict, Union

from pecha_api.texts.texts_response_models import (
    TextDTO,
    TableOfContent,
    Section,
    TextSegment
)

from pecha_api.texts.groups.groups_response_models import GroupDTO


@pytest.mark.asyncio
async def test_get_text_details_by_ids_success():
    text_details_dict = {
        "efb26a06-f373-450b-ba57-e7a8d4dd5b64": TextDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            title="title",
            language="language",
            group_id="group_id",
            type="type",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            views=0
        )
    }
    with patch("pecha_api.texts.texts_utils.get_texts_by_ids", new_callable=AsyncMock, return_value=text_details_dict):
        response = await TextUtils.get_text_details_by_ids(text_ids=["efb26a06-f373-450b-ba57-e7a8d4dd5b64"])
        assert response.get("efb26a06-f373-450b-ba57-e7a8d4dd5b64") == text_details_dict.get("efb26a06-f373-450b-ba57-e7a8d4dd5b64")

@pytest.mark.asyncio
async def test_get_text_details_by_id_success():
    text_details = TextDTO(
        id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        title="title",
        language="language",
        group_id="group_id",
        type="type",
        is_published=True,
        created_date="created_date",
        updated_date="updated_date",
        published_date="published_date",
        published_by="published_by",
        categories=["categories"],
        views=0
    )
    with patch("pecha_api.texts.texts_utils.get_texts_by_id", new_callable=AsyncMock, return_value=text_details),\
        patch("pecha_api.texts.texts_utils.check_text_exists", new_callable=AsyncMock, return_value=True):
        response = await TextUtils.get_text_details_by_id(text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64")
        assert response.id == "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
        assert response.title == "title"
        assert response.language == "language"
        assert response.type == "type"
        assert response.is_published == True
        assert response.categories == ["categories"]
        
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
    text = TextDTO(
        id=text_id,
        title="title",
        language="language",
        group_id="group_id",
        type="type",
        is_published=True,
        created_date="created_date",
        updated_date="updated_date",
        published_date="published_date",
        published_by="published_by",
        categories=["categories"],
        views=0
    )
    with patch("pecha_api.texts.texts_utils.get_texts_by_id", new_callable=AsyncMock, return_value=text):
        response = await TextUtils.get_text_detail_by_id(text_id=text_id)
        assert response.id == text_id
        assert response.title == "title"
        assert response.language == "language"
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
        

@pytest.mark.asyncio
async def test_filter_text_on_root_and_version():
    mock_texts: List[TextDTO] = [
        TextDTO(
            id=f"efb26a06-f373-450b-ba57-e7a8d4dd5b6{i}",
            title=f"en_{i}",
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
        )
        for i in range(1,3)
    ]
    mock_texts.append(
        TextDTO(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            title="bo_1",
            language="bo",
            group_id="group_id",
            type="version",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            views=0
        )
    )
    response: Dict[str, Union[TextDTO, List[TextDTO]]] = TextUtils.filter_text_on_root_and_version(texts=mock_texts, language="en")
    assert response is not None
    assert response["root_text"] is not None
    assert isinstance(response["root_text"], TextDTO)
    assert response["root_text"].language == "en"
    assert response["root_text"].id == "efb26a06-f373-450b-ba57-e7a8d4dd5b61"
    assert response["root_text"].title == "en_1"
    assert response["versions"] is not None
    assert len(response["versions"]) == 2
    index = 0
    assert response["versions"][index] is not None
    assert response["versions"][index].language == "en"
    assert response["versions"][index].id == "efb26a06-f373-450b-ba57-e7a8d4dd5b62"
    assert response["versions"][index].title == "en_2"
    
@pytest.mark.asyncio
async def test_filter_text_base_on_group_id_type():
    mock_texts = _generate_mock_texts_version_and_commentary()
    mock_groups = _generate_mock_groups_version_and_commentary(mock_texts=mock_texts)
    with patch("pecha_api.texts.texts_utils.get_groups_by_list_of_ids", new_callable=AsyncMock, return_value=mock_groups):
        response = await TextUtils.filter_text_base_on_group_id_type(texts=mock_texts, language="en")
        response is not None
        assert response["root_text"] is not None
        assert response["root_text"].id == "ce14bedb-a4ca-402f-b7a0-cbb33efe5181"
        assert response["root_text"].language == "en"
        assert response["root_text"].type == "version"
        
        assert response["commentary"] is not None
        assert len(response["commentary"]) == 5
        for text_commentary in response["commentary"]:
            assert text_commentary.type == "commentary"
    


def _generate_mock_texts_version_and_commentary() -> List[TextDTO]:
    mock_commentary_texts: List[TextDTO] = [
        TextDTO(
            id=f"05c36f8b-95cd-4698-bc97-ba4958b2d55{i}",
            title=f"bo_{i}",
            language="bo",
            group_id=f"05c36f8b-95cd-4698-bc97-ba4958b2d55{i}",
            type="commentary",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            views=0
        )
        for i in range(1, 6)
    ]
    mock_version_texts: List[TextDTO] = [
        TextDTO(
            id=f"ce14bedb-a4ca-402f-b7a0-cbb33efe518{i}",
            title=f"en_{i}",
            language="en",
            group_id=f"ce14bedb-a4ca-402f-b7a0-cbb33efe518{i}",
            type="version",
            is_published=True,
            created_date="created_date",
            updated_date="updated_date",
            published_date="published_date",
            published_by="published_by",
            categories=["categories"],
            views=0
        )
        for i in range(1, 3)
    ]
    return mock_commentary_texts + mock_version_texts

def _generate_mock_groups_version_and_commentary(mock_texts: List[TextDTO]) -> Dict[str, GroupDTO]:
    mock_groups: Dict[str, GroupDTO] = {}
    for text in mock_texts:
        mock_groups[text.id] = GroupDTO(
            id=text.group_id,
            type="text" if text.type == "version" else "commentary"
        )
    return mock_groups
    
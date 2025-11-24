import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from pecha_api.texts.texts_utils import TextUtils
from pecha_api.error_contants import ErrorConstants

from typing import List, Dict, Union

from pecha_api.texts.texts_response_models import (
    TextDTO,
    TableOfContent,
    TableOfContentType,
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
            type=TableOfContentType.TEXT,
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
            type=TableOfContentType.TEXT,
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
    response: Dict[str, Union[TextDTO, List[TextDTO]]] = TextUtils.filter_text_on_root_and_version(texts=mock_texts, language="bo")
    assert response is not None
    assert response["root_text"] is not None
    assert isinstance(response["root_text"], TextDTO)
    assert response["root_text"].language == "bo"
    assert response["root_text"].id == "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    assert response["root_text"].title == "bo_1"
    assert response["versions"] is not None
    assert len(response["versions"]) == 2
    index = 0
    assert response["versions"][index] is not None
    assert response["versions"][index].language == "en"
    assert response["versions"][index].id == "efb26a06-f373-450b-ba57-e7a8d4dd5b61"
    
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
        assert len(response["commentary"]) == 0
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


@pytest.mark.asyncio
async def test_get_all_segment_ids_success_flat_structure():
    """Test get_all_segment_ids with a flat structure (no nested sections)"""
    table_of_content = TableOfContent(
        id="toc_id_1",
        text_id="text_id_1",
        type=TableOfContentType.TEXT,
        sections=[
            Section(
                id="section_id_1",
                title="Section 1",
                section_number=1,
                parent_id="toc_id_1",
                segments=[
                    TextSegment(segment_id="segment_id_1", segment_number=1),
                    TextSegment(segment_id="segment_id_2", segment_number=2)
                ],
                created_date="2025-01-01",
                updated_date="2025-01-01",
                published_date="2025-01-01"
            ),
            Section(
                id="section_id_2",
                title="Section 2",
                section_number=2,
                parent_id="toc_id_1",
                segments=[
                    TextSegment(segment_id="segment_id_3", segment_number=1),
                    TextSegment(segment_id="segment_id_4", segment_number=2)
                ],
                created_date="2025-01-01",
                updated_date="2025-01-01",
                published_date="2025-01-01"
            )
        ]
    )
    
    result = TextUtils.get_all_segment_ids(table_of_content=table_of_content)
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 4
    assert "segment_id_1" in result
    assert "segment_id_2" in result
    assert "segment_id_3" in result
    assert "segment_id_4" in result


@pytest.mark.asyncio
async def test_get_all_segment_ids_success_nested_structure():
    """Test get_all_segment_ids with nested sections"""
    table_of_content = TableOfContent(
        id="toc_id_1",
        text_id="text_id_1",
        type=TableOfContentType.TEXT,
        sections=[
            Section(
                id="section_id_1",
                title="Section 1",
                section_number=1,
                parent_id="toc_id_1",
                segments=[
                    TextSegment(segment_id="segment_id_1", segment_number=1),
                    TextSegment(segment_id="segment_id_2", segment_number=2)
                ],
                sections=[
                    Section(
                        id="section_id_1_1",
                        title="Subsection 1.1",
                        section_number=1,
                        parent_id="section_id_1",
                        segments=[
                            TextSegment(segment_id="segment_id_3", segment_number=1),
                            TextSegment(segment_id="segment_id_4", segment_number=2)
                        ],
                        created_date="2025-01-01",
                        updated_date="2025-01-01",
                        published_date="2025-01-01"
                    ),
                    Section(
                        id="section_id_1_2",
                        title="Subsection 1.2",
                        section_number=2,
                        parent_id="section_id_1",
                        segments=[
                            TextSegment(segment_id="segment_id_5", segment_number=1)
                        ],
                        created_date="2025-01-01",
                        updated_date="2025-01-01",
                        published_date="2025-01-01"
                    )
                ],
                created_date="2025-01-01",
                updated_date="2025-01-01",
                published_date="2025-01-01"
            ),
            Section(
                id="section_id_2",
                title="Section 2",
                section_number=2,
                parent_id="toc_id_1",
                segments=[
                    TextSegment(segment_id="segment_id_6", segment_number=1)
                ],
                created_date="2025-01-01",
                updated_date="2025-01-01",
                published_date="2025-01-01"
            )
        ]
    )
    
    result = TextUtils.get_all_segment_ids(table_of_content=table_of_content)
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 6
    assert "segment_id_1" in result
    assert "segment_id_2" in result
    assert "segment_id_3" in result
    assert "segment_id_4" in result
    assert "segment_id_5" in result
    assert "segment_id_6" in result


@pytest.mark.asyncio
async def test_get_all_segment_ids_empty_sections():
    """Test get_all_segment_ids with empty sections"""
    table_of_content = TableOfContent(
        id="toc_id_1",
        text_id="text_id_1",
        type=TableOfContentType.TEXT,
        sections=[]
    )
    
    result = TextUtils.get_all_segment_ids(table_of_content=table_of_content)
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_all_segment_ids_sections_without_segments():
    """Test get_all_segment_ids with sections that have no segments"""
    table_of_content = TableOfContent(
        id="toc_id_1",
        text_id="text_id_1",
        type=TableOfContentType.TEXT,
        sections=[
            Section(
                id="section_id_1",
                title="Section 1",
                section_number=1,
                parent_id="toc_id_1",
                segments=[],
                created_date="2025-01-01",
                updated_date="2025-01-01",
                published_date="2025-01-01"
            )
        ]
    )
    
    result = TextUtils.get_all_segment_ids(table_of_content=table_of_content)
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_commentaries_by_text_type_success():
    """Test get_commentaries_by_text_type returns commentaries successfully"""
    from pecha_api.texts.texts_models import Text
    from pecha_api.texts.texts_enums import TextType
    from uuid import UUID
    
    mock_text_1 = MagicMock(spec=Text)
    mock_text_1.id = UUID("efb26a06-f373-450b-ba57-e7a8d4dd5b61")
    mock_text_1.pecha_text_id = "pecha_1"
    mock_text_1.title = "Commentary 1"
    mock_text_1.language = "bo"
    mock_text_1.group_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b62"
    mock_text_1.type = TextType.COMMENTARY
    mock_text_1.is_published = True
    mock_text_1.created_date = "2025-03-21 09:40:34.025024"
    mock_text_1.updated_date = "2025-03-21 09:40:34.025035"
    mock_text_1.published_date = "2025-03-21 09:40:34.025038"
    mock_text_1.published_by = "pecha"
    mock_text_1.categories = ["category_1"]
    mock_text_1.views = 10
    mock_text_1.source_link = "http://example.com"
    mock_text_1.ranking = 5
    mock_text_1.license = "MIT"
    
    mock_text_2 = MagicMock(spec=Text)
    mock_text_2.id = UUID("efb26a06-f373-450b-ba57-e7a8d4dd5b63")
    mock_text_2.pecha_text_id = "pecha_2"
    mock_text_2.title = "Commentary 2"
    mock_text_2.language = "bo"
    mock_text_2.group_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    mock_text_2.type = TextType.COMMENTARY
    mock_text_2.is_published = True
    mock_text_2.created_date = "2025-03-21 09:40:34.025024"
    mock_text_2.updated_date = "2025-03-21 09:40:34.025035"
    mock_text_2.published_date = "2025-03-21 09:40:34.025038"
    mock_text_2.published_by = "pecha"
    mock_text_2.categories = ["category_2"]
    mock_text_2.views = 20
    mock_text_2.source_link = "http://example2.com"
    mock_text_2.ranking = 4
    mock_text_2.license = "Apache"
    
    mock_find = AsyncMock()
    mock_find.to_list = AsyncMock(return_value=[mock_text_1, mock_text_2])
    
    with patch.object(Text, "find", return_value=mock_find):
        result = await TextUtils.get_commentaries_by_text_type(
            text_type="commentary",
            language="bo",
            skip=0,
            limit=10
        )
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].id == "efb26a06-f373-450b-ba57-e7a8d4dd5b61"
        assert result[0].title == "Commentary 1"
        assert result[0].language == "bo"
        assert result[0].categories == ["category_1"]
        assert result[1].id == "efb26a06-f373-450b-ba57-e7a8d4dd5b63"
        assert result[1].title == "Commentary 2"


@pytest.mark.asyncio
async def test_get_commentaries_by_text_type_empty_result():
    """Test get_commentaries_by_text_type returns empty list when no commentaries found"""
    from pecha_api.texts.texts_models import Text
    
    mock_find = AsyncMock()
    mock_find.to_list = AsyncMock(return_value=[])
    
    with patch.object(Text, "find", return_value=mock_find):
        result = await TextUtils.get_commentaries_by_text_type(
            text_type="commentary",
            language="bo",
            skip=0,
            limit=10
        )
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


@pytest.mark.asyncio
async def test_get_commentaries_by_text_type_with_none_pecha_text_id():
    """Test get_commentaries_by_text_type handles texts with None pecha_text_id"""
    from pecha_api.texts.texts_models import Text
    from pecha_api.texts.texts_enums import TextType
    from uuid import UUID
    
    mock_text = MagicMock(spec=Text)
    mock_text.id = UUID("efb26a06-f373-450b-ba57-e7a8d4dd5b61")
    mock_text.pecha_text_id = None
    mock_text.title = "Commentary Without Pecha ID"
    mock_text.language = "bo"
    mock_text.group_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b62"
    mock_text.type = TextType.COMMENTARY
    mock_text.is_published = True
    mock_text.created_date = "2025-03-21 09:40:34.025024"
    mock_text.updated_date = "2025-03-21 09:40:34.025035"
    mock_text.published_date = "2025-03-21 09:40:34.025038"
    mock_text.published_by = "pecha"
    mock_text.categories = ["category_1"]
    mock_text.views = 5
    mock_text.source_link = "http://example.com"
    mock_text.ranking = 3
    mock_text.license = "MIT"
    
    mock_find = AsyncMock()
    mock_find.to_list = AsyncMock(return_value=[mock_text])
    
    with patch.object(Text, "find", return_value=mock_find):
        result = await TextUtils.get_commentaries_by_text_type(
            text_type="commentary",
            language="bo",
            skip=0,
            limit=10
        )
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].pecha_text_id is None
        assert result[0].title == "Commentary Without Pecha ID"


@pytest.mark.asyncio
async def test_get_text_details_by_id_with_cache():
    """Test get_text_details_by_id returns cached data when available"""
    text_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    cached_text = TextDTO(
        id=text_id,
        title="Cached Text",
        language="bo",
        group_id="group_id",
        type="root_text",
        is_published=True,
        created_date="2025-03-21 09:40:34.025024",
        updated_date="2025-03-21 09:40:34.025035",
        published_date="2025-03-21 09:40:34.025038",
        published_by="pecha",
        categories=["categories"],
        views=100
    )
    
    with patch("pecha_api.texts.texts_utils.get_text_details_by_id_cache", new_callable=AsyncMock, return_value=cached_text):
        result = await TextUtils.get_text_details_by_id(text_id=text_id)
        
        assert result is not None
        assert result.id == text_id
        assert result.title == "Cached Text"
        assert result.views == 100


@pytest.mark.asyncio
async def test_get_text_details_by_id_no_cache_sets_cache():
    """Test get_text_details_by_id fetches from DB and sets cache when no cache exists"""
    text_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    mock_text = TextDTO(
        id=text_id,
        title="Fresh Text",
        language="bo",
        group_id="group_id",
        type="root_text",
        is_published=True,
        created_date="2025-03-21 09:40:34.025024",
        updated_date="2025-03-21 09:40:34.025035",
        published_date="2025-03-21 09:40:34.025038",
        published_by="pecha",
        categories=["categories"],
        views=50
    )
    
    with patch("pecha_api.texts.texts_utils.get_text_details_by_id_cache", new_callable=AsyncMock, return_value=None), \
         patch("pecha_api.texts.texts_utils.check_text_exists", new_callable=AsyncMock, return_value=True), \
         patch("pecha_api.texts.texts_utils.get_texts_by_id", new_callable=AsyncMock, return_value=mock_text), \
         patch("pecha_api.texts.texts_utils.set_text_details_by_id_cache", new_callable=AsyncMock) as mock_set_cache:
        
        result = await TextUtils.get_text_details_by_id(text_id=text_id)
        
        assert result is not None
        assert result.id == text_id
        assert result.title == "Fresh Text"
        mock_set_cache.assert_called_once()


@pytest.mark.asyncio
async def test_get_text_details_by_id_invalid_text_raises_exception():
    """Test get_text_details_by_id raises exception when text doesn't exist"""
    text_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    
    with patch("pecha_api.texts.texts_utils.get_text_details_by_id_cache", new_callable=AsyncMock, return_value=None), \
         patch("pecha_api.texts.texts_utils.check_text_exists", new_callable=AsyncMock, return_value=False):
        
        with pytest.raises(HTTPException) as exc_info:
            await TextUtils.get_text_details_by_id(text_id=text_id)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE


@pytest.mark.asyncio
async def test_get_all_segment_ids_deeply_nested_structure():
    """Test get_all_segment_ids with deeply nested sections (3 levels)"""
    table_of_content = TableOfContent(
        id="toc_id_1",
        text_id="text_id_1",
        type=TableOfContentType.TEXT,
        sections=[
            Section(
                id="section_id_1",
                title="Section 1",
                section_number=1,
                parent_id="toc_id_1",
                segments=[
                    TextSegment(segment_id="segment_id_1", segment_number=1)
                ],
                sections=[
                    Section(
                        id="section_id_1_1",
                        title="Subsection 1.1",
                        section_number=1,
                        parent_id="section_id_1",
                        segments=[
                            TextSegment(segment_id="segment_id_2", segment_number=1)
                        ],
                        sections=[
                            Section(
                                id="section_id_1_1_1",
                                title="Subsubsection 1.1.1",
                                section_number=1,
                                parent_id="section_id_1_1",
                                segments=[
                                    TextSegment(segment_id="segment_id_3", segment_number=1),
                                    TextSegment(segment_id="segment_id_4", segment_number=2)
                                ],
                                created_date="2025-01-01",
                                updated_date="2025-01-01",
                                published_date="2025-01-01"
                            )
                        ],
                        created_date="2025-01-01",
                        updated_date="2025-01-01",
                        published_date="2025-01-01"
                    )
                ],
                created_date="2025-01-01",
                updated_date="2025-01-01",
                published_date="2025-01-01"
            )
        ]
    )
    
    result = TextUtils.get_all_segment_ids(table_of_content=table_of_content)
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 4
    assert "segment_id_1" in result
    assert "segment_id_2" in result
    assert "segment_id_3" in result
    assert "segment_id_4" in result


@pytest.mark.asyncio
async def test_filter_text_base_on_group_id_type_with_commentary():
    """Test filter_text_base_on_group_id_type returns commentaries correctly"""
    mock_text_1 = TextDTO(
        id="text_id_1",
        title="Root Text",
        language="bo",
        group_id="group_id_1",
        type="root_text",
        is_published=True,
        created_date="2025-01-01",
        updated_date="2025-01-01",
        published_date="2025-01-01",
        published_by="pecha",
        categories=[],
        views=0
    )
    
    mock_text_2 = TextDTO(
        id="text_id_2",
        title="Commentary 1",
        language="bo",
        group_id="group_id_2",
        type="commentary",
        is_published=True,
        created_date="2025-01-01",
        updated_date="2025-01-01",
        published_date="2025-01-01",
        published_by="pecha",
        categories=[],
        views=0
    )
    
    mock_text_3 = TextDTO(
        id="text_id_3",
        title="Commentary 2",
        language="bo",
        group_id="group_id_3",
        type="commentary",
        is_published=True,
        created_date="2025-01-01",
        updated_date="2025-01-01",
        published_date="2025-01-01",
        published_by="pecha",
        categories=[],
        views=0
    )
    
    mock_groups = {
        "group_id_1": GroupDTO(id="group_id_1", type="text"),
        "group_id_2": GroupDTO(id="group_id_2", type="commentary"),
        "group_id_3": GroupDTO(id="group_id_3", type="commentary")
    }
    
    with patch("pecha_api.texts.texts_utils.get_groups_by_list_of_ids", new_callable=AsyncMock, return_value=mock_groups):
        result = await TextUtils.filter_text_base_on_group_id_type(
            texts=[mock_text_1, mock_text_2, mock_text_3],
            language="bo"
        )
        
        assert result is not None
        assert result["root_text"] is not None
        assert result["root_text"].id == "text_id_1"
        assert result["commentary"] is not None
        assert len(result["commentary"]) == 2
        assert result["commentary"][0].id == "text_id_2"
        assert result["commentary"][1].id == "text_id_3"


@pytest.mark.asyncio
async def test_filter_text_base_on_group_id_type_fallback_to_bo():
    """Test filter_text_base_on_group_id_type falls back to 'bo' language when requested language not found"""
    mock_text_bo = TextDTO(
        id="text_id_bo",
        title="Tibetan Text",
        language="bo",
        group_id="group_id_1",
        type="root_text",
        is_published=True,
        created_date="2025-01-01",
        updated_date="2025-01-01",
        published_date="2025-01-01",
        published_by="pecha",
        categories=[],
        views=0
    )
    
    mock_text_other = TextDTO(
        id="text_id_other",
        title="Other Language Text",
        language="zh",
        group_id="group_id_1",
        type="root_text",
        is_published=True,
        created_date="2025-01-01",
        updated_date="2025-01-01",
        published_date="2025-01-01",
        published_by="pecha",
        categories=[],
        views=0
    )
    
    mock_groups = {
        "group_id_1": GroupDTO(id="group_id_1", type="text")
    }
    
    with patch("pecha_api.texts.texts_utils.get_groups_by_list_of_ids", new_callable=AsyncMock, return_value=mock_groups):
        result = await TextUtils.filter_text_base_on_group_id_type(
            texts=[mock_text_other, mock_text_bo],
            language="en"
        )
        
        assert result is not None
        assert result["root_text"] is not None
        assert result["root_text"].id == "text_id_bo"
        assert result["root_text"].language == "bo"


@pytest.mark.asyncio
async def test_filter_text_base_on_group_id_type_empty_texts():
    """Test filter_text_base_on_group_id_type with empty texts list"""
    result = await TextUtils.filter_text_base_on_group_id_type(texts=[], language="bo")
    
    assert result is not None
    assert result["root_text"] is None
    assert result["commentary"] == []


@pytest.mark.asyncio
async def test_filter_text_on_root_and_version_no_matching_language():
    """Test filter_text_on_root_and_version when no text matches the requested language"""
    mock_texts = [
        TextDTO(
            id="text_id_1",
            title="Text 1",
            language="en",
            group_id="group_id",
            type="version",
            is_published=True,
            created_date="2025-01-01",
            updated_date="2025-01-01",
            published_date="2025-01-01",
            published_by="pecha",
            categories=[],
            views=0
        ),
        TextDTO(
            id="text_id_2",
            title="Text 2",
            language="zh",
            group_id="group_id",
            type="version",
            is_published=True,
            created_date="2025-01-01",
            updated_date="2025-01-01",
            published_date="2025-01-01",
            published_by="pecha",
            categories=[],
            views=0
        )
    ]
    
    result = TextUtils.filter_text_on_root_and_version(texts=mock_texts, language="bo")
    
    assert result is not None
    assert result["root_text"] is None
    assert result["versions"] is not None
    assert len(result["versions"]) == 2


@pytest.mark.asyncio
async def test_get_table_of_content_id_and_respective_section_by_segment_id_nested_sections():
    """Test get_table_of_content_id_and_respective_section_by_segment_id with nested sections"""
    list_of_table_of_content = [
        TableOfContent(
            id="toc_id_1",
            text_id="text_id_1",
            type=TableOfContentType.TEXT,
            sections=[
                Section(
                    id="section_id_1",
                    title="Section 1",
                    section_number=1,
                    parent_id="toc_id_1",
                    segments=[
                        TextSegment(segment_id="segment_id_1", segment_number=1)
                    ],
                    sections=[
                        Section(
                            id="section_id_1_1",
                            title="Subsection 1.1",
                            section_number=1,
                            parent_id="section_id_1",
                            segments=[
                                TextSegment(segment_id="segment_id_2", segment_number=1)
                            ],
                            created_date="2025-01-01",
                            updated_date="2025-01-01",
                            published_date="2025-01-01"
                        )
                    ],
                    created_date="2025-01-01",
                    updated_date="2025-01-01",
                    published_date="2025-01-01"
                )
            ]
        )
    ]
    
    with patch("pecha_api.texts.texts_utils.get_contents_by_id", new_callable=AsyncMock, return_value=list_of_table_of_content):
        result = await TextUtils.get_table_of_content_id_and_respective_section_by_segment_id(
            text_id="text_id_1",
            segment_id="segment_id_2"
        )
        
        assert result is not None
        assert isinstance(result, TableOfContent)
        assert result.id == "toc_id_1"
        assert result.text_id == "text_id_1"
        assert len(result.sections) == 1
        assert result.sections[0].id == "section_id_1"
    
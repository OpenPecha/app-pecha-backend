from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from pecha_api.terms.terms_response_models import TermsModel
import pytest
from pecha_api.texts.texts_service import (
    create_new_text,
    get_text_versions_by_group_id,
    get_text_by_text_id_or_term,
    create_table_of_content,
    get_table_of_contents_by_text_id,
    get_text_details_by_text_id,
    update_text_details,
    remove_table_of_content_by_text_id,
    delete_text_by_text_id,
    get_sheet
)
from pecha_api.texts.texts_response_models import (
    CreateTextRequest,
    TextDTO,
    TextVersion,
    TableOfContent,
    Section,
    TextSegment,
    TableOfContentResponse,
    TextDetailsRequest,
    DetailTableOfContentResponse,
    DetailTableOfContent,
    DetailSection,
    DetailTextSegment,
    Translation,
    UpdateTextRequest,
    TextDTOResponse
)

from pecha_api.texts.texts_enums import TextType, PaginationDirection

from pecha_api.error_contants import ErrorConstants
from typing import List

@pytest.mark.asyncio
async def test_get_text_by_text_id_or_term_without_term_id_success():
    text_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    term_id = None
    with patch("pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id", new_callable=AsyncMock) as mock_get_text_detail_by_id, \
        patch("pecha_api.texts.texts_service.set_text_by_text_id_or_term_cache", new_callable=MagicMock, return_value=None), \
        patch("pecha_api.texts.texts_service.get_text_by_text_id_or_term_cache", new_callable=MagicMock, return_value=None):
        mock_get_text_detail_by_id.return_value = TextDTO(
            id=text_id,
            title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
            language="bo",
            group_id="group_id_1",
            type="commentary",
            is_published=True,
            created_date="2025-03-21 09:40:34.025024",
            updated_date="2025-03-21 09:40:34.025035",
            published_date="2025-03-21 09:40:34.025038",
            published_by="pecha",
            categories=[],
            views=0
        )

        response = await get_text_by_text_id_or_term(text_id=text_id, term_id=term_id, language=None, skip=0, limit=10)

        assert response is not None
        assert isinstance(response, TextDTO)
        assert response.id == text_id

@pytest.mark.asyncio
async def test_get_text_by_term_id():
    mock_term = AsyncMock(id="id_1", titles={"bo": "སྤྱོད་འཇུག"}, descriptions={
        "bo": "དུས་རབས་ ༨ པའི་ནང་སློབ་དཔོན་ཞི་བ་ལྷས་མཛད་པའི་རྩ་བ་དང་དེའི་འགྲེལ་བ་སོགས།"}, slug="bodhicaryavatara",
                          has_sub_child=False)
    mock_texts_by_category = [
        TextDTO(
            id="a48c0814-ce56-4ada-af31-f74b179b52a9",
            title="སྤྱོད་འཇུག་དཀའ་འགྲེལ།",
            language="bo",
            group_id="group_id_1",
            type="commentary",
            is_published=True,
            created_date="2025-03-21 09:40:34.025024",
            updated_date="2025-03-21 09:40:34.025035",
            published_date="2025-03-21 09:40:34.025038",
            published_by="pecha",
            categories=[],
            views=0
        ),
        TextDTO(
            id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
            title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
            language="bo",
            group_id="group_id_1",
            type="version",
            is_published=True,
            created_date="2025-03-20 09:26:16.571522",
            updated_date="2025-03-20 09:26:16.571532",
            published_date="2025-03-20 09:26:16.571536",
            published_by="pecha",
            categories=[],
            views=0
        )
    ]

    with patch('pecha_api.texts.texts_service.get_texts_by_term', new_callable=AsyncMock) as mock_get_texts_by_category, \
            patch('pecha_api.terms.terms_service.get_term_by_id', new_callable=AsyncMock) as mock_get_term, \
            patch("pecha_api.texts.texts_service.set_text_by_text_id_or_term_cache", new_callable=MagicMock, return_value=None), \
            patch("pecha_api.texts.texts_service.get_text_by_text_id_or_term_cache", new_callable=MagicMock, return_value=None), \
            patch('pecha_api.texts.texts_service.TextUtils.filter_text_base_on_group_id_type', new_callable=AsyncMock) as mock_filter_text_base_on_group_id_type:
        mock_filter_text_base_on_group_id_type.return_value = {"root_text": mock_texts_by_category[1], "commentary": [mock_texts_by_category[0]]}
        mock_get_texts_by_category.return_value = mock_texts_by_category
        mock_get_term.return_value = mock_term
        response = await get_text_by_text_id_or_term(text_id="", term_id="id_1", language="bo", skip=0, limit=10)
        assert response is not None
        assert response.term is not None
        term: TermsModel = response.term
        assert term.id == "id_1"
        assert term.slug == "bodhicaryavatara"
        assert response.texts is not None
        texts: List[TextDTO] = response.texts
        assert len(texts) == 2
        index = 0
        assert texts[index] is not None
        assert isinstance(texts[index], TextDTO)
        assert texts[index].id == mock_texts_by_category[index].id
        assert texts[index].title == mock_texts_by_category[index].title
        assert texts[index].language == mock_texts_by_category[index].language
        assert texts[index].type == mock_texts_by_category[index].type
        assert response.total == 2
        assert response.skip == 0
        assert response.limit == 10


@pytest.mark.asyncio
async def test_get_versions_by_group_id():
    text_detail = TextDTO(
        id="id_1",
        title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
        group_id="group_id_1",
        language="bo",
        type="version",
        is_published=True,
        created_date="2025-03-20 09:26:16.571522",
        updated_date="2025-03-20 09:26:16.571532",
        published_date="2025-03-20 09:26:16.571536",
        published_by="pecha",
        categories=[],
        views=0
    )
    texts_by_group_id = [
        TextDTO(
            id="text_id_1",
            title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
            group_id="group_id_1",
            language="bo",
            type="version",
            is_published=True,
            created_date="2025-03-20 09:26:16.571522",
            updated_date="2025-03-20 09:26:16.571532",
            published_date="2025-03-20 09:26:16.571536",
            published_by="pecha",
            categories=[],
            views=0
        ),
        TextDTO(
            id="text_id_2",
            title="The Way of the Bodhisattva",
            language="en",
            group_id="group_id_1",
            type="version",
            is_published=True,
            created_date="2025-03-20 09:28:28.076920",
            updated_date="2025-03-20 09:28:28.076934",
            published_date="2025-03-20 09:28:28.076938",
            published_by="pecha",
            categories=[],
            views=0
        ),
        TextDTO(
            id="text_id_3",
            title="शबोधिचर्यावतार",
            language="sa",
            group_id="group_id_1",
            type="version",
            is_published=True,
            created_date="2025-03-20 09:29:51.154697",
            updated_date="2025-03-20 09:29:51.154708",
            published_date="2025-03-20 09:29:51.154712",
            published_by="pecha",
            categories=[],
            views=0
        )
    ]
    mock_table_of_content = TableOfContent(
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
    language = "en"
    with patch('pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id', new_callable=AsyncMock) as mock_text_detail, \
        patch("pecha_api.texts.texts_service.get_text_versions_by_group_id_cache", new_callable=MagicMock, return_value=None),\
        patch("pecha_api.texts.texts_service.set_text_versions_by_group_id_cache", new_callable=MagicMock, return_value=None),\
        patch('pecha_api.texts.texts_service.get_texts_by_group_id', new_callable=AsyncMock) as mock_get_texts_by_group_id,\
        patch('pecha_api.texts.texts_service.get_contents_by_id', new_callable=AsyncMock) as mock_get_contents_by_id:
        mock_text_detail.return_value = text_detail
        mock_get_texts_by_group_id.return_value = texts_by_group_id
        mock_get_contents_by_id.return_value = [mock_table_of_content]
        response = await get_text_versions_by_group_id(text_id="id_1",language=language, skip=0, limit=10)
        assert response is not None
        assert response.text is not None
        assert isinstance(response.text, TextDTO)
        assert response.text.type == "version"
        assert response.text.language == language
        assert response.text.id == "text_id_2"
        assert response.versions is not None
        assert len(response.versions) == 2
        assert response.versions[0] is not None
        assert isinstance(response.versions[0], TextVersion)
        assert response.versions[0].id == "text_id_1"
        for version in response.versions:
            assert isinstance(version, TextVersion)
            assert version.type == "version"



@pytest.mark.asyncio
async def test_create_new_text():
    text_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    title = "བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།"
    language = "bo"
    is_published = True
    group_id = "67dd22a8d9f06ab28feedc90"
    created_date = "2025-03-16 04:40:54.757652"
    updated_date = "2025-03-16 04:40:54.757652"
    published_date = "2025-03-16 04:40:54.757652"
    published_by = "pecha"
    type_ = TextType.VERSION
    categories = []
    with patch('pecha_api.texts.texts_service.validate_user_exists', return_value=True), \
            patch('pecha_api.texts.texts_service.create_text', new_callable=AsyncMock) as mock_create_text,\
            patch('pecha_api.texts.texts_service.validate_group_exists', new_callable=AsyncMock) as mock_validate_group_exists:
        mock_create_text.return_value = AsyncMock(
            id=text_id,
            title=title,
            language=language,
            is_published=is_published,
            group_id=group_id,
            created_date=created_date,
            updated_date=updated_date,
            published_date=published_date,
            published_by=published_by,
            type=type_,
            categories=categories,
        )
        mock_validate_group_exists.return_value = True
        response = await create_new_text(
            create_text_request=CreateTextRequest(
                title=title,
                language=language,
                group_id=group_id,
                published_by=published_by,
                type=type_,
                categories=categories
            ),
            token="admin"
        )
        assert response is not None
        assert isinstance(response, TextDTO)
        assert response.id == text_id
        assert response.title == title
        assert response.language == language
        assert response.type == type_.value
        assert response.is_published == is_published
        assert response.created_date == created_date
        assert response.updated_date == updated_date
        assert response.published_date == published_date
        assert response.published_by == published_by
        assert response.categories == categories
    
@pytest.mark.asyncio
async def test_create_new_text_invalid_user():
    with patch("pecha_api.texts.texts_service.validate_user_exists", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await create_new_text(
                create_text_request=CreateTextRequest(
                    title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
                    language="bo",
                    group_id="67dd22a8d9f06ab28feedc90",
                    published_by="pecha",
                    type=TextType.VERSION,
                    categories=[]
                ),
                token="user"
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

@pytest.mark.asyncio
async def test_create_table_of_content_success():
    table_of_content = TableOfContent (
        id="id_1",
        text_id="id_1",
        sections=[
            Section(
                id="id_1",
                title="section_1",
                section_number=1,
                parent_id="id_1",
                segments=[
                    TextSegment(
                        segment_id="id_1", segment_number=1
                    )
                ],
                sections=[],
                created_date="2025-03-16 04:40:54.757652",
                updated_date="2025-03-16 04:40:54.757652",
                published_date="2025-03-16 04:40:54.757652"
            )
        ]
    )

    with patch("pecha_api.texts.texts_service.validate_user_exists", return_value=True), \
            patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock) as mock_validate_text_exists, \
            patch("pecha_api.texts.texts_service.SegmentUtils.validate_segments_exists", new_callable=AsyncMock) as mock_validate_segments_exists, \
            patch("pecha_api.texts.texts_service.create_table_of_content_detail", new_callable=AsyncMock) as mock_create_table_of_content_detail:
        mock_validate_text_exists.return_value = True
        mock_validate_segments_exists.return_value = True
        mock_create_table_of_content_detail.return_value = table_of_content
        response = await create_table_of_content(table_of_content_request=table_of_content, token="admin")
        assert response is not None
        assert isinstance(response, TableOfContent)
        assert response.id == table_of_content.id
        assert response.text_id == table_of_content.text_id
        assert response.sections is not None
        assert len(response.sections) == 1
        assert response.sections[0].id == table_of_content.sections[0].id
        assert response.sections[0].title == table_of_content.sections[0].title
        assert response.sections[0].section_number == table_of_content.sections[0].section_number
        assert response.sections[0].parent_id == table_of_content.sections[0].parent_id
        assert response.sections[0].segments is not None
        assert len(response.sections[0].segments) == 1
        assert response.sections[0].segments[0].segment_id == table_of_content.sections[0].segments[0].segment_id
        assert response.sections[0].segments[0].segment_number == table_of_content.sections[0].segments[0].segment_number
    
@pytest.mark.asyncio
async def test_create_table_of_content_invalid_user():
    with patch("pecha_api.texts.texts_service.validate_user_exists", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await create_table_of_content(table_of_content_request={}, token="user")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

@pytest.mark.asyncio
async def test_create_table_of_content_invalid_text():
    table_of_content = TableOfContent(
        id="id_1",
        text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        sections=[]
    )
    with patch("pecha_api.texts.texts_service.validate_user_exists", return_value=True), \
        patch("pecha_api.texts.texts_utils.check_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await create_table_of_content(table_of_content_request=table_of_content, token="admin")
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_create_table_of_content_invalid_segment():
    table_of_content = TableOfContent(
        id="id_1",
        text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        sections=[]
    )
    segment_ids = [
        "efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        "efb26a06-f373-450b-ba57-e7a8d4dd5b65"
    ]
    with patch("pecha_api.texts.texts_service.validate_user_exists", return_value=True), \
        patch("pecha_api.texts.texts_service.TextUtils.get_all_segment_ids", return_value=segment_ids), \
        patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.segments.segments_utils.check_all_segment_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await create_table_of_content(table_of_content_request=table_of_content, token="admin")
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE
    
@pytest.mark.asyncio
async def test_get_table_of_contents_by_text_id_success():
    text_id = "text_id_1"
    language = "bo"
    skip = 0
    limit = 10

    mock_text_detail = TextDTO(
        id=text_id,
        title="text_1",
        language=language,
        group_id="group_id_1",
        type="version",
        is_published=False,
        created_date="2025-03-16 04:40:54.757652",
        updated_date="2025-03-16 04:40:54.757652",
        published_date="2025-03-16 04:40:54.757652",
        published_by="pecha",
        categories=[],
        views=0
    )
    mock_group_texts = [
        TextDTO(
            id="text_id_1",
            title="text_1",
            language="bo",
            group_id="group_id_1",
            type="version",
            is_published=False,
            created_date="2025-03-16 04:40:54.757652",
            updated_date="2025-03-16 04:40:54.757652",
            published_date="2025-03-16 04:40:54.757652",
            published_by="pecha",
            categories=[],
            views=0
        ),
        TextDTO(
            id="text_id_2",
            title="text_2",
            language="en",
            group_id="group_id_1",
            type="version",
            is_published=False,
            created_date="2025-03-16 04:40:54.757652",
            updated_date="2025-03-16 04:40:54.757652",
            published_date="2025-03-16 04:40:54.757652",
            published_by="pecha",
            categories=[],
            views=0
        )
    ]

    table_of_contents = [
        TableOfContent(
            id="id_1",
            text_id=text_id,
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
    ]

    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.get_table_of_contents_by_text_id_cache", new_callable=MagicMock, return_value=None),\
        patch("pecha_api.texts.texts_service.set_table_of_contents_by_text_id_cache", new_callable=MagicMock, return_value=None),\
        patch("pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id", new_callable=AsyncMock, return_value=mock_text_detail), \
        patch("pecha_api.texts.texts_service.get_texts_by_group_id", new_callable=AsyncMock, return_value=mock_group_texts), \
        patch("pecha_api.texts.texts_service.get_contents_by_id", new_callable=AsyncMock, return_value=table_of_contents):
        
        response = await get_table_of_contents_by_text_id(
            text_id=text_id,
            language=language,
            skip=skip,
            limit=limit
        )
        
        assert response is not None
        assert isinstance(response, TableOfContentResponse)
        assert response.text_detail is not None
        assert isinstance(response.text_detail, TextDTO)
        assert response.text_detail.id == mock_text_detail.id
        assert response.text_detail.language == language
        assert response.contents is not None
        assert len(response.contents) == 1
        assert response.contents[0] is not None
        assert isinstance(response.contents[0], TableOfContent)
        assert response.contents[0].id == table_of_contents[0].id
        assert response.contents[0].text_id == table_of_contents[0].text_id
        assert response.contents[0].sections is not None

@pytest.mark.asyncio
async def test_get_table_of_contents_by_text_id_invalid_text():
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await get_table_of_contents_by_text_id(
                text_id="id_1",
                language="en",
                skip=0,
                limit=10
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE


@pytest.mark.asyncio
async def test_update_text_details_success():
    mock_text_details = TextDTO(
        id="text_id_1",
        title="text_title",
        language="bo",
        group_id="group_id_1",
        type="version",
        is_published=False,
        created_date="created_date",
        updated_date="updated_date",
        published_date="published_date",
        published_by="published_by",
        categories=[],
        views=0
    )
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id", new_callable=AsyncMock) as mock_get_text_detail_by_id, \
        patch("pecha_api.texts.texts_service.update_text_details_by_id", new_callable=AsyncMock, return_value=mock_text_details):
        mock_get_text_detail_by_id.return_value = mock_text_details
        
        response = await update_text_details(text_id="text_id_1", update_text_request=UpdateTextRequest(title="updated_title", is_published=True))
        
        assert response is not None
        assert response.title == "updated_title"
        assert response.is_published == True

@pytest.mark.asyncio
async def test_update_text_details_invalid_text_id():
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exec_info:
            await update_text_details(text_id="invalid_id", update_text_request=UpdateTextRequest(title="updated_title", is_published=True))
        assert exec_info.value.status_code == 404
        assert exec_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE
    
@pytest.mark.asyncio
async def test_delete_table_of_content_success():
    with patch("pecha_api.texts.texts_service.delete_table_of_content_by_text_id", new_callable=AsyncMock), \
        patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True):
        response = await remove_table_of_content_by_text_id(text_id="text_id_1")
        assert response is not None

@pytest.mark.asyncio
async def test_delete_table_of_content_invalid_text_id():
    with patch("pecha_api.texts.texts_service.delete_table_of_content_by_text_id", new_callable=AsyncMock), \
        patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exec_info:
            await remove_table_of_content_by_text_id(text_id="invalid_id")
        assert exec_info.value.status_code == 404
        assert exec_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_delete_text_by_text_id_success():
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.delete_text_by_id", new_callable=AsyncMock):
        response = await delete_text_by_text_id(text_id="text_id_1")
        assert response is None

@pytest.mark.asyncio
async def test_delete_text_by_text_id_invalid_text_id():
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await delete_text_by_text_id(text_id="invalid_text_id")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_get_sheet_success_user_viewing_own_sheets():
    email = "test_user@gmail.com"
    mock_sheets = [
            type("Text", (), {
                "id": f"sheet_id_{i}",
                "title": "Test Sheet",
                "language": "en",
                "group_id": "group_id",
                "type": "sheet",
                "is_published": True if i % 2 == 0 else False,
                "created_date": "2021-01-01",
                "updated_date": "2021-01-01",
                "published_date": "2021-01-01",
                "published_by": email,
                "categories": [],
                "views": 10
            })()
            for i in range(1,11)
        ]
    with patch("pecha_api.texts.texts_service.fetch_sheets_from_db", new_callable=AsyncMock, return_value=mock_sheets):

        response = await get_sheet(published_by=email, is_published=None, sort_by=None, sort_order=None, skip=0, limit=10)

        assert response is not None
        assert len(response) == 10
        for sheet in response:
            assert sheet.published_by == email

@pytest.mark.asyncio
async def test_get_text_details_by_text_id_with_text_id_content_id_segment_id_success():
    text_id = "text_id_1"
    content_id = "content_id_1"
    segment_id = "segment_id_1"
    mock_text_detail = TextDTO(
        id=text_id,
        title="text_title",
        language="bo",
        group_id="group_id_1",
        type="version",
        is_published=False,
        created_date="created_date",
        updated_date="updated_date",
        published_date="published_date",
        published_by="published_by",
        categories=[],
        views=0
    )
    mock_table_of_content = TableOfContent(
        id=content_id,
        text_id=text_id,
        sections=[
            Section(
                id="section_id_1",
                title="section_title",
                section_number=1,
                parent_id="parent_id_1",
                segments=[
                    TextSegment(
                        segment_id="segment_id_1",
                        segment_number=1
                    ),
                    TextSegment(
                        segment_id="segment_id_2",
                        segment_number=2
                    ),
                    TextSegment(
                        segment_id="segment_id_3",
                        segment_number=3
                    )
                ],
                sections=[],
                created_date="created_date",
                updated_date="updated_date",
                published_date="published_date"
            )
        ]
    )
    mock_mapped_table_of_content = DetailTableOfContent(
        id=content_id,
        text_id=text_id,
        sections=[
            DetailSection(
                id="section_id_1",
                title="section_title",
                section_number=1,
                parent_id="parent_id_1",
                segments=[
                    DetailTextSegment(
                        segment_id="segment_id_1",
                        segment_number=1,
                        content="segment_content_1",
                        translation=None
                    ),
                    DetailTextSegment(
                        segment_id="segment_id_2",
                        segment_number=2,
                        content="segment_content_2",
                        translation=None
                    )
                ],
                sections=[],
                created_date="created_date",
                updated_date="updated_date",
                published_date="published_date"
            )
        ]
    )

    with patch("pecha_api.texts.texts_service._validate_text_detail_request", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id", new_callable=AsyncMock, return_value=mock_text_detail), \
        patch("pecha_api.texts.texts_service.get_table_of_content_by_content_id", new_callable=AsyncMock, return_value=mock_table_of_content), \
        patch("pecha_api.texts.texts_service.SegmentUtils.get_mapped_segment_content_for_table_of_content", new_callable=AsyncMock, return_value=mock_mapped_table_of_content):

        response = await get_text_details_by_text_id(
            text_id=text_id,
            text_details_request=TextDetailsRequest(
                content_id=content_id,
                segment_id=segment_id,
                size=2,
                direction=PaginationDirection.NEXT
            )
        )

        assert response is not None
        assert response.text_detail is not None
        assert isinstance(response.text_detail, TextDTO)
        assert response.text_detail.id == mock_text_detail.id
        assert response.content is not None
        assert isinstance(response.content, DetailTableOfContent)
        assert response.content.sections is not None
        assert len(response.content.sections) == 1
        assert response.content.sections[0] is not None
        assert isinstance(response.content.sections[0], DetailSection)
        section = response.content.sections[0]
        assert section.segments is not None
        assert len(section.segments) == 2
        assert section.segments[0].segment_id == "segment_id_1"
        assert section.segments[1].segment_id == "segment_id_2"
        assert response.pagination_direction == PaginationDirection.NEXT

@pytest.mark.asyncio
async def test_get_text_details_by_text_id_with_segment_id_only_success():
    text_id = "text_id_1"
    segment_id = "segment_id_1"
    mock_text_detail = TextDTO(
        id=text_id,
        title="text_title",
        language="bo",
        group_id="group_id_1",
        type="version",
        is_published=False,
        created_date="created_date",
        updated_date="updated_date",
        published_date="published_date",
        published_by="published_by",
        categories=[],
        views=0
    )
    mock_table_of_contents = [
        TableOfContent(
            id=f"content_id_{i}",
            text_id=text_id,
            sections=[
                Section(
                    id="section_id_1",
                    title="section_title",
                    section_number=1,
                    parent_id="parent_id_1",
                    segments=[
                        TextSegment(
                            segment_id=f"segment_id_{i}",
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
        for i in range(1,11)
    ]
    mock_mapped_table_of_contents = DetailTableOfContent(
        id="content_id_1",
        text_id=text_id,
        sections=[
            DetailSection(
                id="section_id_1",
                title="section_title",
                section_number=1,
                parent_id="parent_id_1",
                segments=[
                    DetailTextSegment(
                        segment_id=f"segment_id_1",
                        segment_number=1,
                        content="segment_content_1",
                        translation=None
                    )
                ],
                sections=[],
                created_date="created_date",
                updated_date="updated_date",
                published_date="published_date"
            )
        ]
    )

    with patch("pecha_api.texts.texts_service._validate_text_detail_request", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id", new_callable=AsyncMock, return_value=mock_text_detail), \
        patch("pecha_api.texts.texts_service.get_contents_by_id", new_callable=AsyncMock, return_value=mock_table_of_contents), \
        patch("pecha_api.texts.texts_service.SegmentUtils.get_mapped_segment_content_for_table_of_content", new_callable=AsyncMock, return_value=mock_mapped_table_of_contents):

        response = await get_text_details_by_text_id(
            text_id=text_id,
            text_details_request=TextDetailsRequest(
                segment_id=segment_id,
                size=2,
                direction=PaginationDirection.NEXT
            )
        )

        assert response is not None
        assert response.text_detail is not None
        assert isinstance(response.text_detail, TextDTO)
        assert response.text_detail.id == mock_text_detail.id
        assert response.content is not None
        assert isinstance(response.content, DetailTableOfContent)
        assert response.content.sections is not None
        assert len(response.content.sections) == 1
        assert response.content.sections[0] is not None
        assert isinstance(response.content.sections[0], DetailSection)
        section = response.content.sections[0]
        assert section.segments is not None
        assert len(section.segments) == 1
        assert section.segments[0].segment_id == segment_id
        assert response.pagination_direction == PaginationDirection.NEXT



@pytest.mark.asyncio
async def test_get_text_details_by_text_id_with_content_id_only_success():
    text_id = "text_id_1"
    content_id = "content_id_1"
    mock_text_detail = TextDTO(
        id=text_id,
        title="text_title",
        language="bo",
        group_id="group_id_1",
        type="version",
        is_published=False,
        created_date="created_date",
        updated_date="updated_date",
        published_date="published_date",
        published_by="published_by",
        categories=[],
        views=0
    )
    mock_table_of_contents = [
        TableOfContent(
            id=f"content_id_{i}",
            text_id=text_id,
            sections=[
                Section(
                    id="section_id_1",
                    title="section_title",
                    section_number=1,
                    parent_id="parent_id_1",
                    segments=[
                        TextSegment(
                            segment_id=f"segment_id_{i}",
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
        for i in range(1,11)
    ]
    mock_mapped_table_of_contents = DetailTableOfContent(
        id="content_id_1",
        text_id=text_id,
        sections=[
            DetailSection(
                id="section_id_1",
                title="section_title",
                section_number=1,
                parent_id="parent_id_1",
                segments=[
                    DetailTextSegment(
                        segment_id=f"segment_id_1",
                        segment_number=1,
                        content="segment_content_1",
                        translation=None
                    )
                ],
                sections=[],
                created_date="created_date",
                updated_date="updated_date",
                published_date="published_date"
            )
        ]
    )

    with patch("pecha_api.texts.texts_service._validate_text_detail_request", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id", new_callable=AsyncMock, return_value=mock_text_detail), \
        patch("pecha_api.texts.texts_service.get_contents_by_id", new_callable=AsyncMock, return_value=mock_table_of_contents), \
        patch("pecha_api.texts.texts_service.SegmentUtils.get_mapped_segment_content_for_table_of_content", new_callable=AsyncMock, return_value=mock_mapped_table_of_contents):

        response = await get_text_details_by_text_id(
            text_id=text_id,
            text_details_request=TextDetailsRequest(
                content_id=content_id,
                size=2,
                direction=PaginationDirection.NEXT
            )
        )

        assert response is not None
        assert response.text_detail is not None
        assert isinstance(response.text_detail, TextDTO)
        assert response.text_detail.id == mock_text_detail.id
        assert response.content is not None
        assert isinstance(response.content, DetailTableOfContent)
        assert response.content.id == content_id
        assert response.content.sections is not None
        assert len(response.content.sections) == 1
        assert response.content.sections[0] is not None
        assert isinstance(response.content.sections[0], DetailSection)
        section = response.content.sections[0]
        assert section.segments is not None
        assert len(section.segments) == 1
        assert section.segments[0].segment_id == "segment_id_1"
        assert response.pagination_direction == PaginationDirection.NEXT
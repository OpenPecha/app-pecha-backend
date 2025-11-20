from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from pecha_api.collections.collections_response_models import CollectionModel
import pytest
from pecha_api.texts.texts_service import (
    create_new_text,
    get_text_versions_by_group_id,
    get_text_by_text_id_or_collection,
    create_table_of_content,
    get_table_of_contents_by_text_id,
    get_text_details_by_text_id,
    update_text_details,
    remove_table_of_content_by_text_id,
    delete_text_by_text_id,
    get_sheet,
    get_table_of_content_by_sheet_id,
    _validate_text_detail_request,
    get_root_text_by_collection_id,
    get_commentaries_by_text_id
)
from pecha_api.terms.terms_response_models import TermsModel
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
    TextDTOResponse,
    TextVersionResponse,
    TextsCategoryResponse
)

from pecha_api.texts.texts_enums import TextType, PaginationDirection

from pecha_api.error_contants import ErrorConstants
from typing import List

@pytest.mark.asyncio
async def test_get_text_by_text_id_or_collection_without_collection_id_success():
    text_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    collection_id = None
    with patch("pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id", new_callable=AsyncMock) as mock_get_text_detail_by_id, \
        patch("pecha_api.texts.texts_service.set_text_by_text_id_or_collection_cache", new_callable=AsyncMock, return_value=None), \
        patch("pecha_api.texts.texts_service.get_text_by_text_id_or_collection_cache", new_callable=AsyncMock, return_value=None):
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

        response = await get_text_by_text_id_or_collection(text_id=text_id, collection_id=collection_id)

        assert response is not None
        assert isinstance(response, TextDTO)
        assert response.id == text_id

@pytest.mark.asyncio
async def test_get_text_by_collection_id():
    mock_collection = CollectionModel(
        id="id_1",
        title="སྤྱོད་འཇུག",
        description="དུས་རབས་ ༨ པའི་ནང་སློབ་དཔོན་ཞི་བ་ལྷས་མཛད་པའི་རྩ་བ་དང་དེའི་འགྲེལ་བ་སོགས།",
        language="bo",
        slug="bodhicaryavatara",
        has_child=False
    )
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

    with patch('pecha_api.texts.texts_service.get_collection', new_callable=AsyncMock, return_value=mock_collection), \
            patch('pecha_api.texts.texts_service.get_texts_by_collection', new_callable=AsyncMock) as mock_get_texts_by_category, \
            patch('pecha_api.texts.texts_service.get_text_by_text_id_or_collection_cache', new_callable=AsyncMock, return_value=None), \
            patch('pecha_api.texts.texts_service.set_text_by_text_id_or_collection_cache', new_callable=AsyncMock, return_value=None), \
            patch('pecha_api.texts.texts_service.TextUtils.filter_text_base_on_group_id_type', new_callable=AsyncMock) as mock_filter_text_base_on_group_id_type:
        mock_filter_text_base_on_group_id_type.return_value = {"root_text": mock_texts_by_category[1], "commentary": [mock_texts_by_category[0]]}
        mock_get_texts_by_category.return_value = mock_texts_by_category
        response = await get_text_by_text_id_or_collection(text_id="", collection_id="id_1", language="bo", skip=0, limit=10)
        assert response is not None
        assert response.collection is not None
        collection: CollectionModel = response.collection
        assert collection.id == "id_1"
        assert collection.slug == "bodhicaryavatara"
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
        patch("pecha_api.texts.texts_service.get_text_versions_by_group_id_cache", new_callable=AsyncMock, return_value=None),\
        patch("pecha_api.texts.texts_service.set_text_versions_by_group_id_cache", new_callable=AsyncMock, return_value=None),\
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
            pecha_text_id="test_pecha_id",
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
            views=0,
            source_link="https://test-source.com",
            ranking=1,
            license="CC0"
        )
        mock_validate_group_exists.return_value = True
        response = await create_new_text(
            create_text_request=CreateTextRequest(
                pecha_text_id="test_pecha_id",
                title=title,
                language=language,
                group_id=group_id,
                published_by=published_by,
                type=type_,
                categories=categories,
                source_link="https://test-source.com",
                ranking=1,
                license="CC0"
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
async def test_create_new_text_invalid_group_id():
    with patch("pecha_api.texts.texts_service.validate_user_exists", return_value=True), \
        patch("pecha_api.texts.texts_service.validate_group_exists", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await create_new_text(
                create_text_request=CreateTextRequest(
                    pecha_text_id="test_pecha_id",
                    title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
                    language="bo",
                    group_id="invalid_group_id",
                    published_by="pecha",
                    type=TextType.VERSION,
                    categories=[],
                    source_link="https://test-source.com",
                    ranking=1,
                    license="CC0"
                ),
                token="user"
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.GROUP_NOT_FOUND_MESSAGE
    
@pytest.mark.asyncio
async def test_create_new_text_invalid_user():
    with patch("pecha_api.texts.texts_service.validate_user_exists", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await create_new_text(
                create_text_request=CreateTextRequest(
                    pecha_text_id="test_pecha_id",
                    title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
                    language="bo",
                    group_id="67dd22a8d9f06ab28feedc90",
                    published_by="pecha",
                    type=TextType.VERSION,
                    categories=[],
                    source_link="https://test-source.com",
                    ranking=1,
                    license="CC0"
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
                    segments=[
                        TextSegment(
                            segment_id="seg_1",
                            segment_number=1
                        )
                    ],
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
async def test_get_table_of_contents_by_text_id_success_language_is_none():
    text_id = "text_id_1"
    language = "en"
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
                    segments=[
                        TextSegment(
                            segment_id="seg_1",
                            segment_number=1
                        )
                    ],
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
            language=None,
            skip=skip,
            limit=limit
        )
        
        assert response is not None
        assert isinstance(response, TableOfContentResponse)
        assert response.text_detail is not None
        assert isinstance(response.text_detail, TextDTO)
        assert response.text_detail.language == language
        assert response.contents is not None
        assert len(response.contents) == 1
        assert response.contents[0] is not None
        assert isinstance(response.contents[0], TableOfContent)

@pytest.mark.asyncio
async def test_get_table_of_contents_by_text_id_root_text_is_none():
    text_id = "text_id_1"
    language = "en"
    skip = 0
    limit = 10

    mock_text_detail = TextDTO(
        id=text_id,
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
        
        with pytest.raises(HTTPException) as exc_info:
            await get_table_of_contents_by_text_id(
                text_id=text_id,
                language="zh",
                skip=0,
                limit=10
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE

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
                direction=PaginationDirection.PREVIOUS
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
        assert section.segments[0].segment_id == "segment_id_1"
        assert response.pagination_direction == PaginationDirection.PREVIOUS


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
                    sections=[
                        Section(
                            id="section_id_2",
                            title="section_title_2",
                            section_number=2,
                            parent_id="parent_id_2",
                            segments=[
                                TextSegment(
                                    segment_id=f"1_segment_id_{i}",
                                    segment_number=1
                                )
                            ],
                            sections=[],
                            created_date="created_date",
                            updated_date="updated_date",
                            published_date="published_date"
                        )
                    ],
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
                sections=[
                    DetailSection(
                        id="section_id_2",
                        title="section_title_2",
                        section_number=2,
                        parent_id="parent_id_2",
                        segments=[
                            DetailTextSegment(
                                segment_id=f"1_segment_id_1",
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
                ],
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
        assert section.sections is not None
        assert len(section.segments) + len(section.sections[0].segments) == 2
        assert section.segments[0].segment_id == "segment_id_1"
        assert response.pagination_direction == PaginationDirection.NEXT
    

@pytest.mark.asyncio
async def test_get_table_of_content_by_sheet_id_success():
    sheet_id = "sheet_id_1"
    mock_table_of_contents = [
        TableOfContent(
            id="content_id_1",
            text_id=sheet_id,
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
                        )
                    ],
                    sections=[],
                    created_date="created_date",
                    updated_date="updated_date",
                    published_date="published_date"
                )
            ]
        )
    ]
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.get_contents_by_id", new_callable=AsyncMock, return_value=mock_table_of_contents):
    
        response = await get_table_of_content_by_sheet_id(sheet_id=sheet_id)

        assert response is not None
        assert isinstance(response, TableOfContent)
        assert response.id == "content_id_1"

@pytest.mark.asyncio
async def test_get_table_of_content_by_sheet_id_invalid_sheet_id():
    sheet_id = "invalid_sheet_id"

    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await get_table_of_content_by_sheet_id(sheet_id=sheet_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE
    

@pytest.mark.asyncio
async def test_validate_text_detail_request_success():
    text_id = "text_id_1"
    content_id = "content_id_1"
    version_id = "version_id_1"
    segment_id = "segment_id_1"
    section_id = "section_id_1"
    size = 20
    direction = PaginationDirection.NEXT

    text_details_request = TextDetailsRequest(
        content_id=content_id,
        version_id=version_id,
        segment_id=segment_id,
        section_id=section_id,
        size=size,
        direction=direction
    )

    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.SegmentUtils.validate_segment_exists", new_callable=AsyncMock, return_value=True):
        
        response = await _validate_text_detail_request(text_id=text_id, text_details_request=text_details_request)
        
@pytest.mark.asyncio
async def test_validate_text_detail_request_text_id_is_none():
    text_id = None
    content_id = "content_id_1"
    version_id = "version_id_1"
    segment_id = "segment_id_1"
    section_id = "section_id_1"
    size = 20
    direction = PaginationDirection.NEXT

    text_details_request = TextDetailsRequest(
        content_id=content_id,
        version_id=version_id,
        segment_id=segment_id,
        section_id=section_id,
        size=size,
        direction=direction
    )

    with pytest.raises(HTTPException) as e:
        await _validate_text_detail_request(text_id=text_id, text_details_request=text_details_request)

    assert e.value.status_code == 400
    assert e.value.detail == ErrorConstants.TEXT_OR_TERM_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_validate_text_detail_request_invalid_version_id():
    text_id = None
    content_id = "content_id_1"
    version_id = "invalid_version_id_1"
    segment_id = "segment_id_1"
    section_id = "section_id_1"
    size = 20
    direction = PaginationDirection.NEXT

    text_details_request = TextDetailsRequest(
        content_id=content_id,
        version_id=version_id,
        segment_id=segment_id,
        section_id=section_id,
        size=size,
        direction=direction
    )

    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as e:
            await _validate_text_detail_request(text_id=text_id, text_details_request=text_details_request)
        assert e.value.status_code == 400
        assert e.value.detail == ErrorConstants.TEXT_OR_TERM_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_validate_text_detail_request_invalid_segment_id():
    text_id = None
    content_id = "content_id_1"
    version_id = "version_id_1"
    segment_id = "invalid_segment_id_1"
    section_id = "section_id_1"
    size = 20
    direction = PaginationDirection.NEXT
    
    text_details_request = TextDetailsRequest(
        content_id=content_id,
        version_id=version_id,
        segment_id=segment_id,
        section_id=section_id,
        size=size,
        direction=direction
    )
    
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.SegmentUtils.validate_segment_exists", new_callable=AsyncMock, return_value=False):

        with pytest.raises(HTTPException) as e:
            await _validate_text_detail_request(text_id=text_id, text_details_request=text_details_request)
        
        assert e.value.status_code == 400
        assert e.value.detail == ErrorConstants.TEXT_OR_TERM_NOT_FOUND_MESSAGE


@pytest.mark.asyncio
async def test_get_versions_by_group_id_language_is_none():
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
        patch("pecha_api.texts.texts_service.get_text_versions_by_group_id_cache", new_callable=AsyncMock, return_value=None),\
        patch("pecha_api.texts.texts_service.set_text_versions_by_group_id_cache", new_callable=AsyncMock, return_value=None),\
        patch('pecha_api.texts.texts_service.get_texts_by_group_id', new_callable=AsyncMock) as mock_get_texts_by_group_id,\
        patch('pecha_api.texts.texts_service.get_contents_by_id', new_callable=AsyncMock) as mock_get_contents_by_id:
        mock_text_detail.return_value = text_detail
        mock_get_texts_by_group_id.return_value = texts_by_group_id
        mock_get_contents_by_id.return_value = [mock_table_of_content]
        response = await get_text_versions_by_group_id(text_id="id_1",language=None, skip=0, limit=10)
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
async def test_get_versions_by_group_id_cache_data_is_not_none():
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
    cache_text_version = TextVersionResponse(
        text=text_detail,
        versions=[
            TextVersion(
                id="text_id_1",
                title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
                parent_id=None,
                priority=None,
                language="bo",
                type="version",
                group_id="group_id_1",
                table_of_contents=[],
                is_published=True,
                created_date="2025-03-20 09:26:16.571522",
                updated_date="2025-03-20 09:26:16.571532",
                published_date="2025-03-20 09:26:16.571536",
                published_by="pecha"
            )
        ]
    )
    language = "en"
    with patch("pecha_api.texts.texts_service.get_text_versions_by_group_id_cache", new_callable=AsyncMock, return_value=cache_text_version):

        response = await get_text_versions_by_group_id(text_id="id_1",language=language, skip=0, limit=10)

        assert response is not None
        assert isinstance(response, TextVersionResponse)
        assert response.text is not None
        assert isinstance(response.text, TextDTO)
        assert response.versions is not None
        assert len(response.versions) == 1
        assert response.text.id == "id_1"
        assert response.versions[0] is not None
        assert isinstance(response.versions[0], TextVersion)
        assert response.versions[0].id == "text_id_1"


@pytest.mark.asyncio
async def test_get_root_text_by_collection_id_success_with_root_text():
    """Test get_root_text_by_collection_id when root text is found"""
    collection_id = "collection_id_1"
    language = "bo"
    
    mock_texts = [
        TextDTO(
            id="text_id_1",
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
        )
    ]
    
    mock_filtered_result = {
        "root_text": mock_texts[0],  
        "versions": [mock_texts[1]]
    }
    
    with patch("pecha_api.texts.texts_service.get_all_texts_by_collection", new_callable=AsyncMock) as mock_get_all_texts, \
         patch("pecha_api.texts.texts_service.TextUtils.filter_text_on_root_and_version") as mock_filter:
        
        mock_get_all_texts.return_value = mock_texts
        mock_filter.return_value = mock_filtered_result
        
        result = await get_root_text_by_collection_id(collection_id=collection_id, language=language)
        
        mock_get_all_texts.assert_called_once_with(collection_id=collection_id)
        mock_filter.assert_called_once_with(texts=mock_texts, language=language)
        
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == "text_id_1"
        assert result[1] == "བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།"


@pytest.mark.asyncio
async def test_get_commentaries_by_text_id_success():
    """Test get_commentaries_by_text_id with valid text_id and matching commentaries"""
    text_id = "root-text-uuid"
    group_id = "group-uuid-123"
    skip = 0
    limit = 10
    
    mock_root_text = MagicMock()
    mock_root_text.id = text_id
    mock_root_text.group_id = group_id
    mock_root_text.language = "bo"
    mock_root_text.type = "root"
    
    mock_commentary_1 = MagicMock()
    mock_commentary_1.id = "commentary-1-uuid"
    mock_commentary_1.pecha_text_id = "commentary_pecha_1"
    mock_commentary_1.title = "Commentary on Heart Sutra"
    mock_commentary_1.language = "bo"
    mock_commentary_1.group_id = "commentary-group-1"
    mock_commentary_1.type = "commentary"
    mock_commentary_1.is_published = True
    mock_commentary_1.created_date = "2025-01-01T00:00:00"
    mock_commentary_1.updated_date = "2025-01-01T00:00:00"
    mock_commentary_1.published_date = "2025-01-01T00:00:00"
    mock_commentary_1.published_by = "commentator_1"
    mock_commentary_1.categories = [group_id, "other-category"]
    mock_commentary_1.views = 100
    mock_commentary_1.source_link = "https://commentary-1.com"
    mock_commentary_1.ranking = 1
    mock_commentary_1.license = "CC0"
    
    mock_commentary_2 = MagicMock()
    mock_commentary_2.id = "commentary-2-uuid"
    mock_commentary_2.pecha_text_id = "commentary_pecha_2"
    mock_commentary_2.title = "Another Commentary"
    mock_commentary_2.language = "bo"
    mock_commentary_2.group_id = "commentary-group-2"
    mock_commentary_2.type = "commentary"
    mock_commentary_2.is_published = True
    mock_commentary_2.created_date = "2025-01-02T00:00:00"
    mock_commentary_2.updated_date = "2025-01-02T00:00:00"
    mock_commentary_2.published_date = "2025-01-02T00:00:00"
    mock_commentary_2.published_by = "commentator_2"
    mock_commentary_2.categories = [group_id]
    mock_commentary_2.views = 50
    mock_commentary_2.source_link = "https://commentary-2.com"
    mock_commentary_2.ranking = 2
    mock_commentary_2.license = "CC BY"
    
    mock_commentary_3 = MagicMock()
    mock_commentary_3.id = "commentary-3-uuid"
    mock_commentary_3.pecha_text_id = "commentary_pecha_3"
    mock_commentary_3.title = "Unrelated Commentary"
    mock_commentary_3.language = "bo"
    mock_commentary_3.group_id = "commentary-group-3"
    mock_commentary_3.type = "commentary"
    mock_commentary_3.is_published = True
    mock_commentary_3.created_date = "2025-01-03T00:00:00"
    mock_commentary_3.updated_date = "2025-01-03T00:00:00"
    mock_commentary_3.published_date = "2025-01-03T00:00:00"
    mock_commentary_3.published_by = "commentator_3"
    mock_commentary_3.categories = ["different-group-id"]
    mock_commentary_3.views = 25
    mock_commentary_3.source_link = None
    mock_commentary_3.ranking = None
    mock_commentary_3.license = None
    
    with patch('pecha_api.texts.texts_service.TextUtils.validate_text_exists', new_callable=AsyncMock) as mock_validate, \
         patch('pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id', new_callable=AsyncMock) as mock_get_text, \
         patch('pecha_api.texts.texts_service.TextUtils.get_commentaries_by_text_type', new_callable=AsyncMock) as mock_get_commentaries:
        
        mock_validate.return_value = True
        mock_get_text.return_value = mock_root_text
        mock_get_commentaries.return_value = [mock_commentary_1, mock_commentary_2, mock_commentary_3]
        
        result = await get_commentaries_by_text_id(text_id=text_id, skip=skip, limit=limit)
        
        mock_validate.assert_called_once_with(text_id=text_id)
        mock_get_text.assert_called_once_with(text_id=text_id)
        mock_get_commentaries.assert_called_once_with(
            text_type="commentary",
            language="bo",
            skip=skip,
            limit=limit
        )
        
        assert len(result) == 2
        assert result[0].id == "commentary-1-uuid"
        assert result[0].title == "Commentary on Heart Sutra"
        assert result[0].categories == [group_id, "other-category"]
        assert result[1].id == "commentary-2-uuid"
        assert result[1].title == "Another Commentary"
        assert result[1].categories == [group_id]


@pytest.mark.asyncio
async def test_get_commentaries_by_text_id_no_matching_commentaries():
    """Test get_commentaries_by_text_id when no commentaries match the group_id"""
    text_id = "root-text-uuid"
    group_id = "group-uuid-123"
    skip = 0
    limit = 10
    
    mock_root_text = MagicMock()
    mock_root_text.id = text_id
    mock_root_text.group_id = group_id
    mock_root_text.language = "bo"
    mock_root_text.type = "root"
    
    mock_commentary = MagicMock()
    mock_commentary.id = "commentary-uuid"
    mock_commentary.pecha_text_id = "commentary_pecha"
    mock_commentary.title = "Unrelated Commentary"
    mock_commentary.language = "bo"
    mock_commentary.group_id = "commentary-group"
    mock_commentary.type = "commentary"
    mock_commentary.is_published = True
    mock_commentary.created_date = "2025-01-01T00:00:00"
    mock_commentary.updated_date = "2025-01-01T00:00:00"
    mock_commentary.published_date = "2025-01-01T00:00:00"
    mock_commentary.published_by = "commentator"
    mock_commentary.categories = ["different-group-id", "another-category"]
    mock_commentary.views = 10
    mock_commentary.source_link = None
    mock_commentary.ranking = None
    mock_commentary.license = None
    
    with patch('pecha_api.texts.texts_service.TextUtils.validate_text_exists', new_callable=AsyncMock) as mock_validate, \
         patch('pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id', new_callable=AsyncMock) as mock_get_text, \
         patch('pecha_api.texts.texts_service.TextUtils.get_commentaries_by_text_type', new_callable=AsyncMock) as mock_get_commentaries:
        
        mock_validate.return_value = True
        mock_get_text.return_value = mock_root_text
        mock_get_commentaries.return_value = [mock_commentary]
        
        result = await get_commentaries_by_text_id(text_id=text_id, skip=skip, limit=limit)
        
        assert len(result) == 0
        assert result == []


@pytest.mark.asyncio
async def test_get_commentaries_by_text_id_empty_commentaries_list():
    """Test get_commentaries_by_text_id when no commentaries exist at all"""
    text_id = "root-text-uuid"
    group_id = "group-uuid-123"
    skip = 0
    limit = 10
    
    mock_root_text = MagicMock()
    mock_root_text.id = text_id
    mock_root_text.group_id = group_id
    mock_root_text.language = "en"
    mock_root_text.type = "root"
    
    with patch('pecha_api.texts.texts_service.TextUtils.validate_text_exists', new_callable=AsyncMock) as mock_validate, \
         patch('pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id', new_callable=AsyncMock) as mock_get_text, \
         patch('pecha_api.texts.texts_service.TextUtils.get_commentaries_by_text_type', new_callable=AsyncMock) as mock_get_commentaries:
        
        mock_validate.return_value = True
        mock_get_text.return_value = mock_root_text
        mock_get_commentaries.return_value = []
        
        result = await get_commentaries_by_text_id(text_id=text_id, skip=skip, limit=limit)
        
        assert len(result) == 0
        assert result == []


@pytest.mark.asyncio
async def test_get_commentaries_by_text_id_text_not_found():
    """Test get_commentaries_by_text_id with non-existent text_id"""
    text_id = "non-existent-uuid"
    skip = 0
    limit = 10
    
    with patch('pecha_api.texts.texts_service.TextUtils.validate_text_exists', new_callable=AsyncMock) as mock_validate:
        mock_validate.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            await get_commentaries_by_text_id(text_id=text_id, skip=skip, limit=limit)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE
        mock_validate.assert_called_once_with(text_id=text_id)


@pytest.mark.asyncio
async def test_get_commentaries_by_text_id_with_pagination():
    """Test get_commentaries_by_text_id with custom pagination parameters"""
    text_id = "root-text-uuid"
    group_id = "group-uuid-123"
    skip = 5
    limit = 20
    
    mock_root_text = MagicMock()
    mock_root_text.id = text_id
    mock_root_text.group_id = group_id
    mock_root_text.language = "zh"
    mock_root_text.type = "root"
    
    mock_commentary = MagicMock()
    mock_commentary.id = "commentary-uuid"
    mock_commentary.pecha_text_id = "commentary_pecha"
    mock_commentary.title = "Chinese Commentary"
    mock_commentary.language = "zh"
    mock_commentary.group_id = "commentary-group"
    mock_commentary.type = "commentary"
    mock_commentary.is_published = True
    mock_commentary.created_date = "2025-01-01T00:00:00"
    mock_commentary.updated_date = "2025-01-01T00:00:00"
    mock_commentary.published_date = "2025-01-01T00:00:00"
    mock_commentary.published_by = "commentator"
    mock_commentary.categories = [group_id]
    mock_commentary.views = 30
    mock_commentary.source_link = "https://chinese-commentary.com"
    mock_commentary.ranking = 1
    mock_commentary.license = "CC BY-SA"
    
    with patch('pecha_api.texts.texts_service.TextUtils.validate_text_exists', new_callable=AsyncMock) as mock_validate, \
         patch('pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id', new_callable=AsyncMock) as mock_get_text, \
         patch('pecha_api.texts.texts_service.TextUtils.get_commentaries_by_text_type', new_callable=AsyncMock) as mock_get_commentaries:
        
        mock_validate.return_value = True
        mock_get_text.return_value = mock_root_text
        mock_get_commentaries.return_value = [mock_commentary]
        
        result = await get_commentaries_by_text_id(text_id=text_id, skip=skip, limit=limit)
        
        mock_get_commentaries.assert_called_once_with(
            text_type="commentary",
            language="zh",
            skip=skip,
            limit=limit
        )
        
        assert len(result) == 1
        assert result[0].language == "zh"


@pytest.mark.asyncio
async def test_get_commentaries_by_text_id_commentary_with_none_categories():
    """Test get_commentaries_by_text_id when commentary has None categories"""
    text_id = "root-text-uuid"
    group_id = "group-uuid-123"
    skip = 0
    limit = 10
    
    mock_root_text = MagicMock()
    mock_root_text.id = text_id
    mock_root_text.group_id = group_id
    mock_root_text.language = "bo"
    mock_root_text.type = "root"
    
    mock_commentary = MagicMock()
    mock_commentary.id = "commentary-uuid"
    mock_commentary.pecha_text_id = "commentary_pecha"
    mock_commentary.title = "Commentary with None categories"
    mock_commentary.language = "bo"
    mock_commentary.group_id = "commentary-group"
    mock_commentary.type = "commentary"
    mock_commentary.is_published = True
    mock_commentary.created_date = "2025-01-01T00:00:00"
    mock_commentary.updated_date = "2025-01-01T00:00:00"
    mock_commentary.published_date = "2025-01-01T00:00:00"
    mock_commentary.published_by = "commentator"
    mock_commentary.categories = None
    mock_commentary.views = 5
    mock_commentary.source_link = None
    mock_commentary.ranking = None
    mock_commentary.license = None
    
    with patch('pecha_api.texts.texts_service.TextUtils.validate_text_exists', new_callable=AsyncMock) as mock_validate, \
         patch('pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id', new_callable=AsyncMock) as mock_get_text, \
         patch('pecha_api.texts.texts_service.TextUtils.get_commentaries_by_text_type', new_callable=AsyncMock) as mock_get_commentaries:
        
        mock_validate.return_value = True
        mock_get_text.return_value = mock_root_text
        mock_get_commentaries.return_value = [mock_commentary]
        
        result = await get_commentaries_by_text_id(text_id=text_id, skip=skip, limit=limit)
        
        assert len(result) == 0


@pytest.mark.asyncio
async def test_get_commentaries_by_text_id_commentary_with_empty_categories():
    """Test get_commentaries_by_text_id when commentary has empty categories list"""
    text_id = "root-text-uuid"
    group_id = "group-uuid-123"
    skip = 0
    limit = 10
    
    mock_root_text = MagicMock()
    mock_root_text.id = text_id
    mock_root_text.group_id = group_id
    mock_root_text.language = "bo"
    mock_root_text.type = "root"
    
    mock_commentary = MagicMock()
    mock_commentary.id = "commentary-uuid"
    mock_commentary.pecha_text_id = "commentary_pecha"
    mock_commentary.title = "Commentary with empty categories"
    mock_commentary.language = "bo"
    mock_commentary.group_id = "commentary-group"
    mock_commentary.type = "commentary"
    mock_commentary.is_published = True
    mock_commentary.created_date = "2025-01-01T00:00:00"
    mock_commentary.updated_date = "2025-01-01T00:00:00"
    mock_commentary.published_date = "2025-01-01T00:00:00"
    mock_commentary.published_by = "commentator"
    mock_commentary.categories = []
    mock_commentary.views = 0
    mock_commentary.source_link = None
    mock_commentary.ranking = None
    mock_commentary.license = None
    
    with patch('pecha_api.texts.texts_service.TextUtils.validate_text_exists', new_callable=AsyncMock) as mock_validate, \
         patch('pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id', new_callable=AsyncMock) as mock_get_text, \
         patch('pecha_api.texts.texts_service.TextUtils.get_commentaries_by_text_type', new_callable=AsyncMock) as mock_get_commentaries:
        
        mock_validate.return_value = True
        mock_get_text.return_value = mock_root_text
        mock_get_commentaries.return_value = [mock_commentary]
        
        result = await get_commentaries_by_text_id(text_id=text_id, skip=skip, limit=limit)
        
        assert len(result) == 0


@pytest.mark.asyncio
async def test_get_commentaries_by_text_id_single_matching_commentary():
    """Test get_commentaries_by_text_id with single matching commentary"""
    text_id = "root-text-uuid"
    group_id = "group-uuid-123"
    skip = 0
    limit = 10
    
    mock_root_text = MagicMock()
    mock_root_text.id = text_id
    mock_root_text.group_id = group_id
    mock_root_text.language = "en"
    mock_root_text.type = "root"
    
    mock_commentary = MagicMock()
    mock_commentary.id = "single-commentary-uuid"
    mock_commentary.pecha_text_id = "single_commentary_pecha"
    mock_commentary.title = "Single Commentary"
    mock_commentary.language = "en"
    mock_commentary.group_id = "commentary-group"
    mock_commentary.type = "commentary"
    mock_commentary.is_published = True
    mock_commentary.created_date = "2025-01-01T00:00:00"
    mock_commentary.updated_date = "2025-01-01T00:00:00"
    mock_commentary.published_date = "2025-01-01T00:00:00"
    mock_commentary.published_by = "single_commentator"
    mock_commentary.categories = [group_id]
    mock_commentary.views = 15
    mock_commentary.source_link = "https://single-commentary.com"
    mock_commentary.ranking = 1
    mock_commentary.license = "CC0"
    
    with patch('pecha_api.texts.texts_service.TextUtils.validate_text_exists', new_callable=AsyncMock) as mock_validate, \
         patch('pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id', new_callable=AsyncMock) as mock_get_text, \
         patch('pecha_api.texts.texts_service.TextUtils.get_commentaries_by_text_type', new_callable=AsyncMock) as mock_get_commentaries:
        
        mock_validate.return_value = True
        mock_get_text.return_value = mock_root_text
        mock_get_commentaries.return_value = [mock_commentary]
        
        result = await get_commentaries_by_text_id(text_id=text_id, skip=skip, limit=limit)
        
        assert len(result) == 1
        assert result[0].id == "single-commentary-uuid"
        assert result[0].title == "Single Commentary"
        assert result[0].type == "commentary"
        assert result[0].categories == [group_id]


@pytest.mark.asyncio
async def test_get_commentaries_by_text_id_with_optional_fields_none():
    """Test get_commentaries_by_text_id with optional fields as None"""
    text_id = "root-text-uuid"
    group_id = "group-uuid-123"
    skip = 0
    limit = 10
    
    mock_root_text = MagicMock()
    mock_root_text.id = text_id
    mock_root_text.group_id = group_id
    mock_root_text.language = "bo"
    mock_root_text.type = "root"
    
    mock_commentary = MagicMock()
    mock_commentary.id = "commentary-uuid"
    mock_commentary.pecha_text_id = None
    mock_commentary.title = "Commentary with None fields"
    mock_commentary.language = "bo"
    mock_commentary.group_id = "commentary-group"
    mock_commentary.type = "commentary"
    mock_commentary.is_published = True
    mock_commentary.created_date = "2025-01-01T00:00:00"
    mock_commentary.updated_date = "2025-01-01T00:00:00"
    mock_commentary.published_date = "2025-01-01T00:00:00"
    mock_commentary.published_by = "commentator"
    mock_commentary.categories = [group_id]
    mock_commentary.views = 0
    mock_commentary.source_link = None
    mock_commentary.ranking = None
    mock_commentary.license = None
    
    with patch('pecha_api.texts.texts_service.TextUtils.validate_text_exists', new_callable=AsyncMock) as mock_validate, \
         patch('pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id', new_callable=AsyncMock) as mock_get_text, \
         patch('pecha_api.texts.texts_service.TextUtils.get_commentaries_by_text_type', new_callable=AsyncMock) as mock_get_commentaries:
        
        mock_validate.return_value = True
        mock_get_text.return_value = mock_root_text
        mock_get_commentaries.return_value = [mock_commentary]
        
        result = await get_commentaries_by_text_id(text_id=text_id, skip=skip, limit=limit)
        
        assert len(result) == 1
        assert result[0].pecha_text_id is None
        assert result[0].source_link is None
        assert result[0].ranking is None
        assert result[0].license is None
        assert result[0].views == 0
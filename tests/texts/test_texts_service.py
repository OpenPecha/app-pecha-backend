from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from pecha_api.terms.terms_response_models import TermsModel
import pytest
from pecha_api.texts.texts_service import (
    create_new_text,
    get_versions_by_text_id,
    get_text_by_text_id_or_term,
    create_table_of_content,
    get_table_of_contents_by_text_id,
    get_text_details_by_text_id
)
from pecha_api.texts.texts_response_models import (
    CreateTextRequest,
    TextModel,
    Text,
    TextVersion,
    TextVersionResponse,
    TableOfContent,
    Section,
    TextSegment,
    TextsCategoryResponse,
    TableOfContentResponse,
    TextDetailsRequest,
    DetailTableOfContentResponse,
    DetailTableOfContent,
    DetailSection,
    DetailTextSegment,
    Translation,
    DetailTextMapping
)
from pecha_api.error_contants import ErrorConstants

@pytest.mark.asyncio
async def test_get_text_by_term_id():
    mock_term = AsyncMock(id="id_1", titles={"bo": "སྤྱོད་འཇུག"}, descriptions={
        "bo": "དུས་རབས་ ༨ པའི་ནང་སློབ་དཔོན་ཞི་བ་ལྷས་མཛད་པའི་རྩ་བ་དང་དེའི་འགྲེལ་བ་སོགས།"}, slug="bodhicaryavatara",
                          has_sub_child=False)
    mock_texts_by_category = [
        Text(
            id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
            title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
            language="bo",
            type="root_text",
            is_published=True,
            created_date="2025-03-20 09:26:16.571522",
            updated_date="2025-03-20 09:26:16.571532",
            published_date="2025-03-20 09:26:16.571536",
            published_by="pecha"
        ),
        Text(
            id="a48c0814-ce56-4ada-af31-f74b179b52a9",
            title="སྤྱོད་འཇུག་དཀའ་འགྲེལ།",
            language="bo",
            type="commentary",
            is_published=True,
            created_date="2025-03-21 09:40:34.025024",
            updated_date="2025-03-21 09:40:34.025035",
            published_date="2025-03-21 09:40:34.025038",
            published_by="pecha"
        )
    ]

    with patch('pecha_api.texts.texts_service.get_texts_by_term', new_callable=AsyncMock) as mock_get_texts_by_category, \
            patch('pecha_api.terms.terms_service.get_term_by_id', new_callable=AsyncMock) as mock_get_term:
        mock_get_texts_by_category.return_value = mock_texts_by_category
        mock_get_term.return_value = mock_term
        response = await get_text_by_text_id_or_term(text_id="", term_id="id_1", language="bo", skip=0, limit=10)
        assert response == TextsCategoryResponse(
            term=TermsModel(
                id="id_1",
                title="སྤྱོད་འཇུག",
                description="དུས་རབས་ ༨ པའི་ནང་སློབ་དཔོན་ཞི་བ་ལྷས་མཛད་པའི་རྩ་བ་དང་དེའི་འགྲེལ་བ་སོགས།",
                has_child=False,
                slug="bodhicaryavatara"
            ),
            texts=[
                Text(
                    id=str(text.id),
                    title=text.title,
                    language=text.language,
                    type=text.type,
                    is_published=text.is_published,
                    created_date=text.created_date,
                    updated_date=text.updated_date,
                    published_date=text.published_date,
                    published_by=text.published_by
                )
                for text in mock_texts_by_category
            ],
            total=len(mock_texts_by_category),
            skip=0,
            limit=10
        )


@pytest.mark.asyncio
async def test_get_versions_by_text_id():
    text_detail = TextModel(
        id="id_1",
        title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
        language="bo",
        type="root_text",
        is_published=True,
        created_date="2025-03-20 09:26:16.571522",
        updated_date="2025-03-20 09:26:16.571532",
        published_date="2025-03-20 09:26:16.571536",
        published_by="pecha",
        categories=["67dd22a8d9f06ab28feedc90"],
        parent_id=None
    )
    versions_by_text_id = [
        TextVersion(
            id="59769286-2787-4181-953d-9149cdeef959",
            title="The Way of the Bodhisattva",
            parent_id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
            priority=None,
            language="en",
            type="version",
            is_published=True,
            created_date="2025-03-20 09:28:28.076920",
            updated_date="2025-03-20 09:28:28.076934",
            published_date="2025-03-20 09:28:28.076938",
            published_by="pecha"
        ),
        TextVersion(
            id="ee88cb8b-42b2-45af-a6a4-753c0e9d779c",
            title="शबोधिचर्यावतार",
            parent_id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
            priority=None,
            language="sa",
            type="version",
            is_published=True,
            created_date="2025-03-20 09:29:51.154697",
            updated_date="2025-03-20 09:29:51.154708",
            published_date="2025-03-20 09:29:51.154712",
            published_by="pecha"
        )
    ]
    with patch('pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id', new_callable=AsyncMock) as mock_text_detail, \
            patch('pecha_api.texts.texts_service.get_versions_by_id',
                  new_callable=AsyncMock) as mock_get_versions_by_text_id:
        mock_text_detail.return_value = text_detail
        mock_get_versions_by_text_id.return_value = versions_by_text_id
        response = await get_versions_by_text_id(text_id="id_1", skip=0, limit=10)

        assert response.text == TextModel(
            id="id_1",
            title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
            language="bo",
            type="root_text",
            is_published=True,
            created_date="2025-03-20 09:26:16.571522",
            updated_date="2025-03-20 09:26:16.571532",
            published_date="2025-03-20 09:26:16.571536",
            published_by="pecha",
            categories=["67dd22a8d9f06ab28feedc90"],
            parent_id=None
        )
        assert response.versions[0] == TextVersion(
            id="59769286-2787-4181-953d-9149cdeef959",
            title="The Way of the Bodhisattva",
            parent_id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
            priority=None,
            language="en",
            type="version",
            is_published=True,
            created_date="2025-03-20 09:28:28.076920",
            updated_date="2025-03-20 09:28:28.076934",
            published_date="2025-03-20 09:28:28.076938",
            published_by="pecha"
        )
        assert response.versions[-1] == TextVersion(
            id="id_1",
            title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
            language="bo",
            type="root_text",
            is_published=True,
            created_date="2025-03-20 09:26:16.571522",
            updated_date="2025-03-20 09:26:16.571532",
            published_date="2025-03-20 09:26:16.571536",
            published_by="pecha",
            parent_id=None
        )


@pytest.mark.asyncio
async def test_create_new_root_text():
    with patch('pecha_api.texts.texts_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.texts_service.create_text', new_callable=AsyncMock) as mock_create_text:
        mock_create_text.return_value = AsyncMock(id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
                                                  title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།", language="bo",
                                                  parent_id=None, is_published=True,
                                                  created_date="2025-03-16 04:40:54.757652",
                                                  updated_date="2025-03-16 04:40:54.757652",
                                                  published_date="2025-03-16 04:40:54.757652",
                                                  published_by="pecha", type="root_text", categories=[])
        response = await create_new_text(
            create_text_request=CreateTextRequest(
                title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
                language="bo",
                parent_id=None,
                published_by="pecha",
                type="root_text",
                categories=[]
            ),
            token="admin"
        )
        assert response == TextModel(
            id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
            language="bo",
            type="root_text",
            is_published=True,
            created_date="2025-03-16 04:40:54.757652",
            updated_date="2025-03-16 04:40:54.757652",
            published_date="2025-03-16 04:40:54.757652",
            published_by="pecha",
            categories=[],
            parent_id=None
        )
    
@pytest.mark.asyncio
async def test_create_new_root_text_not_admin():
    with patch("pecha_api.texts.texts_service.verify_admin_access", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await create_new_text(
                create_text_request=CreateTextRequest(
                    title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
                    language="bo",
                    parent_id=None,
                    published_by="pecha",
                    type="root_text",
                    categories=[]
                ),
                token="user"
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == ErrorConstants.ADMIN_ERROR_MESSAGE

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
                published_date="2025-03-16 04:40:54.757652",
                published_by="pecha"
            )
        ]
    )

    with patch("pecha_api.texts.texts_service.verify_admin_access", return_value=True), \
            patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock) as mock_validate_text_exists, \
            patch("pecha_api.texts.texts_service.SegmentUtils.validate_segments_exists", new_callable=AsyncMock) as mock_validate_segments_exists, \
            patch("pecha_api.texts.texts_service.create_table_of_content_detail", new_callable=AsyncMock) as mock_create_table_of_content_detail:
        mock_validate_text_exists.return_value = True
        mock_validate_segments_exists.return_value = True
        mock_create_table_of_content_detail.return_value = table_of_content
        response = await create_table_of_content(table_of_content_request=table_of_content, token="admin")
        assert response == table_of_content
    
@pytest.mark.asyncio
async def test_create_table_of_content_not_admin():
    with patch("pecha_api.texts.texts_service.verify_admin_access", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await create_table_of_content(table_of_content_request={}, token="user")
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == ErrorConstants.ADMIN_ERROR_MESSAGE

@pytest.mark.asyncio
async def test_create_table_of_content_invalid_text():
    table_of_content = type('TableOfContent', () , {
        'id': "id_1",
        'text_id': "text_id 1"
        }
    )
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock) as mock_validate_text_exists, \
        patch("pecha_api.texts.texts_service.verify_admin_access", return_value=True):
        mock_validate_text_exists.return_value = False
        with pytest.raises(HTTPException) as exc_info:
            await create_table_of_content(table_of_content_request=table_of_content, token="admin")
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_create_table_of_content_invalid_segment():
    table_of_content = type('TableOfContent', () , {
        'id': "id_1",
        'text_id': "text_id 1"
        }
    )
    segment_ids = [
        "efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        "efb26a06-f373-450b-ba57-e7a8d4dd5b65"
    ]
    with patch("pecha_api.texts.texts_service.verify_admin_access", return_value=True), \
        patch("pecha_api.texts.texts_service.TextUtils.get_all_segment_ids", return_value=segment_ids), \
        patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.SegmentUtils.validate_segments_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await create_table_of_content(table_of_content_request=table_of_content, token="admin")
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE
    
@pytest.mark.asyncio
async def test_get_table_of_contents_by_text_id_success():
    table_of_contents = [
        TableOfContent(
            id="id_1",
            text_id="text_id 1",
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
                    published_date="2025-03-16 04:40:54.757652",
                    published_by="pecha"
                )
            ]
        )
    ]
    text_detail = TextModel(
        id="id_1",
        title="text_1",
        language="bo",
        type="root_text",
        is_published=True,
        created_date="2025-03-16 04:40:54.757652",
        updated_date="2025-03-16 04:40:54.757652",
        published_date="2025-03-16 04:40:54.757652",
        published_by="pecha",
        categories=[],
        parent_id=None
    )
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id", new_callable=AsyncMock) as mock_get_text_detail_by_id, \
        patch("pecha_api.texts.texts_service.get_contents_by_id", new_callable=AsyncMock) as mock_get_contents_by_id:
        mock_get_text_detail_by_id.return_value = text_detail
        mock_get_contents_by_id.return_value = table_of_contents
        response = await get_table_of_contents_by_text_id(text_id="id_1", skip=0, limit=10)
        assert response == TableOfContentResponse(
            text_detail=text_detail,
            contents=[
                TableOfContent(
                    id="id_1",
                    text_id="text_id 1",
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
                            published_date="2025-03-16 04:40:54.757652",
                            published_by="pecha"
                        )
                    ]
                )
            ]
        )

@pytest.mark.asyncio
async def test_get_table_of_contents_by_text_id_invalid_text():
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await get_table_of_contents_by_text_id(text_id="id_1", skip=0, limit=10)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_get_text_details_by_text_id_with_content_id_only_success():
    text_detail_request = TextDetailsRequest(
        content_id="content_id_1",
        skip=0,
        limit=1
    )
    text_detail = TextModel(
            id="id_1",
            title="text_1",
            language="bo",
            type="root_text",
            is_published=True,
            created_date="2025-03-16 04:40:54.757652",
            updated_date="2025-03-16 04:40:54.757652",
            published_date="2025-03-16 04:40:54.757652",
            published_by="pecha",
            categories=[],
            parent_id=None
        )
    table_of_content = TableOfContent(
        id="id_1",
        text_id="text_id_1",
        sections=[
            Section(
                id=f"id_{i}",
                title=f"section_{i}",
                section_number=i,
                parent_id="parent_id_1",
                segments=[
                    TextSegment(
                        segment_id=f"segment_id_{i}",
                        segment_number=1
                    )
                    for i in range(1,6)
                ],
                sections=[],
                created_date="2025-03-16 04:40:54.757652",
                updated_date="2025-03-16 04:40:54.757652",
                published_date="2025-03-16 04:40:54.757652",
                published_by="pecha"
            )
            for i in range(1,6)
        ]
    )
    detail_table_of_content = DetailTableOfContent(
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
                published_date="2025-03-16 04:40:54.757652",
                published_by="pecha"
            )
            for i in range(1,6)
        ]
    )
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id", new_callable=AsyncMock) as mock_get_text_detail_by_id, \
        patch("pecha_api.texts.texts_service.get_table_of_content_by_content_id", new_callable=AsyncMock) as mock_get_table_of_content_by_content_id, \
        patch("pecha_api.texts.texts_service.get_sections_count_of_table_of_content", new_callable=AsyncMock) as mock_get_sections_count_of_table_of_content, \
        patch("pecha_api.texts.texts_service.SegmentUtils.get_mapped_segment_content_for_table_of_content", new_callable=AsyncMock) as mock_get_mapped_segment_content:
        mock_get_text_detail_by_id.return_value = text_detail
        mock_get_table_of_content_by_content_id.return_value = table_of_content
        mock_get_sections_count_of_table_of_content.return_value = 10
        mock_get_mapped_segment_content.return_value = detail_table_of_content
        response = await get_text_details_by_text_id(text_id="text_id_1", text_details_request=text_detail_request)
        assert response.text_detail == text_detail
        assert response.mapping == DetailTextMapping(
            segment_id=None,
            section_id=None
        )
        assert response.skip == 0
        assert response.limit == 1
        assert response.total == 10
        assert response.content.sections == [
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
                    published_date="2025-03-16 04:40:54.757652",
                    published_by="pecha"
                )
                for i in range(1,6)
            ]
        assert response.content.id == "id_1"
        assert response.content.text_id == "text_id_1"
        assert response.content.sections[0].segments == [
                DetailTextSegment(
                    segment_id=f"segment_id_{i}",
                    segment_number=1,
                    content=f"content_{i}",
                    translation=None
                )
                for i in range(1,6)
            ]
    
@pytest.mark.asyncio
async def test_get_text_details_by_text_id_with_content_id_and_version_id_success():
    text_detail_request = TextDetailsRequest(
        content_id="content_id_1",
        version_id="version_id_1",
        skip=0,
        limit=1
    )
    text_detail = TextModel(
            id="id_1",
            title="text_1",
            language="bo",
            type="root_text",
            is_published=True,
            created_date="2025-03-16 04:40:54.757652",
            updated_date="2025-03-16 04:40:54.757652",
            published_date="2025-03-16 04:40:54.757652",
            published_by="pecha",
            categories=[],
            parent_id=None
        )
    table_of_content = TableOfContent(
        id="id_1",
        text_id="text_id_1",
        sections=[
            Section(
                id=f"id_{i}",
                title=f"section_{i}",
                section_number=i,
                parent_id="parent_id_1",
                segments=[
                    TextSegment(
                        segment_id=f"segment_id_{i}",
                        segment_number=1
                    )
                    for i in range(1,6)
                ],
                sections=[],
                created_date="2025-03-16 04:40:54.757652",
                updated_date="2025-03-16 04:40:54.757652",
                published_date="2025-03-16 04:40:54.757652",
                published_by="pecha"
            )
            for i in range(1,6)
        ]
    )
    detail_table_of_content = DetailTableOfContent(
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
                        translation=Translation(
                            text_id="text_id_1",
                            language="bo",
                            content=f"translation_{i}"
                        )
                    )
                    for i in range(1,6)
                ],
                sections=[],
                created_date="2025-03-16 04:40:54.757652",
                updated_date="2025-03-16 04:40:54.757652",
                published_date="2025-03-16 04:40:54.757652",
                published_by="pecha"
            )
            for i in range(1,6)
        ]
    )
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id", new_callable=AsyncMock) as mock_get_text_detail_by_id, \
        patch("pecha_api.texts.texts_service.get_table_of_content_by_content_id", new_callable=AsyncMock) as mock_get_table_of_content_by_content_id, \
        patch("pecha_api.texts.texts_service.get_sections_count_of_table_of_content", new_callable=AsyncMock) as mock_get_sections_count_of_table_of_content, \
        patch("pecha_api.texts.texts_service.SegmentUtils.get_mapped_segment_content_for_table_of_content", new_callable=AsyncMock) as mock_get_mapped_segment_content:
        mock_get_text_detail_by_id.return_value = text_detail
        mock_get_table_of_content_by_content_id.return_value = table_of_content
        mock_get_sections_count_of_table_of_content.return_value = 10
        mock_get_mapped_segment_content.return_value = detail_table_of_content
        response = await get_text_details_by_text_id(text_id="text_id_1", text_details_request=text_detail_request)
        assert response.text_detail == text_detail
        assert response.mapping == DetailTextMapping(
            segment_id=None,
            section_id=None
        )
        assert response.skip == 0
        assert response.limit == 1
        assert response.total == 10
        assert response.content.sections == [
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
                                translation=Translation(
                                    text_id="text_id_1",
                                    language="bo",
                                    content=f"translation_{i}"
                                )
                            )
                            for i in range(1,6)
                        ],
                        sections=[],
                        created_date="2025-03-16 04:40:54.757652",
                        updated_date="2025-03-16 04:40:54.757652",
                        published_date="2025-03-16 04:40:54.757652",
                        published_by="pecha"
                    )
                    for i in range(1,6)
                ]
        assert response.content.sections[0].segments == [
                            DetailTextSegment(
                                segment_id=f"segment_id_{i}",
                                segment_number=1,
                                content=f"content_{i}",
                                translation=Translation(
                                    text_id="text_id_1",
                                    language="bo",
                                    content=f"translation_{i}"
                                )
                            )
                            for i in range(1,6)
                        ]

@pytest.mark.asyncio
async def test_get_text_details_by_text_id_with_segment_id_success():
    text_detail_request = TextDetailsRequest(
        content_id=None,
        segment_id="123e4567-e89b-12d3-a456-426614174000",
        skip=0,
        limit=1
    )
    text_detail = TextModel(
            id="id_1",
            title="text_1",
            language="bo",
            type="root_text",
            is_published=True,
            created_date="2025-03-16 04:40:54.757652",
            updated_date="2025-03-16 04:40:54.757652",
            published_date="2025-03-16 04:40:54.757652",
            published_by="pecha",
            categories=[],
            parent_id=None
        )
    table_of_content = TableOfContent(
        id="id_1",
        text_id="text_id_1",
        sections=[
            Section(
                id=f"id_{i}",
                title=f"section_{i}",
                section_number=i,
                parent_id="parent_id_1",
                segments=[
                    TextSegment(
                        segment_id=f"segment_id_{i}",
                        segment_number=1
                    )
                    for i in range(1,6)
                ],
                sections=[],
                created_date="2025-03-16 04:40:54.757652",
                updated_date="2025-03-16 04:40:54.757652",
                published_date="2025-03-16 04:40:54.757652",
                published_by="pecha"
            )
            for i in range(1,6)
        ]
    )
    detail_table_of_content = DetailTableOfContent(
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
                published_date="2025-03-16 04:40:54.757652",
                published_by="pecha"
            )
            for i in range(1,6)
        ]
    )
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.SegmentUtils.validate_segment_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id", new_callable=AsyncMock) as mock_get_text_detail_by_id, \
        patch("pecha_api.texts.texts_service.TextUtils.get_table_of_content_id_and_respective_section_by_segment_id", new_callable=AsyncMock) as mock_get_table_of_content_by_content_id, \
        patch("pecha_api.texts.texts_service.get_sections_count_of_table_of_content", new_callable=AsyncMock) as mock_get_sections_count_of_table_of_content, \
        patch("pecha_api.texts.texts_service.SegmentUtils.get_mapped_segment_content_for_table_of_content", new_callable=AsyncMock) as mock_get_mapped_segment_content:
        mock_get_text_detail_by_id.return_value = text_detail
        mock_get_table_of_content_by_content_id.return_value = table_of_content
        mock_get_sections_count_of_table_of_content.return_value = 10
        mock_get_mapped_segment_content.return_value = detail_table_of_content
        response = await get_text_details_by_text_id(text_id="text_id_1", text_details_request=text_detail_request)
        assert response.text_detail == text_detail
        assert response.mapping == DetailTextMapping(
            segment_id="123e4567-e89b-12d3-a456-426614174000",
            section_id=None
        )
        assert response.skip == 0
        assert response.limit == 1
        assert response.total == 10
        assert response.content.sections == [
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
                    published_date="2025-03-16 04:40:54.757652",
                    published_by="pecha"
                )
                for i in range(1,6)
            ]
        assert response.content.id == "id_1"
        assert response.content.text_id == "text_id_1"
        assert response.content.sections[0].segments == [
                DetailTextSegment(
                    segment_id=f"segment_id_{i}",
                    segment_number=1,
                    content=f"content_{i}",
                    translation=None
                )
                for i in range(1,6)
            ]

@pytest.mark.asyncio
async def test_get_text_details_by_text_id_with_content_id_and_section_id_only_success():
    text_detail_request = TextDetailsRequest(
        content_id="content_id_1",
        section_id="section_id_1",
        skip=0,
        limit=1
    )
    text_detail = TextModel(
            id="id_1",
            title="text_1",
            language="bo",
            type="root_text",
            is_published=True,
            created_date="2025-03-16 04:40:54.757652",
            updated_date="2025-03-16 04:40:54.757652",
            published_date="2025-03-16 04:40:54.757652",
            published_by="pecha",
            categories=[],
            parent_id=None
        )
    table_of_content = TableOfContent(
        id="id_1",
        text_id="text_id_1",
        sections=[
            Section(
                id=f"id_{i}",
                title=f"section_{i}",
                section_number=i,
                parent_id="parent_id_1",
                segments=[
                    TextSegment(
                        segment_id=f"segment_id_{i}",
                        segment_number=1
                    )
                    for i in range(1,6)
                ],
                sections=[],
                created_date="2025-03-16 04:40:54.757652",
                updated_date="2025-03-16 04:40:54.757652",
                published_date="2025-03-16 04:40:54.757652",
                published_by="pecha"
            )
            for i in range(1,6)
        ]
    )
    detail_table_of_content = DetailTableOfContent(
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
                published_date="2025-03-16 04:40:54.757652",
                published_by="pecha"
            )
            for i in range(1,6)
        ]
    )
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.texts_service.TextUtils.get_text_detail_by_id", new_callable=AsyncMock) as mock_get_text_detail_by_id, \
        patch("pecha_api.texts.texts_service.get_table_of_content_by_content_id", new_callable=AsyncMock) as mock_get_table_of_content_by_content_id, \
        patch("pecha_api.texts.texts_service.get_sections_count_of_table_of_content", new_callable=AsyncMock) as mock_get_sections_count_of_table_of_content, \
        patch("pecha_api.texts.texts_service.SegmentUtils.get_mapped_segment_content_for_table_of_content", new_callable=AsyncMock) as mock_get_mapped_segment_content:
        mock_get_text_detail_by_id.return_value = text_detail
        mock_get_table_of_content_by_content_id.return_value = table_of_content
        mock_get_sections_count_of_table_of_content.return_value = 10
        mock_get_mapped_segment_content.return_value = detail_table_of_content
        response = await get_text_details_by_text_id(text_id="text_id_1", text_details_request=text_detail_request)
        assert response.text_detail == text_detail
        assert response.mapping == DetailTextMapping(
            segment_id=None,
            section_id="section_id_1"
        )
        assert response.skip == 0
        assert response.limit == 1
        assert response.total == 10
        assert response.content.sections == [
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
                    published_date="2025-03-16 04:40:54.757652",
                    published_by="pecha"
                )
                for i in range(1,6)
            ]
        assert response.content.id == "id_1"
        assert response.content.text_id == "text_id_1"
        assert response.content.sections[0].segments == [
                DetailTextSegment(
                    segment_id=f"segment_id_{i}",
                    segment_number=1,
                    content=f"content_{i}",
                    translation=None
                )
                for i in range(1,6)
            ]

@pytest.mark.asyncio
async def test_get_text_details_by_text_id_empty_text_id():
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exec_info:
            await get_text_details_by_text_id(text_id=None, text_details_request=TextDetailsRequest())
        assert exec_info.value.status_code == 400
        assert exec_info.value.detail == ErrorConstants.TEXT_OR_TERM_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_get_text_details_by_text_id_invalid_text_id():
    with patch("pecha_api.texts.texts_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exec_info:
            await get_text_details_by_text_id(text_id="invalid_id", text_details_request=TextDetailsRequest())
        assert exec_info.value.status_code == 404
        assert exec_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE


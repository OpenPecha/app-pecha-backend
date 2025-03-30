from unittest.mock import AsyncMock, patch
from fastapi import status, HTTPException

from pecha_api.terms.terms_response_models import TermsModel
import pytest
from pecha_api.texts.texts_service import create_new_text, get_versions_by_text_id
from pecha_api.texts.texts_response_models import CreateTextRequest, TextModel, Text, TextVersion, TextVersionResponse, \
    TableOfContent, Section, TextSegment, Translation, TextDetailsRequest, TableOfContentResponse
from pecha_api.texts.texts_service import get_text_by_text_id_or_term, TextsCategoryResponse, get_text_details_by_text_id, \
    validate_text_exits, validate_texts_exits, get_contents_by_text_id


@pytest.mark.asyncio
async def test_validate_text_exits_true():
    with patch('pecha_api.texts.texts_service.check_text_exists', return_value=True):
        response = await validate_text_exits(text_id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15")
        assert response == True


@pytest.mark.asyncio
async def test_validate_text_exits_false():
    with patch('pecha_api.texts.texts_service.check_text_exists', new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await validate_text_exits(text_id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15")
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Text not found"

@pytest.mark.asyncio
async def test_validate_texts_exits_true():
    with patch('pecha_api.texts.texts_service.check_all_text_exists', return_value=True):
        response = await validate_texts_exits(text_ids=["032b9a5f-0712-40d8-b7ec-73c8c94f1c15", "a48c0814-ce56-4ada-af31-f74b179b52a9"])
        assert response == True

@pytest.mark.asyncio
async def test_validate_texts_exits_true():
    with patch('pecha_api.texts.texts_service.check_all_text_exists', return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await validate_texts_exits(text_ids=["032b9a5f-0712-40d8-b7ec-73c8c94f1c15", "a48c0814-ce56-4ada-af31-f74b179b52a9"])
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Text not found"
        

@pytest.mark.asyncio
async def test_get_text_by_term_id():
    mock_term = AsyncMock(id="id_1", titles={"bo": "སྤྱོད་འཇུག"}, descriptions={"bo": "དུས་རབས་ ༨ པའི་ནང་སློབ་དཔོན་ཞི་བ་ལྷས་མཛད་པའི་རྩ་བ་དང་དེའི་འགྲེལ་བ་སོགས།"}, slug="bodhicaryavatara", has_sub_child=False)
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
                ),
                Text(
                    id="3111b8b4-d14a-4644-b99b-24fb5723c9f4",
                    title="སྤྱོད་འཇུག་དོན་བསྡུས།",
                    language="bo",
                    type="commentary",
                    is_published=True,
                    created_date="2025-03-21 09:41:11.276584",
                    updated_date="2025-03-21 09:41:11.276595",
                    published_date="2025-03-21 09:41:11.276599",
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
            title= "The Way of the Bodhisattva",
            parent_id= "032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
            priority= None,
            language= "en",
            type= "version",
            is_published= True,
            created_date= "2025-03-20 09:28:28.076920",
            updated_date= "2025-03-20 09:28:28.076934",
            published_date= "2025-03-20 09:28:28.076938",
            published_by= "pecha"
        ),
        TextVersion(
            id= "ee88cb8b-42b2-45af-a6a4-753c0e9d779c",
            title= "शबोधिचर्यावतार",
            parent_id= "032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
            priority= None,
            language= "sa",
            type= "version",
            is_published= True,
            created_date= "2025-03-20 09:29:51.154697",
            updated_date= "2025-03-20 09:29:51.154708",
            published_date= "2025-03-20 09:29:51.154712",
            published_by= "pecha"
        )
    ]
    with patch('pecha_api.texts.texts_service.get_texts_by_id', new_callable=AsyncMock) as mock_text_detail, \
        patch('pecha_api.texts.texts_service.get_versions_by_id', new_callable=AsyncMock) as mock_get_versions_by_text_id:
        mock_text_detail.return_value = text_detail
        mock_get_versions_by_text_id.return_value = versions_by_text_id
        response = await get_versions_by_text_id(text_id="id_1", skip=0, limit=10)
        assert response == TextVersionResponse(
            text=TextModel(
                id=text_detail.id,
                title=text_detail.title,
                language=text_detail.language,
                type=text_detail.type,
                is_published=text_detail.is_published,
                created_date=text_detail.created_date,
                updated_date=text_detail.updated_date,
                published_date=text_detail.published_date,
                published_by=text_detail.published_by,
                categories=text_detail.categories,
                parent_id=text_detail.parent_id
            ),
            versions=[
                TextVersion(
                    id=version.id,
                    title=version.title,
                    parent_id=version.parent_id,
                    priority=version.priority,
                    language=version.language,
                    type=version.type,
                    is_published=version.is_published,
                    created_date=version.created_date,
                    updated_date=version.updated_date,
                    published_date=version.published_date,
                    published_by=version.published_by
                )
                for version in versions_by_text_id
            ]
        )


@pytest.mark.asyncio
async def test_create_new_root_text():
    with patch('pecha_api.texts.texts_service.verify_admin_access', return_value=True), \
        patch('pecha_api.texts.texts_service.create_text', new_callable=AsyncMock) as mock_create_text:
        mock_create_text.return_value = AsyncMock(id="efb26a06-f373-450b-ba57-e7a8d4dd5b64", title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།", language="bo", parent_id=None, is_published=True, \
                                                 created_date="2025-03-16 04:40:54.757652", updated_date="2025-03-16 04:40:54.757652", published_date="2025-03-16 04:40:54.757652", \
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
async def test_get_text_details_by_text_id():
    text_request = TextDetailsRequest(
        content_id="content_id_1",
        version_id="version_id_1",
        skip=0,
        limit=10
    )
    text = TextModel(
        id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
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
    text_details = [
        TableOfContent(
            id="abh7u8e4-da52-4ea2-800e-3414emk8uy67",
            text_id="90i7u8e4-da52-4ea2-800e-3414emkki897",
            segments=[
                Section(
                    id="d19338e4-da52-4ea2-800e-3414eac8167e",
                    title="བྱང་གཏེར་དགོངས་པ་ཟང་ཐལ་གྱི་རྒྱུད་ཆེན་ལས་བྱུང་བའི་ཀུན་བཟང་སྨོན་ལམ་གྱི་རྣམ་བཤད། ཀུན་བཟང་ཉེ་ལམ་འོད་སྣང་གསལ་བའི་སྒྲོན་མ།",
                    section_number=1,
                    parent_id=None,
                    segments=[
                        TextSegment(
                            segment_id="2176yt56-51de-4a42-9d49-580b729dnb66",
                            segment_number=1,
                            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།",
                            translation=Translation(
                                text_id="version_id_1",
                                language="en",
                                content="비파시불, 시기불, 비사부불, <br>  구류손불, 구나함모니불, 가섭불, <br>  그리고 석가모니불 - 고타마, 모든 신들의 신께, <br>  이 일곱 용사 같은 부처님들께 예배드립니다!"
                            )
                        )
                    ],
                    sections=None,
                    created_date="2021-09-01T00:00:00.000Z",
                    updated_date="2021-09-01T00:00:00.000Z",
                    published_date="2021-09-01T00:00:00.000Z"
                )
            ]
        )
    ]
    with patch('pecha_api.texts.texts_service.check_text_exists', return_value=True), \
        patch('pecha_api.texts.texts_service.get_text_detail_by_id', new_callable=AsyncMock) as mock_get_text_detail_by_id, \
        patch('pecha_api.texts.texts_service.get_text_details', new_callable=AsyncMock) as mock_get_text_details:
        mock_get_text_detail_by_id.return_value = text
        mock_get_text_details.return_value = text_details
        response = await get_text_details_by_text_id(text_id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15", text_details_request=text_request)
        assert response == TableOfContentResponse(
            text_detail=text,
            contents=text_details
        )

@pytest.mark.asyncio
async def test_get_contents_by_text_id():
    text = TextModel(
        id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
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
    table_of_contents = [
        TableOfContent(
            id="abh7u8e4-da52-4ea2-800e-3414emk8uy67",
            text_id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
            segments=[
                Section(
                    id="d19338e4-da52-4ea2-800e-3414eac8167e",
                    title="A brief presentation of the ground path and result",
                    section_number=1,
                    parent_id=None,
                    created_date="2021-09-01T00:00:00.000Z",
                    updated_date="2021-09-01T00:00:00.000Z",
                    published_date="2021-09-01T00:00:00.000Z"
                ),
                Section(
                    id="b48dad38-da6d-45c3-ad12-97bca590769c",
                    title="The detailed explanation of the divisions of reality",
                    section_number=2,
                    parent_id=None,
                    sections=[
                        Section(
                            id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                            title="Basis",
                            section_number=1,
                            parent_id="b48dad38-da6d-45c3-ad12-97bca590769c",
                            created_date="2021-09-01T00:00:00.000Z",
                            updated_date="2021-09-01T00:00:00.000Z",
                            published_date="2021-09-01T00:00:00.000Z",
                            sections=[
                                Section(
                                    id="at8ujke7-8491-4cfe-9720-dac1acb967y7",
                                    title="The extensive explanation of the abiding nature of the ground",
                                    section_number=1,
                                    parent_id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                                    created_date="2021-09-01T00:00:00.000Z",
                                    updated_date="2021-09-01T00:00:00.000Z",
                                    published_date="2021-09-01T00:00:00.000Z"
                                )
                            ]
                        )
                    ],
                    created_date="2021-09-01T00:00:00.000Z",
                    updated_date="2021-09-01T00:00:00.000Z",
                    published_date="2021-09-01T00:00:00.000Z"
                )
            ]
        )
    ]
    with patch('pecha_api.texts.texts_service.check_text_exists', return_value=True), \
        patch('pecha_api.texts.texts_service.get_texts_by_id', new_callable=AsyncMock) as mock_get_text_detail_by_id, \
        patch('pecha_api.texts.texts_service.get_contents_by_id', new_callable=AsyncMock) as mock_get_contents_by_id:
        mock_get_contents_by_id.return_value = table_of_contents
        mock_get_text_detail_by_id.return_value = text
        response = await get_contents_by_text_id(text_id="032b9a5f-0712-40d8-b7ec-73c8c94f1c15", skip=0, limit=10)
        assert response == TableOfContentResponse(
            text_detail=text,
            contents=table_of_contents
        )
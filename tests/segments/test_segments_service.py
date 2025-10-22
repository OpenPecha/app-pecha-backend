import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
import uuid
import pytest
from pecha_api.texts.segments.segments_service import (
    create_new_segment,
    get_translations_by_segment_id,
    get_segment_details_by_id,
    get_commentaries_by_segment_id,
    get_info_by_segment_id,
    get_root_text_mapping_by_segment_id,
    remove_segments_by_text_id,
    fetch_segments_by_text_id,
    get_segments_details_by_ids
)
from pecha_api.texts.segments.segments_utils import SegmentUtils
from pecha_api.texts.segments.segments_response_models import (
    CreateSegmentRequest,
    SegmentResponse,
    CreateSegment,
    ParentSegment,
    SegmentTranslationsResponse,
    SegmentTranslation,
    SegmentDTO,
    MappingResponse,
    SegmentCommentariesResponse,
    SegmentCommentry,
    SegmentInfoResponse,
    SegmentInfo,
    RelatedText,
    Resources,
    SegmentRootMappingResponse,
    SegmentRootMapping
)

from pecha_api.texts.segments.segments_enum import SegmentType


from pecha_api.texts.texts_response_models import TextDTO

from pecha_api.error_contants import ErrorConstants
from pecha_api.cache.cache_enums import CacheType

@pytest.mark.asyncio
async def test_get_translations_by_segment_id_success():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    segment = SegmentDTO(
        id=segment_id,
        text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        content="To the buddhas: Vipaśyin,<br> Śikhin, Viśvabhū,<br>   Krakucchanda, Kanakamuni,<br> and Kāśyapa,<br>   And Śākyamuni—Gautama,<br> deity of all deities,   <br>To the seven warrior-like buddhas, I pay homage!",
        mapping=[],
        type=SegmentType.SOURCE
    )
    translations = [
        SegmentTranslation(
            segment_id=f"efb26a06-f373-450b-ba57-e7a8d4dd5b64_{i}",
            text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            title = f"Title {i}",
            source = f"source {i}",
            language = "en",
            content="To the buddhas: Vipaśyin,<br> Śikhin, Viśvabhū,<br>   Krakucchanda, Kanakamuni,<br> and Kāśyapa,<br>   And Śākyamuni—Gautama,<br> deity of all deities,   <br>To the seven warrior-like buddhas, I pay homage!",
        )
        for i in range(1, 4)
    ]
    with patch("pecha_api.texts.segments.segments_service.SegmentUtils.validate_segment_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.segments.segments_service.get_segment_by_id", new_callable=AsyncMock) as mock_segment, \
        patch("pecha_api.texts.segments.segments_service.SegmentUtils.filter_segment_mapping_by_type_or_text_id", new_callable=AsyncMock) as mock_filter, \
        patch("pecha_api.texts.segments.segments_service.get_related_mapped_segments", new_callable=AsyncMock) as mock_translations:
        mock_segment.return_value = segment
        mock_translations.return_value = translations
        mock_filter.return_value = translations

        response = await get_translations_by_segment_id(segment_id=segment_id)
        
        assert response == SegmentTranslationsResponse(
            parent_segment=ParentSegment(
                segment_id=segment_id,
                content="To the buddhas: Vipaśyin,<br> Śikhin, Viśvabhū,<br>   Krakucchanda, Kanakamuni,<br> and Kāśyapa,<br>   And Śākyamuni—Gautama,<br> deity of all deities,   <br>To the seven warrior-like buddhas, I pay homage!"
            ),
            translations=translations
        )


@pytest.mark.asyncio
async def test_get_translations_by_segment_id_segment_not_found():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"

    with patch("pecha_api.texts.segments.segments_service.SegmentUtils.validate_segment_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as excinfo:
            await get_translations_by_segment_id(segment_id=segment_id)
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_create_new_segment():
    """
    Test case for the create_new_segment function from the segments_service file
    """
    create_segment_request = CreateSegmentRequest(
        text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        segments=[
            CreateSegment(
                content="content", 
                mapping=[],
                type=SegmentType.SOURCE
            )
        ]
    )

    with patch('pecha_api.texts.segments.segments_service.validate_user_exists', return_value=True), \
        patch('pecha_api.texts.segments.segments_service.TextUtils.validate_text_exists', new_callable=AsyncMock, return_value=True), \
        patch('pecha_api.texts.segments.segments_service.create_segment', new_callable=AsyncMock) as mock_create_segment:
        mock_segment = type('Segment', (), {
            'id': uuid.UUID("efb26a06-f373-450b-ba57-e7a8d4dd5b64"),
            'text_id': "efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            'content': "content",
            'mapping': [],
            'type': SegmentType.SOURCE,
            'model_dump': lambda self: {
                'id': self.id,
                'text_id': self.text_id,
                'content': self.content,
                'mapping': self.mapping,
                'type': self.type
            }
        })()
        mock_create_segment.return_value = [mock_segment]
        
        response = await create_new_segment(
            create_segment_request=create_segment_request,
            token="admin"
        )
        
        expected_response = SegmentResponse(
            segments=[
                SegmentDTO(
                    id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
                    text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
                    content="content",
                    mapping=[],
                    type=SegmentType.SOURCE
                )
            ]
        )
        assert response == expected_response


@pytest.mark.asyncio
async def test_create_new_segment_invalid_user():
    """
    Test case for the create_new_segment function fails due to admin
    """
    create_segment_request = CreateSegmentRequest(
        text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        segments=[
            CreateSegment(
                content="content", 
                mapping=[],
                type=SegmentType.SOURCE
            )
        ]
    )

    with patch('pecha_api.texts.segments.segments_service.validate_user_exists', return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await create_new_segment(
                create_segment_request=create_segment_request,
                token="no_admin"
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

@pytest.mark.asyncio
async def test_validate_segment_exists_success():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch('pecha_api.texts.segments.segments_utils.check_segment_exists', new_callable=AsyncMock) as mock_check:
        mock_check.return_value = True
        result = await SegmentUtils.validate_segment_exists(segment_id)
        assert result is True

@pytest.mark.asyncio
async def test_validate_segment_exists_not_found():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch('pecha_api.texts.segments.segments_utils.check_segment_exists', new_callable=AsyncMock) as mock_check:
        mock_check.return_value = False
        with pytest.raises(HTTPException) as exc_info:
            await SegmentUtils.validate_segment_exists(segment_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_validate_segments_exists_success():
    segment_ids = ["efb26a06-f373-450b-ba57-e7a8d4dd5b64", "efb26a06-f373-450b-ba57-e7a8d4dd5b65"]
    with patch('pecha_api.texts.segments.segments_utils.check_all_segment_exists', new_callable=AsyncMock) as mock_check:
        mock_check.return_value = True
        result = await SegmentUtils.validate_segments_exists(segment_ids)
        assert result is True

@pytest.mark.asyncio
async def test_validate_segments_exists_not_found():
    segment_ids = ["efb26a06-f373-450b-ba57-e7a8d4dd5b64", "efb26a06-f373-450b-ba57-e7a8d4dd5b65"]
    with patch('pecha_api.texts.segments.segments_utils.check_all_segment_exists', new_callable=AsyncMock) as mock_check:
        mock_check.return_value = False
        with pytest.raises(HTTPException) as exc_info:
            await SegmentUtils.validate_segments_exists(segment_ids)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_get_segment_details_by_id_without_text_details_success():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    mock_segment = type('Segment', (), {
        'id': segment_id,
        'text_id': "text123",
        'content': "test content",
        'mapping': [],
        'type': SegmentType.SOURCE,
        'model_dump': lambda self: {
            'id': self.id,
            'text_id': self.text_id,
            'content': self.content,
            'mapping': self.mapping,
            'type': self.type
        }
    })()
    
    with patch('pecha_api.texts.segments.segments_service.get_segment_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_segment
        response = await get_segment_details_by_id(segment_id)
        assert isinstance(response, SegmentDTO)
        assert str(response.id) == segment_id
        assert response.text_id == "text123"
        assert response.content == "test content"
        assert response.mapping == []
        assert response.type == SegmentType.SOURCE

@pytest.mark.asyncio
async def test_get_segment_details_by_id_not_found():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch('pecha_api.texts.segments.segments_service.get_segment_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await get_segment_details_by_id(segment_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_get_segment_details_by_id_with_text_details_success():
    segment_id = str(uuid.uuid4())
    text_id = str(uuid.uuid4())
    group_id = str(uuid.uuid4())
    mock_text_details = TextDTO(
        id=text_id,
        title="title",
        language="en",
        type="text",
        group_id=group_id,
        is_published=True,
        created_date="2021-01-01",
        updated_date="2021-01-01",
        published_date="2021-01-01",
        published_by="admin",
        categories=["category1", "category2"],
        views=0
    )
    mock_segment = SegmentDTO(
        id=segment_id,
        text_id=text_id,
        content="test content",
        mapping=[],
        type=SegmentType.SOURCE,
        text=mock_text_details
    )
    with patch("pecha_api.texts.segments.segments_service.get_segment_by_id", new_callable=AsyncMock, return_value=mock_segment), \
        patch("pecha_api.texts.segments.segments_service.TextUtils.get_text_details_by_id", new_callable=AsyncMock, return_value=mock_text_details):

        response = await get_segment_details_by_id(segment_id=segment_id, text_details=True)
    
        assert response is not None
        assert response.text_id == text_id
        assert response.id == segment_id
        assert response.text is not None
        


@pytest.mark.asyncio
async def test_get_commentaries_by_segment_id_success():
    parent_segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    parent_segment = ParentSegment(
        segment_id=parent_segment_id,
        content="parent_segment_content"
    )
    commentaries = [
        SegmentDTO(
            id=f"id_{i}",
            text_id=f"text_id_{i}",
            content=f"content_{i}",
            mapping=[
                MappingResponse(
                    text_id="parent_text_id",
                    segments=[
                        parent_segment_id
                    ]
                )
            ],
            type=SegmentType.SOURCE
        )
        for i in range(1,6)
    ]
    filtered_commentaries = [
        SegmentCommentry(
            segment_id=f"id_{i}",
            text_id=f"text_id_{i}",
            title=f"title_{i}",
            content=f"content_{i}",
            language="en",
            count=1
        )
        for i in range(1,6)
    ]
    with patch("pecha_api.texts.segments.segments_service.SegmentUtils.validate_segment_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.segments.segments_service.get_segment_by_id", new_callable=AsyncMock) as mock_parent_segment, \
        patch("pecha_api.texts.segments.segments_service.get_related_mapped_segments", new_callable=AsyncMock) as mock_get_related_mapped_segment, \
        patch("pecha_api.texts.segments.segments_service.SegmentUtils.filter_segment_mapping_by_type_or_text_id", new_callable=AsyncMock) as mock_filtered_segment_mapping:
        mock_parent_segment.return_value = parent_segment
        mock_get_related_mapped_segment.return_value = commentaries
        mock_filtered_segment_mapping.return_value = filtered_commentaries
        response = await get_commentaries_by_segment_id(segment_id=parent_segment_id)
        assert isinstance(response, SegmentCommentariesResponse)
        assert response.parent_segment == parent_segment
        assert response.commentaries[0].text_id == "text_id_1"
        assert response.commentaries[0].content == "content_1"
        assert response.commentaries[0].language == "en"
        assert response.commentaries[0].count == 1


@pytest.mark.asyncio
async def test_get_commentaries_by_segment_id_not_found():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch("pecha_api.texts.segments.segments_service.SegmentUtils.validate_segment_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await get_commentaries_by_segment_id(segment_id=segment_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_get_infos_by_segment_id_success():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    related_mapped_segments = [
        SegmentDTO(
            id=f"id_{i}",
            text_id=f"text_id_{i}",
            content=f"content_{i}",
            mapping=[],
            type=SegmentType.SOURCE
        )
        for i in range(1,6)
    ]
    with patch("pecha_api.texts.segments.segments_service.SegmentUtils.validate_segment_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.segments.segments_service.get_related_mapped_segments", new_callable=AsyncMock) as mock_get_related_mapped_segment, \
        patch("pecha_api.texts.segments.segments_service.SegmentUtils.get_count_of_each_commentary_and_version", new_callable=AsyncMock, return_value={"version": 1, "commentary": 2}), \
        patch("pecha_api.texts.segments.segments_service.SegmentUtils.get_root_mapping_count", new_callable=AsyncMock, return_value=3):
        mock_get_related_mapped_segment.return_value = related_mapped_segments
        response = await get_info_by_segment_id(segment_id=segment_id)
        assert isinstance(response, SegmentInfoResponse)
        assert isinstance(response.segment_info, SegmentInfo)
        assert isinstance(response.segment_info.related_text, RelatedText)
        assert isinstance(response.segment_info.resources, Resources)
        assert response.segment_info.segment_id == segment_id
        assert response.segment_info.translations == 1
        assert response.segment_info.related_text.commentaries == 2
        assert response.segment_info.related_text.root_text == 3


@pytest.mark.asyncio
async def test_get_infos_by_segment_id_invalid_segment_id():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch("pecha_api.texts.segments.segments_service.SegmentUtils.validate_segment_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await get_info_by_segment_id(segment_id=segment_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_get_root_text_mapping_by_segment_id_success():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch("pecha_api.texts.segments.segments_service.SegmentUtils.validate_segment_exists", new_callable=AsyncMock, return_value=True), \
        patch("pecha_api.texts.segments.segments_service.get_segment_by_id", new_callable=AsyncMock) as mock_get_segment_by_id, \
        patch("pecha_api.texts.segments.segments_service.SegmentUtils.get_segment_root_mapping_details", new_callable=AsyncMock) as mock_get_segment_root_mapping_details:
        mock_get_segment_by_id.return_value = type('SegmentDTO', (), {
            'id': segment_id,
            'text_id': "efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            'content': "test content",
            'mapping': [],
            'type': SegmentType.SOURCE
        })
        mock_get_segment_root_mapping_details.return_value = [
            SegmentRootMapping(
                segment_id=f"id_{i}",
                text_id=f"text_id_{i}",
                title=f"title_{i}",
                content=f"content_{i}",
                language=f"language_{i}"
            )
            for i in range(1,6)
        ]
        response = await get_root_text_mapping_by_segment_id(segment_id=segment_id)
        assert isinstance(response, SegmentRootMappingResponse)
        assert isinstance(response.parent_segment, ParentSegment)
        assert isinstance(response.segment_root_mapping[0], SegmentRootMapping)
        assert response.parent_segment.segment_id == segment_id
        assert response.parent_segment.content == "test content"
        assert response.segment_root_mapping[0].segment_id == "id_1"
        assert response.segment_root_mapping[0].content == "content_1"
        assert response.segment_root_mapping[0].language == "language_1"
        assert response.segment_root_mapping[0].title == "title_1"
        assert response.segment_root_mapping[0].text_id == "text_id_1"

@pytest.mark.asyncio
async def test_get_root_text_mapping_by_segment_id_invalid_segment_id():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch("pecha_api.texts.segments.segments_service.SegmentUtils.validate_segment_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await get_root_text_mapping_by_segment_id(segment_id=segment_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE
        

@pytest.mark.asyncio
async def test_remove_segments_by_text_id_success():
    text_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch("pecha_api.texts.segments.segments_service.delete_segments_by_text_id", new_callable=AsyncMock, return_value=True),\
        patch("pecha_api.texts.segments.segments_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=True):
        
        response = await remove_segments_by_text_id(text_id=text_id)
        
        assert response is not None
    
@pytest.mark.asyncio
async def test_remove_segments_by_text_id_invalid_text_id():
    text_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch("pecha_api.texts.segments.segments_service.TextUtils.validate_text_exists", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await remove_segments_by_text_id(text_id=text_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_fetch_segments_by_text_id_success():
    text_id = "text_id"
    mock_segments = [
        SegmentDTO(
            id=f"id_{i}",
            text_id=f"{text_id}_{i}",
            content=f"content_{i}",
            mapping=[],
            type=SegmentType.SOURCE
        )
        for i in range(1,6)
    ]
    with patch("pecha_api.texts.segments.segments_service.get_segments_by_text_id", new_callable=AsyncMock, return_value=mock_segments):
        response = await fetch_segments_by_text_id(text_id=text_id)

        assert response is not None
        assert len(response) == 5
        assert response[0].id == "id_1"
        assert response[0].text_id == f"{text_id}_1"
        assert response[0].type == SegmentType.SOURCE


@pytest.mark.asyncio
async def test_get_segments_details_by_ids_cache_hit():
    segment_ids = ["id_1", "id_2"]
    cached = {
        "id_1": SegmentDTO(
            id="id_1", text_id="t1", content="c1", mapping=[], type=SegmentType.SOURCE
        ),
        "id_2": SegmentDTO(
            id="id_2", text_id="t2", content="c2", mapping=[], type=SegmentType.SOURCE
        ),
    }

    with patch(
        "pecha_api.texts.segments.segments_service.get_segments_details_by_ids_cache",
        new_callable=AsyncMock,
        return_value=cached,
    ) as mock_cache, patch(
        "pecha_api.texts.segments.segments_service.get_segments_by_ids",
        new_callable=AsyncMock,
    ) as mock_repo:
        result = await get_segments_details_by_ids(segment_ids)
        assert result == cached
        mock_cache.assert_awaited_once()
        mock_repo.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_segments_details_by_ids_cache_miss_sets_cache():
    segment_ids = ["id_1", "id_2"]
    repo_result = {
        "id_1": SegmentDTO(
            id="id_1", text_id="t1", content="c1", mapping=[], type=SegmentType.SOURCE
        ),
        "id_2": SegmentDTO(
            id="id_2", text_id="t2", content="c2", mapping=[], type=SegmentType.SOURCE
        ),
    }

    with patch(
        "pecha_api.texts.segments.segments_service.get_segments_details_by_ids_cache",
        new_callable=AsyncMock,
        return_value=None,
    ) as mock_cache, patch(
        "pecha_api.texts.segments.segments_service.get_segments_by_ids",
        new_callable=AsyncMock,
        return_value=repo_result,
    ) as mock_repo, patch(
        "pecha_api.texts.segments.segments_service.set_segments_details_by_ids_cache",
        new_callable=AsyncMock,
    ) as mock_set:
        result = await get_segments_details_by_ids(segment_ids)
        assert result == repo_result
        mock_cache.assert_awaited_once()
        mock_repo.assert_awaited_once_with(segment_ids=segment_ids)
        # ensure cache set called with expected segment_ids
        assert mock_set.await_count == 1
        called_kwargs = mock_set.await_args.kwargs
        assert called_kwargs["segment_ids"] == segment_ids


@pytest.mark.asyncio
async def test_get_info_by_segment_id_cache_hit():
    segment_id = "seg_1"
    cached_response = SegmentInfoResponse(
        segment_info=SegmentInfo(
            segment_id=segment_id,
            translations=0,
            related_text=RelatedText(commentaries=0, root_text=0),
            resources=Resources(sheets=0),
        )
    )

    with patch(
        "pecha_api.texts.segments.segments_service.SegmentUtils.validate_segment_exists",
        new_callable=AsyncMock,
        return_value=True,
    ), patch(
        "pecha_api.texts.segments.segments_service.get_segment_info_by_id_cache",
        new_callable=AsyncMock,
        return_value=cached_response,
    ) as mock_cache, patch(
        "pecha_api.texts.segments.segments_service.get_related_mapped_segments",
        new_callable=AsyncMock,
    ) as mock_related:
        result = await get_info_by_segment_id(segment_id)
        assert result == cached_response
        mock_cache.assert_awaited_once_with(segment_id=segment_id, cache_type=CacheType.SEGMENT_INFO)
        mock_related.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_info_by_segment_id_sets_cache_on_miss():
    segment_id = "seg_1"

    with patch(
        "pecha_api.texts.segments.segments_service.SegmentUtils.validate_segment_exists",
        new_callable=AsyncMock,
        return_value=True,
    ), patch(
        "pecha_api.texts.segments.segments_service.get_segment_info_by_id_cache",
        new_callable=AsyncMock,
        return_value=None,
    ), patch(
        "pecha_api.texts.segments.segments_service.get_related_mapped_segments",
        new_callable=AsyncMock,
        return_value=[],
    ), patch(
        "pecha_api.texts.segments.segments_service.SegmentUtils.get_count_of_each_commentary_and_version",
        new_callable=AsyncMock,
        return_value={"version": 0, "commentary": 0},
    ), patch(
        "pecha_api.texts.segments.segments_service.SegmentUtils.get_root_mapping_count",
        new_callable=AsyncMock,
        return_value=0,
    ), patch(
        "pecha_api.texts.segments.segments_service.set_segment_info_by_id_cache",
        new_callable=AsyncMock,
    ) as mock_set:
        result = await get_info_by_segment_id(segment_id)
        assert isinstance(result, SegmentInfoResponse)
        # ensure cache set was called with the built response
        assert mock_set.await_count == 1
        called_kwargs = mock_set.await_args.kwargs
        assert called_kwargs["segment_id"] == segment_id
        assert called_kwargs["cache_type"] == CacheType.SEGMENT_INFO

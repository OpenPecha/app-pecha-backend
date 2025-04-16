import uuid
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from pecha_api.texts.segments.segments_models import Segment
import pytest
from pecha_api.texts.segments.segments_service import (
    create_new_segment,
    get_translations_by_segment_id,
    get_segment_details_by_id
)
from pecha_api.texts.segments.segments_utils import SegmentUtils
from pecha_api.texts.segments.segments_response_models import CreateSegmentRequest, SegmentResponse, CreateSegment, \
    ParentSegment, SegmentTranslationsResponse, SegmentTranslation, SegmentDTO
from pecha_api.error_contants import ErrorConstants

@pytest.mark.asyncio
async def test_get_translations_by_segment_id_success():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    segment = SegmentDTO(
        id=segment_id,
        text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        content="To the buddhas: Vipaśyin,<br> Śikhin, Viśvabhū,<br>   Krakucchanda, Kanakamuni,<br> and Kāśyapa,<br>   And Śākyamuni—Gautama,<br> deity of all deities,   <br>To the seven warrior-like buddhas, I pay homage!",
        mapping=[]
    )
    translations = [
        SegmentTranslation(
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
            CreateSegment(content="content", mapping=[])
        ]
    )

    with patch('pecha_api.texts.segments.segments_service.verify_admin_access', return_value=True), \
        patch('pecha_api.texts.segments.segments_service.TextUtils.validate_text_exists', new_callable=AsyncMock, return_value=True), \
        patch('pecha_api.texts.segments.segments_service.create_segment', new_callable=AsyncMock) as mock_create_segment:
        mock_segment = type('Segment', (), {
            'id': uuid.UUID("efb26a06-f373-450b-ba57-e7a8d4dd5b64"),
            'text_id': "efb26a06-f373-450b-ba57-e7a8d4dd5b64",
            'content': "content",
            'mapping': [],
            'model_dump': lambda self: {
                'id': self.id,
                'text_id': self.text_id,
                'content': self.content,
                'mapping': self.mapping
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
                    mapping=[]
                )
            ]
        )
        assert response == expected_response


@pytest.mark.asyncio
async def test_create_new_segment_error_admin():
    """
    Test case for the create_new_segment function fails due to admin
    """
    create_segment_request = CreateSegmentRequest(
        text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
        segments=[
            CreateSegment(content="content", mapping=[])
        ]
    )

    with patch('pecha_api.texts.segments.segments_service.verify_admin_access', return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await create_new_segment(
                create_segment_request=create_segment_request,
                token="no_admin"
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == ErrorConstants.ADMIN_ERROR_MESSAGE

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
async def test_get_segment_details_by_id_success():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    mock_segment = type('Segment', (), {
        'id': segment_id,
        'text_id': "text123",
        'content': "test content",
        'mapping': [],
        'model_dump': lambda self: {
            'id': self.id,
            'text_id': self.text_id,
            'content': self.content,
            'mapping': self.mapping
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

@pytest.mark.asyncio
async def test_get_segment_details_by_id_not_found():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch('pecha_api.texts.segments.segments_service.get_segment_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await get_segment_details_by_id(segment_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE





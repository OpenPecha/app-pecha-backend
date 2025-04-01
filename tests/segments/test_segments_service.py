from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from pecha_api.texts.segments.segments_service import (
    create_new_segment,
    validate_segment_exists,
    validate_segments_exists,
    get_segment_details_by_id,
    get_translations_by_segment_id
)
from pecha_api.texts.segments.segments_response_models import (
    CreateSegmentRequest,
    SegmentResponse,
    CreateSegment
)
from pecha_api.error_contants import ErrorConstants

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
        patch('pecha_api.texts.segments.segments_service.validate_text_exits', new_callable=AsyncMock, return_value=True), \
        patch('pecha_api.texts.segments.segments_service.create_segment', new_callable=AsyncMock) as mock_create_segment:
        mock_segment_list = [
            SegmentResponse(
                id="efb26a06-f373-450b-ba57-e7a8d4dd5b64", 
                text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64", 
                content="content", 
                mapping=[]
            )
        ]
        mock_create_segment.return_value = mock_segment_list
        
        response = await create_new_segment(
            create_segment_request=create_segment_request,
            token="admin"
        )
        assert response == [
            SegmentResponse(
                id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
                text_id="efb26a06-f373-450b-ba57-e7a8d4dd5b64",
                content="content",
                mapping=[]
            )
        ]


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
    with patch('pecha_api.texts.segments.segments_service.check_segment_exists', new_callable=AsyncMock) as mock_check:
        mock_check.return_value = True
        result = await validate_segment_exists(segment_id)
        assert result is True

@pytest.mark.asyncio
async def test_validate_segment_exists_not_found():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch('pecha_api.texts.segments.segments_service.check_segment_exists', new_callable=AsyncMock) as mock_check:
        mock_check.return_value = False
        with pytest.raises(HTTPException) as exc_info:
            await validate_segment_exists(segment_id)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE

@pytest.mark.asyncio
async def test_validate_segments_exists_success():
    segment_ids = ["efb26a06-f373-450b-ba57-e7a8d4dd5b64", "efb26a06-f373-450b-ba57-e7a8d4dd5b65"]
    with patch('pecha_api.texts.segments.segments_service.check_all_segment_exists', new_callable=AsyncMock) as mock_check:
        mock_check.return_value = True
        result = await validate_segments_exists(segment_ids)
        assert result is True

@pytest.mark.asyncio
async def test_validate_segments_exists_not_found():
    segment_ids = ["efb26a06-f373-450b-ba57-e7a8d4dd5b64", "efb26a06-f373-450b-ba57-e7a8d4dd5b65"]
    with patch('pecha_api.texts.segments.segments_service.check_all_segment_exists', new_callable=AsyncMock) as mock_check:
        mock_check.return_value = False
        with pytest.raises(HTTPException) as exc_info:
            await validate_segments_exists(segment_ids)
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
        assert isinstance(response, SegmentResponse)
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

@pytest.mark.asyncio
async def test_get_translations_by_segment_id_success():
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
    mock_translations = []
    
    with patch('pecha_api.texts.segments.segments_service.get_segment_by_id', new_callable=AsyncMock) as mock_get_segment, \
         patch('pecha_api.texts.segments.segments_service.get_translations', new_callable=AsyncMock) as mock_get_translations:
        mock_get_segment.return_value = mock_segment
        mock_get_translations.return_value = mock_translations
        
        response = await get_translations_by_segment_id(segment_id, skip=0, limit=10)
        assert response.segment.segment_id == segment_id
        assert response.segment.segment_number == 1
        assert response.translations == []

@pytest.mark.asyncio
async def test_get_translations_by_segment_id_not_found():
    segment_id = "efb26a06-f373-450b-ba57-e7a8d4dd5b64"
    with patch('pecha_api.texts.segments.segments_service.get_segment_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await get_translations_by_segment_id(segment_id, skip=0, limit=10)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE
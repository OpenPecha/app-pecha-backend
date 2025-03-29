from unittest.mock import AsyncMock, patch
import pytest
from fastapi import HTTPException, status
import uuid

from pecha_api.texts.mappings.mappings_response_models import TextMappingRequest, MappingsModel
from pecha_api.texts.mappings.mappings_service import update_segment_mapping, validate_request_info
from pecha_api.texts.segments.segments_models import Segment, Mapping
from pecha_api.texts.segments.segments_response_models import SegmentResponse, MappingResponse

@pytest.mark.asyncio
async def test_update_segment_mapping_success():
    # Test data
    text_mapping_request = TextMappingRequest(
        text_id="2ff4215e-bc9e-4d16-8d7e-b4adea3c6ef9",
        segment_id="cce14575-ebc3-43aa-bcce-777676f3b2e2",
        mappings=[
            MappingsModel(
                parent_text_id="e55d66bc-0b2c-4575-afe1-c357856b1592",
                segments=[
                     "5bbe24b9-625e-41bf-b6aa-a949f26a7c05",
                    "83311e49-7e8b-413d-95c3-80d2cdea5158"
                ]
            )
        ]
    )
    
    mock_segment = Segment(
        id=uuid.UUID("cce14575-ebc3-43aa-bcce-777676f3b2e2"),
        text_id="2ff4215e-bc9e-4d16-8d7e-b4adea3c6ef9",
        content="test content",
        mapping=[
            Mapping(
                text_id="5bbe24b9-625e-41bf-b6aa-a949f26a7c05",
                segments=[
                    "5bbe24b9-625e-41bf-b6aa-a949f26a7c05",
                    "83311e49-7e8b-413d-95c3-80d2cdea5158"
                ]
            )
        ]
    )

    with patch('pecha_api.users.users_service.verify_admin_access', return_value=True), \
         patch('pecha_api.texts.mappings.mappings_service.validate_request_info', new_callable=AsyncMock), \
         patch('pecha_api.texts.mappings.mappings_service.update_mapping', new_callable=AsyncMock) as mock_update:
        
        mock_update.return_value = mock_segment
        
        response = await update_segment_mapping(text_mapping_request, token="admin-token")
        
        assert isinstance(response, SegmentResponse)
        assert response.id == "segment-123"
        assert response.text_id == "text-123"
        assert response.content == "test content"
        assert len(response.mapping) == 1
        assert response.mapping[0].text_id == "parent-text-123"
        assert response.mapping[0].segments == ["segment-456"]

@pytest.mark.asyncio
async def test_update_segment_mapping_unauthorized():
    text_mapping_request = TextMappingRequest(
        text_id="text-123",
        segment_id="segment-123",
        mappings=[
            MappingsModel(
                parent_text_id="parent-text-123",
                segments=["segment-456"]
            )
        ]
    )

    with patch('pecha_api.users.users_service.verify_admin_access', return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request, token="invalid-token")
            
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Admin access required"

@pytest.mark.asyncio
async def test_validate_request_info_success():
    mapping_request = TextMappingRequest(
        text_id="text-123",
        segment_id="segment-123",
        mappings=[
            MappingsModel(
                parent_text_id="parent-text-123",
                segments=["segment-456"]
            )
        ]
    )
    
    with patch('pecha_api.texts.texts_service.validate_text_exits', new_callable=AsyncMock) as mock_validate_text, \
         patch('pecha_api.texts.segments.segments_service.validate_segment_exists', new_callable=AsyncMock) as mock_validate_segment, \
         patch('pecha_api.texts.texts_service.validate_texts_exits', new_callable=AsyncMock) as mock_validate_texts, \
         patch('pecha_api.texts.segments.segments_service.validate_segments_exists', new_callable=AsyncMock) as mock_validate_segments:
        
        await validate_request_info(
            text_id=mapping_request.text_id,
            segment_id=mapping_request.segment_id,
            mappings=mapping_request.mappings
        )
        
        mock_validate_text.assert_called_once_with(text_id="text-123")
        mock_validate_segment.assert_called_once_with(segment_id="segment-123")
        mock_validate_texts.assert_called_once_with(text_ids=["parent-text-123"])
        mock_validate_segments.assert_called_once_with(segment_ids=["segment-456"])
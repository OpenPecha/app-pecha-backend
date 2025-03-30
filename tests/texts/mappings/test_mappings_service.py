from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from fastapi import HTTPException, status
import uuid
from datetime import datetime
from jose import jwt

from pecha_api.texts.mappings.mappings_response_models import TextMappingRequest, MappingsModel
from pecha_api.texts.mappings.mappings_service import update_segment_mapping, validate_request_info
from pecha_api.texts.segments.segments_models import Segment, Mapping
from pecha_api.texts.segments.segments_response_models import SegmentResponse, MappingResponse
from pecha_api.texts.texts_models import Text
from pecha_api.texts.texts_repository import check_text_exists
from pecha_api.config import get
from pecha_api.users.users_service import validate_token

@pytest.mark.asyncio
async def test_update_segment_mapping_success():
    """Test successful update of segment mapping with valid admin access and data"""
    # Arrange
    text_id = "8749b360-a55e-441c-b541-f7c6ba2f3c61"
    segment_id = "f7e14876-a3af-4652-8c84-8df2c046a105"
    parent_text_id = "c87aae38-ea7a-4d2b-ba0e-fd7dc61e68d1"
    parent_segment_id = "aca07f77-5906-4636-b7b5-edb7c9bbf1cf"
    
    mapping_request = TextMappingRequest(
        text_id=text_id,
        segment_id=segment_id,
        mappings=[
            MappingsModel(
                parent_text_id=parent_text_id,
                segments=[parent_segment_id]
            )
        ]
    )

    # Create a mock segment object instead of using Beanie model
    mock_segment = AsyncMock()
    mock_segment.id = uuid.UUID(segment_id)
    mock_segment.text_id = text_id
    mock_segment.content = "Test content"
    mock_segment.mapping = [Mapping(
        text_id=parent_text_id,
        segments=[parent_segment_id]
    )]

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True),\
            patch('pecha_api.texts.mappings.mappings_service.validate_request_info', new_callable=AsyncMock) as mock_validate,\
            patch('pecha_api.texts.mappings.mappings_service.update_mapping', new_callable=AsyncMock) as mock_update_mapping:
        
        # Set up mock returns
        mock_validate.return_value = True
        mock_update_mapping.return_value = mock_segment

        # Act
        response = await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")

        # Assert
        assert response is not None
        assert isinstance(response, SegmentResponse)
        assert str(response.id) == segment_id
        assert response.text_id == text_id
        assert response.content == "Test content"
        assert len(response.mapping) == 1
        assert response.mapping[0].text_id == parent_text_id
        assert response.mapping[0].segments == [parent_segment_id]

        # Verify function calls
        mock_validate.assert_awaited_once_with(
            text_id=text_id,
            segment_id=segment_id,
            mappings=mapping_request.mappings
        )
        mock_update_mapping.assert_awaited_once_with(
            text_id=text_id,
            segment_id=uuid.UUID(segment_id),
            mappings=[Mapping(text_id=parent_text_id, segments=[parent_segment_id])]
        )


@pytest.mark.asyncio
async def test_update_segment_mapping_non_admin():
    """Test update fails when user is not admin"""
    # Arrange
    mapping_request = TextMappingRequest(
        text_id="text-1",
        segment_id="segment-1",
        mappings=[MappingsModel(parent_text_id="parent-1", segments=["seg-1"])]
    )

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=False):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Admin access required"


@pytest.mark.asyncio
async def test_update_segment_mapping_invalid_text():
    """Test update fails when text ID doesn't exist"""
    # Arrange
    text_id = "invalid-text"
    segment_id = "f7e14876-a3af-4652-8c84-8df2c046a105"
    mapping_request = TextMappingRequest(
        text_id=text_id,
        segment_id=segment_id,
        mappings=[MappingsModel(parent_text_id="parent-1", segments=["seg-1"])]
    )

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True),\
            patch('pecha_api.texts.mappings.mappings_service.validate_request_info', side_effect=HTTPException(status_code=404, detail="Text not found")) as mock_validate:
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Text not found"
        mock_validate.assert_called_once()


@pytest.mark.asyncio
async def test_update_segment_mapping_invalid_segment():
    """Test update fails when segment ID doesn't exist"""
    # Arrange
    text_id = "text-1"
    segment_id = "invalid-segment"
    mapping_request = TextMappingRequest(
        text_id=text_id,
        segment_id=segment_id,
        mappings=[MappingsModel(parent_text_id="parent-1", segments=["seg-1"])]
    )

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True),\
            patch('pecha_api.texts.mappings.mappings_service.validate_request_info', side_effect=HTTPException(status_code=404, detail="Segment not found")) as mock_validate:
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Segment not found"
        mock_validate.assert_called_once()


@pytest.mark.asyncio
async def test_update_segment_mapping_text_and_parent_text_same_error():
    """Test update fails when parent text id contains the current text id"""
    # Arrange
    text_id = "text-1"
    segment_id = "segment-1"
    mapping_request = TextMappingRequest(
        text_id=text_id,
        segment_id=segment_id,
        mappings=[MappingsModel(parent_text_id=text_id, segments=["seg-1"])]
    )

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service.validate_request_info',
                  side_effect=HTTPException(status_code=400, detail="Mapping within same text not allowed")) as mock_validate:
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Mapping within same text not allowed"
        mock_validate.assert_called_once()

@pytest.mark.asyncio
async def test_update_segment_mapping_invalid_parent_text():
    """Test update fails when parent text ID doesn't exist"""
    # Arrange
    text_id = "text-1"
    segment_id = "segment-1"
    mapping_request = TextMappingRequest(
        text_id=text_id,
        segment_id=segment_id,
        mappings=[MappingsModel(parent_text_id="invalid-parent", segments=["seg-1"])]
    )

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True),\
            patch('pecha_api.texts.mappings.mappings_service.validate_request_info', side_effect=HTTPException(status_code=404, detail="Parent text not found")) as mock_validate:
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Parent text not found"
        mock_validate.assert_called_once()


@pytest.mark.asyncio
async def test_update_segment_mapping_invalid_parent_segment():
    """Test update fails when parent segment ID doesn't exist"""
    # Arrange
    text_id = "text-1"
    segment_id = "segment-1"
    mapping_request = TextMappingRequest(
        text_id=text_id,
        segment_id=segment_id,
        mappings=[MappingsModel(parent_text_id="parent-1", segments=["invalid-seg"])]
    )

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True),\
            patch('pecha_api.texts.mappings.mappings_service.validate_request_info', side_effect=HTTPException(status_code=404, detail="Parent segment not found")) as mock_validate:
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Parent segment not found"
        mock_validate.assert_called_once()


@pytest.mark.asyncio
async def test_validate_request_info_success():
    """Test validation succeeds with valid data"""
    # Arrange
    text_id = "text-1"
    segment_id = "segment-1"
    mappings = [MappingsModel(
        parent_text_id="parent-1",
        segments=["seg-1", "seg-2"]
    )]

    with patch('pecha_api.texts.mappings.mappings_service.validate_text_exits') as mock_validate_text,\
            patch('pecha_api.texts.mappings.mappings_service.validate_segment_exists') as mock_validate_segment,\
            patch('pecha_api.texts.mappings.mappings_service.validate_texts_exits') as mock_validate_texts,\
            patch('pecha_api.texts.mappings.mappings_service.validate_segments_exists') as mock_validate_segments:
        # Act
        result = await validate_request_info(text_id=text_id, segment_id=segment_id, mappings=mappings)

        # Assert
        assert result is True
        mock_validate_text.assert_awaited_once_with(text_id=text_id)
        mock_validate_segment.assert_awaited_once_with(segment_id=segment_id)
        mock_validate_texts.assert_awaited_once_with(text_ids=["parent-1"])
        mock_validate_segments.assert_awaited_once_with(segment_ids=["seg-1", "seg-2"])


@pytest.mark.asyncio
async def test_validate_request_info_invalid_text():
    """Test validation fails when text ID doesn't exist"""
    # Arrange
    text_id = "invalid-text"
    segment_id = "segment-1"
    mappings = [MappingsModel(parent_text_id="parent-1", segments=["seg-1"])]

    with patch('pecha_api.texts.mappings.mappings_service.validate_text_exits', side_effect=HTTPException(status_code=404, detail="Text not found")):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await validate_request_info(text_id=text_id, segment_id=segment_id, mappings=mappings)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Text not found"


@pytest.mark.asyncio
async def test_validate_request_info_invalid_segment():
    """Test validation fails when segment ID doesn't exist"""
    # Arrange
    text_id = "text-1"
    segment_id = "invalid-segment"
    mappings = [MappingsModel(parent_text_id="parent-1", segments=["seg-1"])]

    with patch('pecha_api.texts.mappings.mappings_service.validate_text_exits'),\
            patch('pecha_api.texts.mappings.mappings_service.validate_segment_exists', side_effect=HTTPException(status_code=404, detail="Segment not found")):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await validate_request_info(text_id=text_id, segment_id=segment_id, mappings=mappings)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Segment not found"


@pytest.mark.asyncio
async def test_validate_request_info_invalid_parent_text():
    """Test validation fails when parent text ID doesn't exist"""
    # Arrange
    text_id = "text-1"
    segment_id = "segment-1"
    mappings = [MappingsModel(parent_text_id="invalid-parent", segments=["seg-1"])]

    with patch('pecha_api.texts.mappings.mappings_service.validate_text_exits'),\
            patch('pecha_api.texts.mappings.mappings_service.validate_segment_exists'),\
            patch('pecha_api.texts.mappings.mappings_service.validate_texts_exits', side_effect=HTTPException(status_code=404, detail="Parent text not found")):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await validate_request_info(text_id=text_id, segment_id=segment_id, mappings=mappings)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Parent text not found"


@pytest.mark.asyncio
async def test_validate_request_info_invalid_parent_segment():
    """Test validation fails when parent segment ID doesn't exist"""
    # Arrange
    text_id = "text-1"
    segment_id = "segment-1"
    mappings = [MappingsModel(parent_text_id="parent-1", segments=["invalid-seg"])]

    with patch('pecha_api.texts.mappings.mappings_service.validate_text_exits'),\
            patch('pecha_api.texts.mappings.mappings_service.validate_segment_exists'),\
            patch('pecha_api.texts.mappings.mappings_service.validate_texts_exits'),\
            patch('pecha_api.texts.mappings.mappings_service.validate_segments_exists', side_effect=HTTPException(status_code=404, detail="Parent segment not found")):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await validate_request_info(text_id=text_id, segment_id=segment_id, mappings=mappings)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Parent segment not found"

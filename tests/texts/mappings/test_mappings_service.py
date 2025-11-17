from unittest.mock import AsyncMock, patch
import pytest
from fastapi import HTTPException, status
import uuid

from pecha_api.error_contants import ErrorConstants
from pecha_api.texts.mappings.mappings_response_models import TextMappingRequest, MappingsModel, TextMapping
from pecha_api.texts.mappings.mappings_service import update_segment_mapping
from pecha_api.texts.segments.segments_models import Mapping
from pecha_api.texts.segments.segments_response_models import SegmentResponse
from pecha_api.texts.segments.segments_enum import SegmentType


@pytest.mark.asyncio
async def test_update_segment_mapping_success():
    """Test successful update of segment mapping with valid admin access and data"""
    # Arrange
    text_id = "8749b360-a55e-441c-b541-f7c6ba2f3c61"
    segment_id = "f7e14876-a3af-4652-8c84-8df2c046a105"
    parent_text_id = "c87aae38-ea7a-4d2b-ba0e-fd7dc61e68d1"
    parent_segment_id = "aca07f77-5906-4636-b7b5-edb7c9bbf1cf"

    mapping_request = TextMappingRequest(
        text_mappings=[
            TextMapping(
                text_id=text_id,
                segment_id=segment_id,
                mappings=[
                    MappingsModel(
                        parent_text_id=parent_text_id,
                        segments=[parent_segment_id]
                    )
                ]
            )
        ]
    )

    # Create mock text objects
    mock_text = AsyncMock()
    mock_text.id = uuid.UUID(text_id)
    mock_text.pecha_text_id = text_id
    
    mock_parent_text = AsyncMock()
    mock_parent_text.id = uuid.UUID(parent_text_id)
    mock_parent_text.pecha_text_id = parent_text_id

    # Create mock segment objects
    mock_segment_obj = AsyncMock()
    mock_segment_obj.id = uuid.UUID(segment_id)
    mock_segment_obj.pecha_segment_id = segment_id
    
    mock_parent_segment_obj = AsyncMock()
    mock_parent_segment_obj.id = uuid.UUID(parent_segment_id)
    mock_parent_segment_obj.pecha_segment_id = parent_segment_id

    # Create a mock segment object instead of using Beanie model
    mock_updated_segment = AsyncMock()
    mock_updated_segment.id = uuid.UUID(segment_id)
    mock_updated_segment.pecha_segment_id = segment_id
    mock_updated_segment.text_id = text_id
    mock_updated_segment.content = "Test content"
    mock_updated_segment.type = SegmentType.SOURCE
    mock_updated_segment.mapping = [Mapping(
        text_id=parent_text_id,
        segments=[parent_segment_id]
    )]
    mock_segment = AsyncMock()
    mock_segment.id = uuid.UUID(segment_id)
    mock_segment.pecha_segment_id = segment_id
    mock_segment.text_id = text_id
    mock_segment.content = "Test content"
    mock_segment.mapping = []
    mock_segment.type = SegmentType.SOURCE

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service.get_text_by_pecha_text_id', new_callable=AsyncMock) as mock_get_text, \
            patch('pecha_api.texts.mappings.mappings_service.get_segments_by_pecha_segment_ids', new_callable=AsyncMock) as mock_get_segments_by_pecha_ids, \
            patch('pecha_api.texts.mappings.mappings_service._validate_mapping_request', new_callable=AsyncMock, return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service.get_segments_by_ids', new_callable=AsyncMock) as mock_get_segments_by_ids, \
            patch('pecha_api.texts.mappings.mappings_service.update_mappings', new_callable=AsyncMock) as mock_update_mappings:
        # Set up mock returns for pecha ID lookups
        def get_text_side_effect(pecha_text_id):
            if pecha_text_id == text_id:
                return mock_text
            elif pecha_text_id == parent_text_id:
                return mock_parent_text
            return None
        
        def get_segments_side_effect(pecha_segment_ids):
            if isinstance(pecha_segment_ids, str):
                pecha_segment_ids = [pecha_segment_ids]
            if segment_id in pecha_segment_ids:
                return [mock_segment_obj]
            elif parent_segment_id in pecha_segment_ids:
                return [mock_parent_segment_obj]
            return []
        
        mock_get_text.side_effect = get_text_side_effect
        mock_get_segments_by_pecha_ids.side_effect = get_segments_side_effect
        mock_get_segments_by_ids.return_value = [mock_segment]
        mock_update_mappings.return_value = [mock_updated_segment]

        # Act
        response = await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")

        # Assert
        assert response is not None
        assert isinstance(response, SegmentResponse)
        segment_dto = response.segments[0]
        assert str(segment_dto.id) == segment_id
        assert segment_dto.text_id == text_id
        assert segment_dto.content == "Test content"
        assert len(segment_dto.mapping) == 1
        assert segment_dto.mapping[0].text_id == parent_text_id
        assert segment_dto.mapping[0].segments == [parent_segment_id]


@pytest.mark.asyncio
async def test_update_segment_mapping_non_admin():
    """Test update fails when user is not admin"""
    # Arrange
    mapping_request = TextMappingRequest(
        text_mappings=[
            TextMapping(
                text_id="text-1",
                segment_id="segment-1",
                mappings=[MappingsModel(parent_text_id="parent-1", segments=["seg-1"])]
            )
        ]
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
        text_mappings=[
            TextMapping(
                text_id=text_id,
                segment_id=segment_id,
                mappings=[MappingsModel(parent_text_id="parent-1", segments=["seg-1"])]
            )
        ]
    )

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service.get_text_by_pecha_text_id', new_callable=AsyncMock, return_value=None):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE


@pytest.mark.asyncio
async def test_update_segment_mapping_invalid_segment():
    """Test update fails when segment ID doesn't exist"""
    # Arrange
    text_id = "8749b360-a55e-441c-b541-f7c6ba2f3c61"
    segment_id = "invalid-segment"
    mapping_request = TextMappingRequest(
        text_mappings=[
            TextMapping(
                text_id=text_id,
                segment_id=segment_id,
                mappings=[MappingsModel(parent_text_id="parent-1", segments=["seg-1"])]
            )
        ]
    )

    # Create mock text object
    mock_text = AsyncMock()
    mock_text.id = uuid.UUID(text_id)
    mock_text.pecha_text_id = text_id

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service.get_text_by_pecha_text_id', new_callable=AsyncMock, return_value=mock_text), \
            patch('pecha_api.texts.mappings.mappings_service.get_segments_by_pecha_segment_ids', new_callable=AsyncMock, return_value=[]):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE


@pytest.mark.asyncio
async def test_update_segment_mapping_text_and_parent_text_same_error():
    """Test update fails when parent text id contains the current text id"""
    # Arrange
    text_id = "8749b360-a55e-441c-b541-f7c6ba2f3c61"
    segment_id = "f7e14876-a3af-4652-8c84-8df2c046a105"
    parent_segment_id = "aca07f77-5906-4636-b7b5-edb7c9bbf1cf"
    
    mapping_request = TextMappingRequest(
        text_mappings=[
            TextMapping(
                text_id=text_id,
                segment_id=segment_id,
                mappings=[MappingsModel(parent_text_id=text_id, segments=[parent_segment_id])]
            )
        ]
    )

    # Create mock text object (same for both text and parent)
    mock_text = AsyncMock()
    mock_text.id = uuid.UUID(text_id)
    mock_text.pecha_text_id = text_id

    # Create mock segment objects
    mock_segment_obj = AsyncMock()
    mock_segment_obj.id = uuid.UUID(segment_id)
    mock_segment_obj.pecha_segment_id = segment_id
    
    mock_parent_segment_obj = AsyncMock()
    mock_parent_segment_obj.id = uuid.UUID(parent_segment_id)
    mock_parent_segment_obj.pecha_segment_id = parent_segment_id

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service.get_text_by_pecha_text_id', new_callable=AsyncMock, return_value=mock_text), \
            patch('pecha_api.texts.mappings.mappings_service.get_segments_by_pecha_segment_ids', new_callable=AsyncMock) as mock_get_segments, \
            patch('pecha_api.texts.texts_utils.check_text_exists', new_callable=AsyncMock, return_value=True), \
            patch('pecha_api.texts.segments.segments_utils.check_segment_exists', new_callable=AsyncMock, return_value=True), \
            patch('pecha_api.texts.segments.segments_utils.check_all_segment_exists', new_callable=AsyncMock, return_value=True), \
            patch('pecha_api.texts.texts_utils.check_all_text_exists', new_callable=AsyncMock, return_value=True):
        
        def get_segments_side_effect(pecha_segment_ids):
            if isinstance(pecha_segment_ids, str):
                pecha_segment_ids = [pecha_segment_ids]
            if segment_id in pecha_segment_ids:
                return [mock_segment_obj]
            elif parent_segment_id in pecha_segment_ids:
                return [mock_parent_segment_obj]
            return []
        
        mock_get_segments.side_effect = get_segments_side_effect
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == ErrorConstants.SAME_TEXT_MAPPING_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_update_segment_mapping_invalid_parent_text():
    """Test update fails when parent text ID doesn't exist"""
    # Arrange
    text_id = "8749b360-a55e-441c-b541-f7c6ba2f3c61"
    segment_id = "f7e14876-a3af-4652-8c84-8df2c046a105"
    invalid_parent_text_id = "invalid-parent"
    
    mapping_request = TextMappingRequest(
        text_mappings=[
            TextMapping(
                text_id=text_id,
                segment_id=segment_id,
                mappings=[MappingsModel(parent_text_id=invalid_parent_text_id, segments=["seg-1"])]
            )
        ]
    )

    # Create mock text object
    mock_text = AsyncMock()
    mock_text.id = uuid.UUID(text_id)
    mock_text.pecha_text_id = text_id

    # Create mock segment object
    mock_segment_obj = AsyncMock()
    mock_segment_obj.id = uuid.UUID(segment_id)
    mock_segment_obj.pecha_segment_id = segment_id

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service.get_text_by_pecha_text_id', new_callable=AsyncMock) as mock_get_text, \
            patch('pecha_api.texts.mappings.mappings_service.get_segments_by_pecha_segment_ids', new_callable=AsyncMock, return_value=[mock_segment_obj]):
        
        def get_text_side_effect(pecha_text_id):
            if pecha_text_id == text_id:
                return mock_text
            return None
        
        mock_get_text.side_effect = get_text_side_effect
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE


@pytest.mark.asyncio
async def test_update_segment_mapping_invalid_parent_segment():
    """Test update fails when parent segment ID doesn't exist"""
    # Arrange
    text_id = "8749b360-a55e-441c-b541-f7c6ba2f3c61"
    segment_id = "f7e14876-a3af-4652-8c84-8df2c046a105"
    parent_text_id = "c87aae38-ea7a-4d2b-ba0e-fd7dc61e68d1"
    invalid_parent_segment = "invalid-seg"
    
    mapping_request = TextMappingRequest(
        text_mappings=[
            TextMapping(
                text_id=text_id,
                segment_id=segment_id,
                mappings=[MappingsModel(parent_text_id=parent_text_id, segments=[invalid_parent_segment])]
            )]
    )

    # Create mock text objects
    mock_text = AsyncMock()
    mock_text.id = uuid.UUID(text_id)
    mock_text.pecha_text_id = text_id
    
    mock_parent_text = AsyncMock()
    mock_parent_text.id = uuid.UUID(parent_text_id)
    mock_parent_text.pecha_text_id = parent_text_id

    # Create mock segment object
    mock_segment_obj = AsyncMock()
    mock_segment_obj.id = uuid.UUID(segment_id)
    mock_segment_obj.pecha_segment_id = segment_id

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service.get_text_by_pecha_text_id', new_callable=AsyncMock) as mock_get_text, \
            patch('pecha_api.texts.mappings.mappings_service.get_segments_by_pecha_segment_ids', new_callable=AsyncMock) as mock_get_segments:
        
        def get_text_side_effect(pecha_text_id):
            if pecha_text_id == text_id:
                return mock_text
            elif pecha_text_id == parent_text_id:
                return mock_parent_text
            return None
        
        def get_segments_side_effect(pecha_segment_ids):
            if isinstance(pecha_segment_ids, str):
                pecha_segment_ids = [pecha_segment_ids]
            if segment_id in pecha_segment_ids:
                return [mock_segment_obj]
            return []
        
        mock_get_text.side_effect = get_text_side_effect
        mock_get_segments.side_effect = get_segments_side_effect
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE


@pytest.mark.asyncio
async def test_update_segment_mapping_error_400():
    """Test update fails when update_mappings returns None"""
    # Arrange
    text_id = "8749b360-a55e-441c-b541-f7c6ba2f3c61"
    segment_id = "f7e14876-a3af-4652-8c84-8df2c046a105"
    parent_text_id = "c87aae38-ea7a-4d2b-ba0e-fd7dc61e68d1"
    parent_segment_id = "aca07f77-5906-4636-b7b5-edb7c9bbf1cf"

    mapping_request = TextMappingRequest(
        text_mappings=[
            TextMapping(
                text_id=text_id,
                segment_id=segment_id,
                mappings=[
                    MappingsModel(
                        parent_text_id=parent_text_id,
                        segments=[parent_segment_id]
                    )
                ]
            )]
    )

    # Create mock text objects
    mock_text = AsyncMock()
    mock_text.id = uuid.UUID(text_id)
    mock_text.pecha_text_id = text_id
    
    mock_parent_text = AsyncMock()
    mock_parent_text.id = uuid.UUID(parent_text_id)
    mock_parent_text.pecha_text_id = parent_text_id

    # Create mock segment objects
    mock_segment_obj = AsyncMock()
    mock_segment_obj.id = uuid.UUID(segment_id)
    mock_segment_obj.pecha_segment_id = segment_id
    
    mock_parent_segment_obj = AsyncMock()
    mock_parent_segment_obj.id = uuid.UUID(parent_segment_id)
    mock_parent_segment_obj.pecha_segment_id = parent_segment_id

    mock_segment = AsyncMock()
    mock_segment.id = uuid.UUID(segment_id)
    mock_segment.pecha_segment_id = segment_id
    mock_segment.text_id = text_id
    mock_segment.content = "Test content"
    mock_segment.mapping = []
    mock_segment.type = SegmentType.SOURCE

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service.get_text_by_pecha_text_id', new_callable=AsyncMock) as mock_get_text, \
            patch('pecha_api.texts.mappings.mappings_service.get_segments_by_pecha_segment_ids', new_callable=AsyncMock) as mock_get_segments_by_pecha_ids, \
            patch('pecha_api.texts.mappings.mappings_service._validate_mapping_request', new_callable=AsyncMock, return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service.get_segments_by_ids', new_callable=AsyncMock) as mock_get_segments_by_ids, \
            patch('pecha_api.texts.mappings.mappings_service.update_mappings', new_callable=AsyncMock) as mock_update_mappings:
        
        # Set up mock returns for pecha ID lookups
        def get_text_side_effect(pecha_text_id):
            if pecha_text_id == text_id:
                return mock_text
            elif pecha_text_id == parent_text_id:
                return mock_parent_text
            return None
        
        def get_segments_side_effect(pecha_segment_ids):
            if isinstance(pecha_segment_ids, str):
                pecha_segment_ids = [pecha_segment_ids]
            if segment_id in pecha_segment_ids:
                return [mock_segment_obj]
            elif parent_segment_id in pecha_segment_ids:
                return [mock_parent_segment_obj]
            return []
        
        mock_get_text.side_effect = get_text_side_effect
        mock_get_segments_by_pecha_ids.side_effect = get_segments_side_effect
        mock_get_segments_by_ids.return_value = [mock_segment]
        mock_update_mappings.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == ErrorConstants.SEGMENT_MAPPING_ERROR_MESSAGE
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

    # Create a mock segment object instead of using Beanie model
    mock_updated_segment = AsyncMock()
    mock_updated_segment.id = uuid.UUID(segment_id)
    mock_updated_segment.text_id = text_id
    mock_updated_segment.content = "Test content"
    mock_updated_segment.type = SegmentType.SOURCE
    mock_updated_segment.mapping = [Mapping(
        text_id=parent_text_id,
        segments=[parent_segment_id]
    )]
    mock_segment = AsyncMock()
    mock_segment.id = uuid.UUID(segment_id)
    mock_segment.text_id = text_id
    mock_segment.content = "Test content"
    mock_segment.mapping = []
    mock_segment.type = SegmentType.SOURCE

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service._validate_mapping_request', new_callable=AsyncMock, return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service.get_segments_by_ids', new_callable=AsyncMock) as mock_get_segments_by_ids, \
            patch('pecha_api.texts.mappings.mappings_service.update_mappings', new_callable=AsyncMock) as mock_update_mappings:
        # Set up mock returns
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
            patch('pecha_api.texts.mappings.mappings_service._validate_mapping_request',
                  side_effect=HTTPException(status_code=404, detail="Text not found")) as mock_validate:
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
        text_mappings=[
            TextMapping(
                text_id=text_id,
                segment_id=segment_id,
                mappings=[MappingsModel(parent_text_id="parent-1", segments=["seg-1"])]
            )
        ]
    )

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service._validate_mapping_request',
                  side_effect=HTTPException(status_code=404, detail="Segment not found")) as mock_validate:
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
        text_mappings=[
            TextMapping(
                text_id=text_id,
                segment_id=segment_id,
                mappings=[MappingsModel(parent_text_id=text_id, segments=["seg-1"])]
            )
        ]
    )

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service._validate_mapping_request',
                  side_effect=HTTPException(status_code=400,
                                            detail="Mapping within same text not allowed")) as mock_validate:
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
        text_mappings=[
            TextMapping(
                text_id=text_id,
                segment_id=segment_id,
                mappings=[MappingsModel(parent_text_id="invalid-parent", segments=["seg-1"])]
            )
        ]
    )

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service._validate_mapping_request',
                  side_effect=HTTPException(status_code=404, detail="Parent text not found")) as mock_validate:
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
        text_mappings=[
            TextMapping(
                text_id=text_id,
                segment_id=segment_id,
                mappings=[MappingsModel(parent_text_id="parent-1", segments=["invalid-seg"])]
            )]
    )

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service._validate_mapping_request',
                  side_effect=HTTPException(status_code=404, detail="Parent segment not found")) as mock_validate:
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Parent segment not found"
        mock_validate.assert_called_once()


@pytest.mark.asyncio
async def test_update_segment_mapping_error_400():
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
            )]
    )
    mock_segment = AsyncMock()
    mock_segment.id = uuid.UUID(segment_id)
    mock_segment.text_id = text_id
    mock_segment.content = "Test content"
    mock_segment.mapping = []
    mock_segment.type = SegmentType.SOURCE

    with patch('pecha_api.texts.mappings.mappings_service.verify_admin_access', return_value=True), \
            patch('pecha_api.texts.mappings.mappings_service._validate_mapping_request', new_callable=AsyncMock, return_value=True) as mock_validate, \
            patch('pecha_api.texts.mappings.mappings_service.get_segments_by_ids', new_callable=AsyncMock) as mock_get_segments_by_ids, \
            patch('pecha_api.texts.mappings.mappings_service.update_mappings',
                  new_callable=AsyncMock) as mock_update_mappings:
        # Set up mock returns
        mock_get_segments_by_ids.return_value = [mock_segment]
        mock_update_mappings.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_segment_mapping(text_mapping_request=mapping_request, token="Bearer token")

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == ErrorConstants.SEGMENT_MAPPING_ERROR_MESSAGE
        mock_validate.assert_called_once()
from unittest.mock import AsyncMock, patch
import pytest
from typing import List, Dict
from fastapi import HTTPException
from starlette import status
from pecha_api.error_contants import ErrorConstants

from pecha_api.texts.groups.groups_service import (
    validate_group_exists,
    get_groups_by_list_of_ids,
    get_group_details,
    create_new_group
)

from pecha_api.texts.groups.groups_response_models import (
    GroupDTO,
    CreateGroupRequest
)

@pytest.mark.asyncio
async def test_validate_group_exists_success():
    group_id = "4d2f3498-3cc6-4bc6-9beb-37d2f7dc0163"
    with patch("pecha_api.texts.groups.groups_service.check_group_exists", new_callable=AsyncMock, return_value=True):
        response = await validate_group_exists(group_id=group_id)
        assert response == True

@pytest.mark.asyncio
async def test_validate_group_exists_invalid_group_id():
    group_id = "invalid_group_id"
    with patch("pecha_api.texts.groups.groups_service.check_group_exists", new_callable=AsyncMock, return_value=False):
        response = await validate_group_exists(group_id=group_id)
        assert response == False
    
@pytest.mark.asyncio
async def test_get_list_of_group_details_success():
    group_ids: List[str] = [
        "4d2f3498-3cc6-4bc6-9beb-37d2f7dc0163",
        "4d2f3498-3cc6-4bc6-9beb-37d2f7dc0164"
    ]
    group_details = {
        group_ids[0]: GroupDTO(
            id=group_ids[0],
            type="version"
        ),
        group_ids[1]: GroupDTO(
            id=group_ids[1],
            type="commentary"
        )
    }
    with patch("pecha_api.texts.groups.groups_service.get_groups_by_ids", new_callable=AsyncMock) as mock_group_details:
        mock_group_details.return_value = group_details
        response = await get_groups_by_list_of_ids(group_ids=group_ids)
        assert isinstance(response[group_ids[0]], GroupDTO)
        assert response[group_ids[0]].id == group_ids[0]
        assert response[group_ids[0]].type == "version"
    
@pytest.mark.asyncio
async def test_get_group_details_success():
    group_id = "4d2f3498-3cc6-4bc6-9beb-37d2f7dc0163"
    group_details = GroupDTO(
        id=group_id,
        type="version"
    )
    with patch("pecha_api.texts.groups.groups_service.get_group_by_id", new_callable=AsyncMock) as mock_group_details:
        mock_group_details.return_value = group_details
        response = await get_group_details(group_id=group_id)
        assert response.id == group_id
        assert response.type == "version"
    
@pytest.mark.asyncio
async def test_get_group_details_invalid_group_id():
    group_id = "invalid_group_id"
    with patch("pecha_api.texts.groups.groups_service.get_group_by_id", new_callable=AsyncMock) as mock_group_details:
        mock_group_details.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await get_group_details(group_id=group_id)
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == ErrorConstants.INVALID_UUID_MESSAGE
        
@pytest.mark.asyncio
async def test_get_group_details_invalid_uuid():
    group_id = "invalid_uuid"
    with patch("pecha_api.texts.groups.groups_service.get_group_by_id", new_callable=AsyncMock) as mock_group_details:
        mock_group_details.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await get_group_details(group_id=group_id)
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == ErrorConstants.INVALID_UUID_MESSAGE

@pytest.mark.asyncio
async def test_create_new_group_success():
    create_group_request = CreateGroupRequest(
        type="version"
    )
    group_details: GroupDTO = GroupDTO(
        id="4d2f3498-3cc6-4bc6-9beb-37d2f7dc0163",
        type="version"
    )
    with patch("pecha_api.texts.groups.groups_service.verify_admin_access", return_value=True), \
        patch("pecha_api.texts.groups.groups_service.create_group", new_callable=AsyncMock) as mock_create_group:
        mock_create_group.return_value = group_details
        response = await create_new_group(create_group_request=create_group_request, token="admin_token")
        assert response.id == "4d2f3498-3cc6-4bc6-9beb-37d2f7dc0163"
        assert response.type == create_group_request.type.value

@pytest.mark.asyncio
async def test_create_new_group_not_admin():
    create_group_request = CreateGroupRequest(
        type="version"
    )
    with patch("pecha_api.texts.groups.groups_service.verify_admin_access", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await create_new_group(create_group_request=create_group_request, token="admin_token")
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert exc_info.value.detail == ErrorConstants.ADMIN_ERROR_MESSAGE
import pytest
import uuid
from unittest.mock import patch

from pecha_api.plans.users.recitation.plan_user_recitation_response_models import CreateUserRecitationRequest
from pecha_api.plans.users.recitation.plan_user_recitation_views import create_user_recitation, delete_user_recitation


class _Creds:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_create_user_recitation_success():
    """Test successful user recitation creation"""
    recitation_id = uuid.uuid4()
    request = CreateUserRecitationRequest(recitation_id=recitation_id)

    creds = _Creds(token="token123")

    with patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_views.create_user_recitation_service",
        return_value=None,
    ) as mock_create:
        resp = create_user_recitation(
            authentication_credential=creds,
            create_user_recitation_request=request,
        )

        assert mock_create.call_count == 1
        assert mock_create.call_args.kwargs == {
            "token": "token123",
            "create_user_recitation_request": request,
        }

        assert resp is None


@pytest.mark.asyncio
async def test_create_user_recitation_with_different_recitation_id():
    """Test user recitation creation with different recitation ID"""
    different_recitation_id = uuid.uuid4()
    request = CreateUserRecitationRequest(recitation_id=different_recitation_id)

    creds = _Creds(token="valid_token")

    with patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_views.create_user_recitation_service",
        return_value=None,
    ) as mock_create:
        resp = create_user_recitation(
            authentication_credential=creds,
            create_user_recitation_request=request,
        )

        assert mock_create.call_count == 1
        assert mock_create.call_args.kwargs["token"] == "valid_token"
        assert mock_create.call_args.kwargs["create_user_recitation_request"].recitation_id == different_recitation_id
        assert resp is None

@pytest.mark.asyncio
async def test_delete_user_recitation_success():
    """Test successful user recitation deletion"""
    recitation_id = uuid.uuid4()
    creds = _Creds(token="token123")

    with patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_views.delete_user_recitation_service",
        return_value=None,
    ) as mock_delete:
        resp = delete_user_recitation(
            authentication_credential=creds,
            recitation_id=recitation_id,
        )

        assert mock_delete.call_count == 1
        assert mock_delete.call_args.kwargs == {
            "token": "token123",
            "recitation_id": recitation_id,
        }

        assert resp is None


@pytest.mark.asyncio
async def test_delete_user_recitation_with_different_recitation_id():
    """Test user recitation deletion with different recitation ID"""
    different_recitation_id = uuid.uuid4()
    creds = _Creds(token="valid_token")

    with patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_views.delete_user_recitation_service",
        return_value=None,
    ) as mock_delete:
        resp = delete_user_recitation(
            authentication_credential=creds,
            recitation_id=different_recitation_id,
        )

        assert mock_delete.call_count == 1
        assert mock_delete.call_args.kwargs["token"] == "valid_token"
        assert mock_delete.call_args.kwargs["recitation_id"] == different_recitation_id
        assert resp is None

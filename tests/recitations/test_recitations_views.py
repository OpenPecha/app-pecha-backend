import pytest
import uuid
from unittest.mock import patch, AsyncMock

from pecha_api.recitations.recitations_response_models import CreateRecitationsRequest
from pecha_api.recitations.recitations_view import create_recitations


class _Creds:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_create_recitation_success():
    """Test successful recitation creation"""
    request = CreateRecitationsRequest(
        title="Test Recitation",
        audio_url="https://example.com/audio.mp3",
        text_id=uuid.uuid4(),
        content={"text": "Sample recitation content", "language": "en"}
    )

    creds = _Creds(token="token123")

    with patch(
        "pecha_api.plans.recitation.plan_recitation_view.create_recitation_service",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_create:
        resp = await create_recitations(
            authentication_credential=creds,
            create_recitation_request=request,
        )

        assert mock_create.call_count == 1
        assert mock_create.call_args.kwargs == {
            "token": "token123",
            "create_recitations_request": request,
        }

        assert resp is None


@pytest.mark.asyncio
async def test_create_recitation_with_empty_content():
    """Test recitation creation with empty content dictionary"""
    request = CreateRecitationsRequest(
        title="Empty Content Recitation",
        audio_url="https://example.com/empty.mp3",
        text_id=uuid.uuid4(),
        content={}
    )

    creds = _Creds(token="valid_token")

    with patch(
        "pecha_api.recitations.recitations_view.create_recitations_service",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_create:
        resp = await create_recitations(
            authentication_credential=creds,
            create_recitations_request=request,
        )

        assert mock_create.call_count == 1
        assert mock_create.call_args.kwargs["token"] == "valid_token"
        assert mock_create.call_args.kwargs["create_recitations_request"].content == {}
        assert resp is None
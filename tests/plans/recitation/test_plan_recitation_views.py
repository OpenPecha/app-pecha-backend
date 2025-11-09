import pytest
import uuid
from unittest.mock import patch, AsyncMock

from pecha_api.plans.recitation.plan_recitation_response_models import CreateRecitationRequest, RecitationDTO, RecitationsResponse
from pecha_api.plans.recitation.plan_recitation_view import create_recitation, get_list_of_recitations


class _Creds:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_create_recitation_success():
    """Test successful recitation creation"""
    request = CreateRecitationRequest(
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
        resp = await create_recitation(
            authentication_credential=creds,
            create_recitation_request=request,
        )

        assert mock_create.call_count == 1
        assert mock_create.call_args.kwargs == {
            "token": "token123",
            "create_recitation_request": request,
        }

        assert resp is None


@pytest.mark.asyncio
async def test_create_recitation_with_empty_content():
    """Test recitation creation with empty content dictionary"""
    request = CreateRecitationRequest(
        title="Empty Content Recitation",
        audio_url="https://example.com/empty.mp3",
        text_id=uuid.uuid4(),
        content={}
    )

    creds = _Creds(token="valid_token")

    with patch(
        "pecha_api.plans.recitation.plan_recitation_view.create_recitation_service",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_create:
        resp = await create_recitation(
            authentication_credential=creds,
            create_recitation_request=request,
        )

        assert mock_create.call_count == 1
        assert mock_create.call_args.kwargs["token"] == "valid_token"
        assert mock_create.call_args.kwargs["create_recitation_request"].content == {}
        assert resp is None


@pytest.mark.asyncio
async def test_get_list_of_recitations_success():
    """Test successful retrieval of recitations list"""
    creds = _Creds(token="valid_token")
    
    expected_recitations = [
        RecitationDTO(
            id=uuid.uuid4(),
            title="First Recitation",
            audio_url="https://example.com/audio1.mp3",
            text_id=uuid.uuid4(),
            content={"text": "First content", "language": "en"}
        ),
        RecitationDTO(
            id=uuid.uuid4(),
            title="Second Recitation", 
            audio_url="https://example.com/audio2.mp3",
            text_id=uuid.uuid4(),
            content={"text": "Second content", "language": "bo"}
        )
    ]
    
    expected_response = RecitationsResponse(
        recitations=expected_recitations,
        skip=0,
        limit=10,
        total=2
    )

    with patch(
        "pecha_api.plans.recitation.plan_recitation_view.get_list_of_recitations_service",
        return_value=expected_response,
        new_callable=AsyncMock,
    ) as mock_get_list:
        resp = await get_list_of_recitations(
            authentication_credential=creds,
            skip=0,
            limit=10
        )

        assert mock_get_list.call_count == 1
        assert mock_get_list.call_args.kwargs == {
            "token": "valid_token",
            "skip": 0,
            "limit": 10
        }

        assert resp == expected_response
        assert isinstance(resp, RecitationsResponse)
        assert len(resp.recitations) == 2
        assert resp.recitations[0].title == "First Recitation"
        assert resp.recitations[1].title == "Second Recitation"
        assert resp.skip == 0
        assert resp.limit == 10
        assert resp.total == 2


@pytest.mark.asyncio
async def test_get_list_of_recitations_empty_list():
    """Test retrieval when no recitations exist"""
    creds = _Creds(token="valid_token")
    
    expected_response = RecitationsResponse(
        recitations=[],
        skip=0,
        limit=10,
        total=0
    )
    
    with patch(
        "pecha_api.plans.recitation.plan_recitation_view.get_list_of_recitations_service",
        return_value=expected_response,
        new_callable=AsyncMock,
    ) as mock_get_list:
        resp = await get_list_of_recitations(
            authentication_credential=creds,
            skip=0,
            limit=10
        )

        assert mock_get_list.call_count == 1
        assert mock_get_list.call_args.kwargs == {
            "token": "valid_token",
            "skip": 0,
            "limit": 10
        }
        assert resp == expected_response
        assert isinstance(resp, RecitationsResponse)
        assert resp.recitations == []
        assert len(resp.recitations) == 0
        assert resp.skip == 0
        assert resp.limit == 10
        assert resp.total == 0


@pytest.mark.asyncio
async def test_get_list_of_recitations_with_custom_pagination():
    """Test retrieval with custom pagination parameters"""
    creds = _Creds(token="valid_token")
    
    expected_recitations = [
        RecitationDTO(
            id=uuid.uuid4(),
            title="Third Recitation",
            audio_url="https://example.com/audio3.mp3",
            text_id=uuid.uuid4(),
            content={"text": "Third content", "language": "en"}
        )
    ]
    
    expected_response = RecitationsResponse(
        recitations=expected_recitations,
        skip=5,
        limit=5,
        total=15
    )
    
    with patch(
        "pecha_api.plans.recitation.plan_recitation_view.get_list_of_recitations_service",
        return_value=expected_response,
        new_callable=AsyncMock,
    ) as mock_get_list:
        resp = await get_list_of_recitations(
            authentication_credential=creds,
            skip=5,
            limit=5
        )

        assert mock_get_list.call_count == 1
        assert mock_get_list.call_args.kwargs == {
            "token": "valid_token",
            "skip": 5,
            "limit": 5
        }
        assert resp == expected_response
        assert isinstance(resp, RecitationsResponse)
        assert len(resp.recitations) == 1
        assert resp.recitations[0].title == "Third Recitation"
        assert resp.skip == 5
        assert resp.limit == 5
        assert resp.total == 15
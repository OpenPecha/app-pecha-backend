import uuid
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from pecha_api.recitations.recitations_response_models import CreateRecitationsRequest, RecitationContent, TextSegments
from pecha_api.recitations.recitations_view import create_recitations


class _Creds:
    def __init__(self, token: str):
        self.credentials = token


@pytest.mark.asyncio
async def test_create_recitations_success():
    """Test successful recitation creation with valid authentication and data."""
    text_id = uuid.uuid4()
    segment_id = uuid.uuid4()
    
    text_segments = [
        TextSegments(
            text="Sample text content",
            segment_id=segment_id,
            start_time="00:00:00",
            end_time="00:00:10"
        )
    ]
    
    recitation_content = RecitationContent(texts=text_segments)
    
    request = CreateRecitationsRequest(
        title="Test Recitation",
        audio_url="https://example.com/audio.mp3",
        text_id=text_id,
        content=recitation_content
    )
    
    creds = _Creds(token="valid_token_123")
    
    with patch(
        "pecha_api.recitations.recitations_view.create_recitations_service",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_create:
        result = await create_recitations(
            authentication_credential=creds,
            create_recitations_request=request,
        )
        
        assert mock_create.call_count == 1
        assert mock_create.call_args.kwargs == {
            "token": "valid_token_123",
            "create_recitations_request": request,
        }
        
        assert result is None

@pytest.mark.asyncio
async def test_create_recitations_text_not_found():
    """Test recitation creation fails when text doesn't exist."""
    text_id = uuid.uuid4()
    segment_id = uuid.uuid4()
    
    text_segments = [
        TextSegments(
            text="Sample text content",
            segment_id=segment_id,
            start_time="00:00:00",
            end_time="00:00:10"
        )
    ]
    
    recitation_content = RecitationContent(texts=text_segments)
    
    request = CreateRecitationsRequest(
        title="Test Recitation",
        audio_url="https://example.com/audio.mp3",
        text_id=text_id,
        content=recitation_content
    )
    
    creds = _Creds(token="valid_token_123")
    
    with patch(
        "pecha_api.recitations.recitations_view.create_recitations_service",
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "Text not found"}
        ),
    ) as mock_create:
        with pytest.raises(HTTPException) as exc_info:
            await create_recitations(
                authentication_credential=creds,
                create_recitations_request=request,
            )
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail["message"].lower()
        
        assert mock_create.call_count == 1

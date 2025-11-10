import uuid
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from types import SimpleNamespace
from pecha_api.recitations.recitations_response_models import CreateRecitationsRequest, RecitationContent, TextSegments
from pecha_api.recitations.recitations_services import create_recitations_service


@pytest.mark.asyncio
async def test_create_recitations_service_success():
    """Test successful recitation creation with valid token and text."""
    text_id = uuid.uuid4()
    segment_id = uuid.uuid4()
    token = "valid_token_123"
    author_email = "author@example.com"
    
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
    
    mock_author = SimpleNamespace(
        id=uuid.uuid4(),
        email=author_email,
        first_name="John",
        last_name="Doe"
    )
    
    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock
    session_cm.__exit__.return_value = None
    
    with patch(
        "pecha_api.recitations.recitations_services.validate_and_extract_author_details",
        return_value=mock_author,
    ) as mock_validate, patch(
        "pecha_api.recitations.recitations_services.TextUtils.validate_text_exists",
        return_value=True,
        new_callable=AsyncMock,
    ) as mock_text_validate, patch(
        "pecha_api.recitations.recitations_services.SessionLocal",
        return_value=session_cm,
    ) as mock_session, patch(
        "pecha_api.recitations.recitations_services.Recitation",
    ) as MockRecitation, patch(
        "pecha_api.recitations.recitations_services.save_recitations",
    ) as mock_save:
        # Return a prebuilt recitation instance from the mocked constructor
        constructed_recitation = SimpleNamespace(
            title=request.title,
            audio_url=request.audio_url,
            text_id=request.text_id,
            content=request.content.model_dump(mode='json')
        )
        MockRecitation.return_value = constructed_recitation
        
        result = await create_recitations_service(
            token=token,
            create_recitations_request=request
        )
        
        # Validate authentication
        assert mock_validate.call_count == 1
        assert mock_validate.call_args.kwargs == {"token": token}
        
        # Validate text exists
        assert mock_text_validate.call_count == 1
        assert mock_text_validate.call_args.args == (str(request.text_id),)
        
        assert mock_session.call_count == 1
        
        ctor_kwargs = MockRecitation.call_args.kwargs
        assert ctor_kwargs == {
            "title": request.title,
            "audio_url": request.audio_url,
            "text_id": request.text_id,
            "content": request.content.model_dump(mode='json')
        }
        
        assert mock_save.call_count == 1
        save_kwargs = mock_save.call_args.kwargs
        assert save_kwargs["db"] is db_mock
        assert save_kwargs["recitation"] is constructed_recitation
        
        assert result is None

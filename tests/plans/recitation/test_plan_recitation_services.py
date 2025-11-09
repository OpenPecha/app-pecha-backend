import pytest
import uuid
from types import SimpleNamespace
from unittest.mock import patch, MagicMock, AsyncMock

from pecha_api.plans.recitation.plan_recitation_response_models import CreateRecitationRequest
from pecha_api.plans.recitation.plan_recitation_services import create_recitation_service


@pytest.mark.asyncio
async def test_create_recitation_service_success():
    """Test successful recitation creation with all operations"""
    text_id = uuid.uuid4()
    request = CreateRecitationRequest(
        title="Test Recitation",
        audio_url="https://example.com/audio.mp3",
        text_id=text_id,
        content={"text": "Sample recitation content", "language": "en"}
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.recitation.plan_recitation_services.validate_and_extract_author_details",
        return_value=SimpleNamespace(email="author@example.com"),
    ) as mock_validate, patch(
        "pecha_api.plans.recitation.plan_recitation_services.TextUtils.validate_text_exists",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_validate_text, patch(
        "pecha_api.plans.recitation.plan_recitation_services.SessionLocal",
        return_value=session_cm,
    ) as mock_session, patch(
        "pecha_api.plans.recitation.plan_recitation_services.Recitation",
    ) as MockRecitation, patch(
        "pecha_api.plans.recitation.plan_recitation_services.save_recitation",
        return_value=None,
    ) as mock_save:
        constructed_recitation = SimpleNamespace(
            title=request.title,
            audio_url=request.audio_url,
            text_id=request.text_id,
            content=request.content,
        )

        MockRecitation.return_value = constructed_recitation

        resp = await create_recitation_service(
            token="token123",
            create_recitation_request=request,
        )

        assert mock_validate.call_count == 1
        assert mock_validate.call_args.kwargs == {"token": "token123"}

        assert mock_validate_text.call_count == 1
        assert mock_validate_text.call_args.args == (str(text_id),)

        assert mock_session.call_count == 1

        assert MockRecitation.call_count == 1
        recitation_kwargs = MockRecitation.call_args.kwargs
        assert recitation_kwargs == {
            "title": request.title,
            "audio_url": request.audio_url,
            "text_id": request.text_id,
            "content": request.content,
        }

        assert mock_save.call_count == 1
        save_kwargs = mock_save.call_args.kwargs
        assert save_kwargs["db"] is db_mock
        assert save_kwargs["recitation"] is constructed_recitation

        assert resp is None


@pytest.mark.asyncio
async def test_create_recitation_service_with_empty_content():
    """Test recitation creation with empty content dictionary"""
    text_id = uuid.uuid4()
    request = CreateRecitationRequest(
        title="Empty Content Recitation",
        audio_url="https://example.com/empty.mp3",
        text_id=text_id,
        content={}
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.recitation.plan_recitation_services.validate_and_extract_author_details",
        return_value=SimpleNamespace(email="author@example.com"),
    ), patch(
        "pecha_api.plans.recitation.plan_recitation_services.TextUtils.validate_text_exists",
        return_value=None,
        new_callable=AsyncMock,
    ) as mock_validate_text, patch(
        "pecha_api.plans.recitation.plan_recitation_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.recitation.plan_recitation_services.Recitation",
    ) as MockRecitation, patch(
        "pecha_api.plans.recitation.plan_recitation_services.save_recitation",
        return_value=None,
    ) as mock_save:
        constructed_recitation = SimpleNamespace(
            title=request.title,
            audio_url=request.audio_url,
            text_id=request.text_id,
            content=request.content,
        )

        MockRecitation.return_value = constructed_recitation

        resp = await create_recitation_service(
            token="valid_token",
            create_recitation_request=request,
        )

        assert mock_validate_text.call_count == 1
        assert mock_validate_text.call_args.args == (str(text_id),)
        assert MockRecitation.call_args.kwargs["content"] == {}
        assert MockRecitation.call_args.kwargs["text_id"] == text_id
        assert mock_save.call_count == 1
        assert resp is None
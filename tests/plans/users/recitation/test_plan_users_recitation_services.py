import pytest
import uuid
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from pecha_api.plans.users.recitation.plan_user_recitation_response_models import CreateUserRecitationRequest
from pecha_api.plans.users.recitation.plan_user_recitation_services import create_user_recitation_service


@pytest.mark.asyncio
async def test_create_user_recitation_service_success():
    """Test successful user recitation creation with all operations"""
    recitation_id = uuid.uuid4()
    user_id = uuid.uuid4()
    request = CreateUserRecitationRequest(recitation_id=recitation_id)

    mock_user = SimpleNamespace(
        id=user_id,
        email="user@example.com"
    )

    mock_recitation = SimpleNamespace(
        id=recitation_id,
        title="Test Recitation",
        audio_url="https://example.com/audio.mp3"
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.validate_and_extract_user_details",
        return_value=mock_user,
    ) as mock_validate_user, patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.SessionLocal",
        return_value=session_cm,
    ) as mock_session, patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.check_recitation_exists",
        return_value=mock_recitation,
    ) as mock_check_recitation, patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.UserRecitation",
    ) as MockUserRecitation, patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.save_user_recitation",
        return_value=None,
    ) as mock_save:
        constructed_user_recitation = SimpleNamespace(
            user_id=user_id,
            recitation_id=recitation_id,
        )

        MockUserRecitation.return_value = constructed_user_recitation

        resp = create_user_recitation_service(
            token="token123",
            create_user_recitation_request=request,
        )

        assert mock_validate_user.call_count == 1
        assert mock_validate_user.call_args.kwargs == {"token": "token123"}

        assert mock_session.call_count == 1

        assert mock_check_recitation.call_count == 1
        assert mock_check_recitation.call_args.kwargs == {
            "db": db_mock,
            "recitation_id": recitation_id
        }

        assert MockUserRecitation.call_count == 1
        user_recitation_kwargs = MockUserRecitation.call_args.kwargs
        assert user_recitation_kwargs == {
            "user_id": user_id,
            "recitation_id": recitation_id,
        }

        assert mock_save.call_count == 1
        save_kwargs = mock_save.call_args.kwargs
        assert save_kwargs["db"] is db_mock
        assert save_kwargs["user_recitation"] is constructed_user_recitation

        assert resp is None

@pytest.mark.asyncio
async def test_create_user_recitation_service_checks_recitation_exists():
    """Test that service properly checks if recitation exists"""
    recitation_id = uuid.uuid4()
    user_id = uuid.uuid4()
    request = CreateUserRecitationRequest(recitation_id=recitation_id)

    mock_user = SimpleNamespace(
        id=user_id,
        email="user@example.com"
    )

    mock_recitation = SimpleNamespace(
        id=recitation_id,
        title="Existing Recitation"
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.validate_and_extract_user_details",
        return_value=mock_user,
    ), patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.check_recitation_exists",
        return_value=mock_recitation,
    ) as mock_check_recitation, patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.UserRecitation",
    ), patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.save_user_recitation",
        return_value=None,
    ):
        create_user_recitation_service(
            token="token123",
            create_user_recitation_request=request,
        )

        assert mock_check_recitation.call_count == 1
        check_args = mock_check_recitation.call_args.kwargs
        assert check_args["db"] is db_mock
        assert check_args["recitation_id"] == recitation_id


@pytest.mark.asyncio
async def test_create_user_recitation_service_creates_correct_user_recitation():
    """Test that service creates UserRecitation with correct parameters"""
    recitation_id = uuid.uuid4()
    user_id = uuid.uuid4()
    request = CreateUserRecitationRequest(recitation_id=recitation_id)

    mock_user = SimpleNamespace(
        id=user_id,
        email="user@example.com"
    )

    mock_recitation = SimpleNamespace(
        id=recitation_id,
        title="Test Recitation"
    )

    db_mock = MagicMock()
    session_cm = MagicMock()
    session_cm.__enter__.return_value = db_mock

    with patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.validate_and_extract_user_details",
        return_value=mock_user,
    ), patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.SessionLocal",
        return_value=session_cm,
    ), patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.check_recitation_exists",
        return_value=mock_recitation,
    ), patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.UserRecitation",
    ) as MockUserRecitation, patch(
        "pecha_api.plans.users.recitation.plan_user_recitation_services.save_user_recitation",
        return_value=None,
    ):
        create_user_recitation_service(
            token="token123",
            create_user_recitation_request=request,
        )

        assert MockUserRecitation.call_count == 1
        creation_kwargs = MockUserRecitation.call_args.kwargs
        assert creation_kwargs["user_id"] == user_id
        assert creation_kwargs["recitation_id"] == recitation_id
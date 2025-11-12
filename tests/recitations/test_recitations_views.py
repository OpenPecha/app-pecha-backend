import uuid
import pytest
from unittest.mock import patch, AsyncMock

from pecha_api.recitations.recitations_view import get_list_of_recitations
from pecha_api.recitations.recitations_response_models import RecitationDTO, RecitationsResponse


@pytest.mark.asyncio
async def test_get_list_of_recitations_success():
    """Test successful retrieval of recitations list."""
    expected = RecitationsResponse(
        recitations=[
            RecitationDTO(title="First Recitation", text_id=uuid.uuid4()),
            RecitationDTO(title="Second Recitation", text_id=uuid.uuid4())
        ]
    )

    with patch(
        "pecha_api.recitations.recitations_view.get_list_of_recitations_service",
        return_value=expected,
        new_callable=AsyncMock,
    ) as mock_service:
        resp = await get_list_of_recitations(language="en")

        mock_service.assert_awaited_once_with(language="en")
        assert resp == expected
        assert len(resp.recitations) == 2
        assert resp.recitations[0].title == "First Recitation"
        assert resp.recitations[1].title == "Second Recitation"


@pytest.mark.asyncio
async def test_get_list_of_recitations_single_recitation():
    """Test get_list_of_recitations with single recitation."""
    text_id = uuid.uuid4()
    expected = RecitationsResponse(
        recitations=[
            RecitationDTO(title="Single Recitation", text_id=text_id)
        ]
    )

    with patch(
        "pecha_api.recitations.recitations_view.get_list_of_recitations_service",
        return_value=expected,
        new_callable=AsyncMock,
    ) as mock_service:
        resp = await get_list_of_recitations(language="bo")

        mock_service.assert_awaited_once_with(language="bo")
        assert resp == expected
        assert len(resp.recitations) == 1
        assert resp.recitations[0].title == "Single Recitation"
        assert resp.recitations[0].text_id == text_id
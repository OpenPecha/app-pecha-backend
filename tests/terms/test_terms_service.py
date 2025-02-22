import pytest
from unittest.mock import patch, AsyncMock

from starlette import status

from pecha_api.terms.terms_service import get_all_terms, create_new_term, update_existing_term, delete_existing_term
from pecha_api.terms.terms_response_models import TermsModel, TermsResponse, CreateTermRequest, UpdateTermRequest
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_get_all_terms():
    with patch("pecha_api.terms.terms_service.verify_admin_access", return_value=True), \
            patch("pecha_api.terms.terms_service.get_terms_by_parent",
                  new_callable=AsyncMock) as mock_get_terms_by_parent, \
            patch("pecha_api.terms.terms_service.get_child_count", new_callable=AsyncMock, return_value=2):
        mock_get_terms_by_parent.return_value = [
            AsyncMock(id="id_1", titles={"en": "Term 1"}, slug="term-1",parent_id=None),
            AsyncMock(id="id_2", titles={"en": "Term 2"}, descriptions={"en": "Description 2"}, slug="term-2",parent_id=None)
        ]
        response = await get_all_terms(language="en",parent_id=None,skip=0,limit=10)
        assert isinstance(response, TermsResponse)
        assert len(response.terms) == 2
        assert response.terms[0].title == "Term 1"


@pytest.mark.asyncio
async def test_create_new_term():
    with patch("pecha_api.terms.terms_service.verify_admin_access", return_value=True), \
            patch("pecha_api.terms.terms_service.create_term", new_callable=AsyncMock) as mock_create_term:
        mock_create_term.return_value = AsyncMock(titles={"en": "New Term"}, descriptions={"en": "New Description"}, slug="new-term",parent_id=None)
        create_term_request = CreateTermRequest(slug="new-term", titles={"en": "New Term"}, descriptions={"en": "New Description"},parent_id=None)
        response = await create_new_term(
            create_term_request=create_term_request,
            token="valid_token",
            language="en"
        )
        assert isinstance(response, TermsModel)
        assert response.title == "New Term"
        assert response.slug == "new-term"
        assert response.description == "New Description"


@pytest.mark.asyncio
async def test_update_existing_term():
    with patch("pecha_api.terms.terms_service.verify_admin_access", return_value=True), \
            patch("pecha_api.terms.terms_service.update_term_titles",
                  new_callable=AsyncMock) as mock_update_term_titles:
        mock_update_term_titles.return_value = AsyncMock(titles={"en": "Updated Term"}, descriptions={"en": "Description 1"}, slug="updated-term",parent_id=None)
        update_term_request = UpdateTermRequest(titles={"en": "Updated Term"}, descriptions={"en": "New Description"})
        response = await update_existing_term(term_id="1", update_term_request=update_term_request, token="valid_token",
                                              language="en")
        assert isinstance(response, TermsModel)
        assert response.title == "Updated Term"


@pytest.mark.asyncio
async def test_delete_existing_term():
    with patch("pecha_api.terms.terms_service.verify_admin_access", return_value=True), \
            patch("pecha_api.terms.terms_service.delete_term", new_callable=AsyncMock) as mock_delete_term:
        mock_delete_term.return_value = "id_1"
        response = await delete_existing_term(term_id="id_1", token="valid_token")
        assert response == "id_1"


@pytest.mark.asyncio
async def test_create_new_term_unauthorized():
    with patch("pecha_api.terms.terms_service.verify_admin_access", return_value=False):
        create_term_request = CreateTermRequest(slug="new-term", titles={"en": "New Term"},descriptions={"en": "New Description"},parent_id=None)
        try:
            await create_new_term(create_term_request=create_term_request, token="invalid_token", language="en")
        except HTTPException as e:
            assert e.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
@patch("pecha_api.terms.terms_service.verify_admin_access", return_value=False)
async def test_update_existing_term_unauthorized(mock_verify_admin_access):
    update_term_request = UpdateTermRequest(titles={"en": "Updated Term"}, descriptions={"en": "Updated Descriptions"})
    try:
        await update_existing_term(term_id="1", update_term_request=update_term_request, token="invalid_token",
                                   language=None)
    except HTTPException as e:
        assert e.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
@patch("pecha_api.terms.terms_service.verify_admin_access", return_value=False)
async def test_delete_existing_term_unauthorized(mock_verify_admin_access):
    try:
        await delete_existing_term(term_id="1", token="invalid_token")
    except HTTPException as e:
        assert e.status_code == status.HTTP_403_FORBIDDEN

from typing import Optional

from starlette import status

from pecha_api.constants import get_value_from_dict
from ..config import get
from ..terms.terms_response_models import TermsModel, TermsResponse, CreateTermRequest, UpdateTermRequest
from .terms_repository import get_child_count, get_terms_by_parent, create_term, update_term_titles, delete_term
from ..users.users_service import verify_admin_access
from fastapi import HTTPException


async def get_all_terms(language: str, parent_id: Optional[str], skip: int, limit: int) -> TermsResponse:
    total = await get_child_count(parent_id=parent_id)
    terms = await get_terms_by_parent(
        parent_id=parent_id,
        skip=skip,
        limit=limit
    )
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    term_list = [
        TermsModel(
            id=str(term.id),
            title=get_value_from_dict(values=term.titles, language=language),
            description=get_value_from_dict(values=term.descriptions, language=language),
            slug=term.slug
        )
        for term in terms
    ]
    term_response = TermsResponse(terms=term_list, total=total, skip=skip, limit=limit)
    return term_response



async def create_new_term(create_term_request: CreateTermRequest, token: str, language: Optional[str]) -> TermsModel:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        new_term = await create_term(create_term_request=create_term_request)
        if language is None:
            language = get("DEFAULT_LANGUAGE")
        return TermsModel(
            id=str(new_term.id),
            title=get_value_from_dict(values=new_term.titles, language=language),
            description=get_value_from_dict(values=new_term.descriptions, language=language),
            slug=new_term.slug
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


async def update_existing_term(term_id: str, update_term_request: UpdateTermRequest, token: str,
                               language: Optional[str]) -> TermsModel:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        updated_term = await update_term_titles(term_id=term_id, update_term_request=update_term_request)
        if language is None:
            language = get("DEFAULT_LANGUAGE")
        return TermsModel(
            id=term_id,
            title=get_value_from_dict(values=updated_term.titles, language=language),
            description=get_value_from_dict(values=updated_term.descriptions, language=language),
            slug=updated_term.slug
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


async def delete_existing_term(term_id: str, token: str):
    is_admin = verify_admin_access(token=token)
    if is_admin:
        await delete_term(term_id=term_id)
        return term_id
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

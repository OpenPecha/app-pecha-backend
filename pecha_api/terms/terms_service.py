from typing import Optional

from starlette import status

from pecha_api.utils import Utils
from ..config import get
from ..terms.terms_response_models import TermsModel, TermsResponse, CreateTermRequest, UpdateTermRequest
from .terms_repository import get_child_count, get_terms_by_parent, create_term, update_term_titles, delete_term, \
    get_term_by_id
from ..users.users_service import verify_admin_access
from fastapi import HTTPException


async def get_all_terms(language: str, parent_id: Optional[str], skip: int, limit: int) -> TermsResponse:
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    total = await get_child_count(parent_id=parent_id)
    parent_term = await get_term(term_id=parent_id,language=language)
    terms = await get_terms_by_parent(
        parent_id=parent_id,
        skip=skip,
        limit=limit
    )
    term_list = [
        TermsModel(
            id=str(term.id),
            title=Utils.get_value_from_dict(values=term.titles, language=language),
            description=Utils.get_value_from_dict(values=term.descriptions, language=language),
            has_child=term.has_sub_child,
            slug=term.slug
        )
        for term in terms
    ]
    term_response = TermsResponse(parent=parent_term, terms=term_list, total=total, skip=skip, limit=limit)
    return term_response


async def create_new_term(create_term_request: CreateTermRequest, token: str, language: Optional[str]) -> TermsModel:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        new_term = await create_term(create_term_request=create_term_request)
        if language is None:
            language = get("DEFAULT_LANGUAGE")
        return TermsModel(
            id=str(new_term.id),
            title=Utils.get_value_from_dict(values=new_term.titles, language=language),
            description=Utils.get_value_from_dict(values=new_term.descriptions, language=language),
            has_child=new_term.has_sub_child,
            slug=new_term.slug
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

async def get_term(term_id: str,language: str) -> Optional[TermsModel]:
    selected_term = await get_term_by_id(term_id=term_id)
    if selected_term:
        return TermsModel(
            id=term_id,
            title=Utils.get_value_from_dict(values=selected_term.titles, language=language),
            description=Utils.get_value_from_dict(values=selected_term.descriptions, language=language),
            has_child=selected_term.has_sub_child,
            slug=selected_term.slug
        )
    return None

async def update_existing_term(term_id: str, update_term_request: UpdateTermRequest, token: str,
                               language: Optional[str]) -> TermsModel:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        updated_term = await update_term_titles(term_id=term_id, update_term_request=update_term_request)
        if language is None:
            language = get("DEFAULT_LANGUAGE")
        return TermsModel(
            id=term_id,
            title=Utils.get_value_from_dict(values=updated_term.titles, language=language),
            description=Utils.get_value_from_dict(values=updated_term.descriptions, language=language),
            has_child=updated_term.has_sub_child,
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

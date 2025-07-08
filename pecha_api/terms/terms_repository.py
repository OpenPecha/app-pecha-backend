import logging
from typing import Optional

from beanie.exceptions import CollectionWasNotInitialized
from fastapi import HTTPException
from starlette import status

from pecha_api.utils import Utils
from ..terms.terms_models import Term
from ..terms.terms_response_models import CreateTermRequest, UpdateTermRequest

TERM_NOT_FOUND = 'Term not found'


async def get_terms_by_parent(
        parent_id: Optional[str],
        skip: int,
        limit: int) -> list[Term]:
    try:
        topic_parent_id = Utils.get_parent_id(parent_id=parent_id)
        terms = await Term.get_children_by_id(parent_id=topic_parent_id, skip=skip, limit=limit)
        return terms
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return []


async def get_child_count(parent_id: Optional[str]) -> int:
    topic_parent_id = Utils.get_parent_id(parent_id=parent_id)
    count = await Term.count_children(parent_id=topic_parent_id)
    return count


async def create_term(create_term_request: CreateTermRequest) -> Term:
    try:
        existing_term = await Term.find_one(Term.slug == create_term_request.slug)
        if existing_term:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Term with this slug already exists")
    except AttributeError as e:
        logging.debug(e)
    new_term = Term(slug=create_term_request.slug, titles=create_term_request.titles,
                    descriptions=create_term_request.descriptions, parent_id=create_term_request.parent_id)
    saved_term = await new_term.insert()
    if create_term_request.parent_id is not None:
        await update_term_child_status(term_id=create_term_request.parent_id)
    return saved_term


async def get_term_by_id(term_id: Optional[str]) -> Optional[Term]:
    if not term_id:
        return None
    return await Term.get(term_id)


async def update_term_child_status(term_id: str) -> Term:
    existing_term = await Term.get(term_id)
    if not existing_term:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TERM_NOT_FOUND)
    child_count = await Term.count_children(parent_id=existing_term.id)
    has_child = child_count > 0
    if existing_term.has_sub_child != has_child:
        existing_term.has_sub_child = has_child
        await existing_term.save()
    return existing_term


async def update_term_titles(term_id: str, update_term_request: UpdateTermRequest) -> Term:
    existing_term = await Term.get(term_id)
    if not existing_term:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TERM_NOT_FOUND)

    existing_term.titles = update_term_request.titles
    await existing_term.save()
    return existing_term


async def delete_term(term_id: str):
    existing_term = await Term.get(term_id)
    if not existing_term:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TERM_NOT_FOUND)
    parent_id = existing_term.parent_id
    await existing_term.delete()
    if parent_id is not None:
        await update_term_child_status(term_id=str(parent_id))
    return existing_term
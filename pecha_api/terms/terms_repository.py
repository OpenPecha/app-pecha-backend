import logging
from typing import Optional

from beanie import PydanticObjectId
from beanie.exceptions import CollectionWasNotInitialized
from fastapi import HTTPException
from starlette import status

from ..terms.terms_models import Term
from ..terms.terms_response_models import CreateTermRequest, UpdateTermRequest


async def get_terms_by_parent(
        parent_id: Optional[str],
        skip: int,
        limit: int) -> list[Term]:
    try:
        topic_parent_id = get_parent_id(parent_id=parent_id)
        terms = await Term.get_children_by_id(parent_id=topic_parent_id, skip=skip, limit=limit)
        return terms
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return []


async def get_child_count(parent_id: Optional[str]) -> int:
    topic_parent_id = get_parent_id(parent_id=parent_id)
    count = await Term.count_children(parent_id=topic_parent_id)
    return count


async def create_term(create_term_request: CreateTermRequest) -> Term:
    try:
        existing_term = await Term.find_one(Term.slug == create_term_request.slug)
        if existing_term:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Term with this slug already exists")
    except AttributeError as e:
        logging.debug(e)
    new_term = Term(slug=create_term_request.slug, titles=create_term_request.titles)
    saved_term = await new_term.insert()
    return saved_term


async def update_term_titles(term_id: str, update_term_request: UpdateTermRequest) -> Term:
    existing_term = await Term.get(term_id)
    if not existing_term:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")

    existing_term.titles = update_term_request.titles
    await existing_term.save()
    return existing_term


async def delete_term(term_id: str):
    existing_term = await Term.get(term_id)
    if not existing_term:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")

    await existing_term.delete()
    return existing_term


def get_parent_id(parent_id: Optional[str]):
    topic_parent_id = None
    if parent_id is not None:
        topic_parent_id = PydanticObjectId(parent_id)
    return topic_parent_id

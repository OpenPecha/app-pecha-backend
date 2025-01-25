from fastapi import HTTPException
from starlette import status

from terms.terms_models import Term
from terms.terms_response_models import CreateTermRequest, UpdateTermRequest


async def get_terms() -> list[Term]:
    terms = await Term.find_all().to_list()
    return terms


async def create_term(create_term_request: CreateTermRequest) -> Term:
    existing_term = await Term.find_one(Term.slug == create_term_request.slug)
    if existing_term:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Term with this slug already exists")
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
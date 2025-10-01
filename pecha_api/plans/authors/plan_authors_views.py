from uuid import UUID

from fastapi import APIRouter
from fastapi.security import HTTPBearer
from starlette import status

from db import database
from plans.authors.plan_authors_response_models import AuthorInfoResponse
from plans.authors.plan_authors_service import get_selected_author_details

oauth2_scheme = HTTPBearer()
author_router = APIRouter(
    prefix="/authors",
    tags=["Authors Profile"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@author_router.get("{author_id}", status_code=status.HTTP_200_OK)
async def get_author_information(author_id: UUID)  -> AuthorInfoResponse:
    return await get_selected_author_details(author_id=author_id)

@author_router.get("{author_id}/plans", status_code=status.HTTP_200_OK)
async def get_plans_by_author(author_id: UUID)  -> AuthorInfoResponse:
    return await get_selected_author_details(author_id=author_id)
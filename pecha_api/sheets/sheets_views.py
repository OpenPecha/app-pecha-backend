from __future__ import annotations
from fastapi import APIRouter, Query
from fastapi.security import HTTPBearer
from starlette import status

from typing import Optional

from .sheets_service import get_sheets, get_sheets_by_userID, create_new_sheet
from .sheets_response_models import CreateSheetRequest

oauth2_scheme = HTTPBearer()
sheets_router = APIRouter(
    prefix="/sheets",
    tags=["Sheets"]
)


@sheets_router.get("/topic", status_code=status.HTTP_200_OK)
def get_topics(language: str | None):
    return get_sheets(topic_id='', language=language)

#get sheet with user_id with pagination
@sheets_router.get("", status_code=status.HTTP_200_OK)
async def get_sheets_by_user_id(
    user_id: Optional[str] = None,
    language: Optional[str] = None,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return")
):
    return await get_sheets_by_userID(
        user_id=user_id,
        language=language,
        skip=skip,
        limit=limit
    )

@sheets_router.post("", status_code=status.HTTP_201_CREATED)
async def create_sheet(
    create_sheet_request: CreateSheetRequest,
        ):
    return await create_new_sheet(
        create_sheet_request=create_sheet_request
    )

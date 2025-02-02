from __future__ import annotations
from fastapi import APIRouter
from fastapi.security import HTTPBearer
from starlette import status

from .sheets_service import get_sheets

oauth2_scheme = HTTPBearer()
sheets_router = APIRouter(
    prefix="/sheets",
    tags=["Sheets"]
)


@sheets_router.get("", status_code=status.HTTP_200_OK)
def get_topics(language: str | None):
    return get_sheets(topic_id='', language=language)

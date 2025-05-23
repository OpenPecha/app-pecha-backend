from fastapi import APIRouter, Query
from starlette import status

from typing import Union

from .search_service import (
    get_search_results
)

from .search_response_models import (
    SearchSourceResponse,
    SearchSheetResponse
)

search_router = APIRouter(
    prefix="/search",
    tags=["Search"]
)

@search_router.get("", status_code=status.HTTP_200_OK)
async def search(
    query: str = Query(default=None, description="Search query"),
    type: str = Query(default=None, description="Search type (Source / Sheet)")
) -> Union[SearchSourceResponse, SearchSheetResponse, str]:
    return await get_search_results(query=query, type=type)

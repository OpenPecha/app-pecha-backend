from fastapi import APIRouter, Query
from .search_enums import SearchType
from starlette import status

from .search_enums import SearchType

from typing import Optional

from .search_service import (
    get_search_results
)

from .search_response_models import (
    SearchResponse
)

search_router = APIRouter(
    prefix="/search",
    tags=["Search"]
)

@search_router.get("", status_code=status.HTTP_200_OK)
async def search(
    query: str = Query(default=None, description="Search query"),
    search_type: SearchType = Query(default=None, description="Search type (SOURCE / SHEET)"),
    text_id: Optional[str] = Query(default=None, description="Text ID where the search is to be performed"),
    skip: int = Query(default=0),
    limit: int = Query(default=10)
) -> SearchResponse:
    return await get_search_results(
        query=query,
        search_type=search_type,
        text_id=text_id,
        skip=skip,
        limit=limit
    )

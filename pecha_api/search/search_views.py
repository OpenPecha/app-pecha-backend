from fastapi import APIRouter, Query
from .search_enums import SearchType
from starlette import status

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
    type: SearchType = Query(default=None, description="Search type: source or sheet"),
    skip: int = Query(default=0),
    limit: int = Query(default=10)
) -> SearchResponse:
    return await get_search_results(query=query, type=type)

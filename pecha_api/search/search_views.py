from fastapi import APIRouter, Query
from starlette import status

from .search_service import (
    get_search_results
)

search_router = APIRouter(
    prefix="/search",
    tags=["Search"]
)

@search_router.get("", status_code=status.HTTP_200_OK)
async def search(
    query: str = Query(default=None, description="Search query")
):
    return await get_search_results(query=query)

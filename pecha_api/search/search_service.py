from elastic_transport import ObjectApiResponse

from .search_enums import SearchType
from .search_response_models import (
    SearchResponse,
    TextIndex,
    SegmentMatch,
    SourceResultItem,
    Search,
    SheetResultItem
)
from .search_client import search_client
from pecha_api.config import get
   

async def get_search_results(query: str, search_type: SearchType, skip: int = 0, limit: int = 10) -> SearchResponse:
    if SearchType.SOURCE == search_type:
        source_search_response: SourceResultItem = await _source_search(
            query=query,
            skip=skip,
            limit=limit
        )
    elif SearchType.SHEET == search_type:
        sheet_search_response: SheetResultItem = await _sheet_search(
            query=query,
            skip=skip,
            limit=limit
        )
        return sheet_search_response
    return SearchResponse(
        search=Search(text=query, type=search_type),
        sources=source_search_response,
        sheets=sheet_search_response,
        skip=skip,
        limit=limit,
        total=0
    )


async def _source_search(query: str, skip: int, limit: int) -> SearchResponse:
    client = await search_client()
    search_query = _generate_search_query(
        query=query,
        page=skip,
        size=limit
    )
    query_response: ObjectApiResponse = await client.search(
        index=get("ELASTICSEARCH_SEGMENT_INDEX"),
        **search_query
    )
    search_response = _process_source_search_response(query, query_response)
    return search_response


def _process_source_search_response(query: str, search_response: ObjectApiResponse) -> SourceResultItem:
    hits = search_response["hits"]["hits"]
    total = search_response["hits"]["total"]["value"] if "total" in search_response["hits"] else 0
    text_segments = {}
    for result in hits:
        source = result["_source"]
        text_id = source["text_id"]
        if text_id not in text_segments:
            text_segments[text_id] = {
                "segments": [
                    SegmentMatch(
                        segment_id=source["id"],
                        content=source["content"]
                    )
                ]
            }
        else:
            text_segments[text_id]["segments"].append(
                SegmentMatch(
                    segment_id=source["id"],
                    content=source["content"]
                )
            )
    sources: SourceResultItem = [
        SourceResultItem(
            text=TextIndex(
                text_id="static",
                language="static",
                title="static",
                published_date="static"
            ),
            segment_match=data["segments"]
        )
        for data in text_segments.values()
    ]
    return sources


def _generate_search_query(query: str, page: int, size: int):
    return {
        "query": {
            "match": {
                "content": {
                    "query": query,
                    "fuzziness": "AUTO"
                }
            }
        },
        "from": (page - 1) * size,
        "size": size
    }


async def _sheet_search(query: str, skip: int, limit: int) -> SearchResponse:
    client = await search_client()
    search_query = _generate_search_query(
        query=query,
        page=skip,
        size=limit
    )
    query_response: ObjectApiResponse = await client.search(
        index=get("ELASTICSEARCH_SHEET_INDEX"),
        **search_query
    )
    # search_response = _process_sheet_search_response(query, query_response)
    return []
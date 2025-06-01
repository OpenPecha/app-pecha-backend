from elastic_transport import ObjectApiResponse

from .search_enums import SearchType
from .search_response_models import (
    SearchResponse,
    TextIndex,
    SegmentMatch,
    SourceResultItem,
    Search
)
from .search_client import search_client
from pecha_api.config import get


async def get_search_results(query: str, search_type: SearchType, skip: int = 0, limit: int = 10) -> SearchResponse:
    if SearchType.SOURCE == search_type:
        search_response: SearchResponse = await _text_search(
            query=query,
            skip=skip,
            limit=limit
        )
        return search_response
    elif SearchType.SHEET == search_type:
        sheet_search_response: SearchResponse = await _sheet_search(
            query=query,
            skip=skip,
            limit=limit
        )
        return sheet_search_response
    return SearchResponse(
        search=Search(text=query, type="sheet"),
        skip=skip,
        limit=limit,
        total=0
    )


async def _text_search(query: str, skip: int, limit: int) -> SearchResponse:
    client = await search_client()
    search_query = _generate_search_query(
        query=query,
        page=skip,
        size=limit
    )
    query_response: ObjectApiResponse = await client.search(
        index=get("ELASTICSEARCH_CONTENT_INDEX"),
        **search_query
    )
    search_response = process_search_response(query, query_response)
    return search_response


def process_search_response(query: str, search_response: ObjectApiResponse) -> SearchResponse:
    hits = search_response["hits"]["hits"]
    total = search_response["hits"]["total"]["value"] if "total" in search_response["hits"] else 0
    text_segments = {}
    for result in hits:
        source = result["_source"]
        text_id = source["text_id"]
        if text_id not in text_segments:
            text_segments[text_id] = {
                "text": TextIndex(
                    text_id=text_id,
                    language=source["language"],
                    title=source["title"],
                    published_date=source["published_date"]
                ),
                "segments": []
            }
        if text_id in text_segments:
            text_segments[text_id]["segments"].append(
                SegmentMatch(
                    segment_id=source["id"],
                    content=source["content"]
                )
            )
    sources = [
        SourceResultItem(
            text=data["text"],
            segment_match=data["segments"]
        )
        for data in text_segments.values()
    ]
    if not sources:
        return SearchResponse(
            search=Search(text=query, type="source"),
            sources=[],
            skip=0,
            limit=10,
            total=0
        )

    return SearchResponse(
        search=Search(text=query, type="source"),
        sources=sources,
        skip=0,
        limit=len(sources),
        total=total
    )


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
        index=get("ELASTICSEARCH_SEGMENT_INDEX"),
        **search_query
    )
    search_response = process_search_response(query, query_response)
    return search_response

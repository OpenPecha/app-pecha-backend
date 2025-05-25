from elastic_transport import ObjectApiResponse

from .search_enums import SearchType
from .search_response_models import (
    SearchResponse,
    TextIndex,
    SegmentMatch,
    SourceIndex,
    Sheet,
    Search
)
from .search_client import search_client
from pecha_api.config import get


async def get_search_results(query: str, type: SearchType,skip: int,limit: int) -> SearchResponse:
    if SearchType.SOURCE == type:
        search_response: SearchResponse = await text_search(query=query,skip=skip,limit=limit)
        if not search_response.sources:
            search_response = await _source_search_(
                query=query
            )
        return search_response
    elif SearchType.SHEET == type:
        hits: SearchResponse = await _sheet_search_(query=query)
        return hits
    return None


async def text_search(query: str,skip: int,limit: int) -> SearchResponse:
    client = await search_client()
    search_query = _generate_search_query(query)
    query_response: ObjectApiResponse = await client.search(
        index=get("ELASTICSEARCH_SEGMENT_INDEX"),
        body=search_query
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
        SourceIndex(
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


async def _source_search_(query: str) -> SearchResponse:
    sources = [
        SourceIndex(
            text=TextIndex(
                text_id="91a616af-c8f4-4797-baf7-9772a3474cff",
                language="bo",
                title="མཐུ་སྟོབས།",
                published_date="12-02-2025"
            ),
            segment_match=[
                SegmentMatch(
                    segment_id="a7391925-c9bd-4304-8287-c71b313b2fc6",
                    content="བོད་ཡིག་གི་ཚིག་གྲུབ་འདི་ནི་བུདྡྷེསཏ་རེད། buddhist"
                ),
                SegmentMatch(
                    segment_id="9dd7c2f4-eacc-46a7-80b0-4b24357cce58",
                    content="བོད་ཡིག་གི་ཚིག་གྲུབ་འདི་ནི་བུདྡྷེསཏ་རེད། བོད་ཡིག་གི་ཚིག་གྲུབ་འདི་ནི་བུདྡྷེསཏ་རེད། buddhist"
                )
            ]
        ),
        SourceIndex(
            text=TextIndex(
                text_id="e597eeb8-3142-4937-b1c7-f211b8230f2c",
                language="en",
                title="The Buddhist Path",
                published_date="12-02-2025"
            ),
            segment_match=[
                SegmentMatch(
                    segment_id="25e50dbe-9243-4732-b1cf-a25c5e3e25c0",
                    content="This text is all about Buddhist Path"
                )
            ]
        )
    ]
    return SearchResponse(
        search=Search(text=query, type="source"),
        sources=sources,
        skip=0,
        limit=10,
        total=2
    )

def _generate_search_query(query: str) -> str:
    search_query = {
        "query": {
            "match": {
                "content": {
                    "query": query,
                    "fuzziness": "AUTO"
                }
            }
        },
        "highlight": {
            "fields": {
                "content": {}
            }
        }
    }
    return search_query

async def _sheet_search_(query: str) -> SearchResponse:
    sheets = [
        Sheet(
            sheet_title="བཟོད་པའི་མཐུ་སྟོབས།",
            sheet_summary="བཟོད་པའི་ཕན་ཡོན་དང་ཁོང་ཁྲོའི་ཉེས་དམིགས་ཀྱི་གཏམ་རྒྱུད་འདི། ད་ལྟའང་བོད་ཀྱི་གྲོང་གསེབ་དེར་གླེང་སྒྲོས་སུ་གྱུར་ཡོད་དོ།། །། Buddhist Path",
            publisher_id=48,
            sheet_id=114,
            publisher_name="Yeshi Lhundup",
            publisher_url="/profile/yeshi-lhundup",
            publisher_image="https://storage.googleapis.com/pecha-profile-img/yeshi-lhundup-1742619970-small.png",
            publisher_position="LCM",
            publisher_organization="pecha.org"
        ),
        Sheet(
            sheet_title="Teaching 1st Jan 2025",
            sheet_summary="sadf asdfas dfas Buddhist Path",
            publisher_id=61,
            sheet_id=170,
            publisher_name="Yeshi Lhundup",
            publisher_url="/profile/yeshi-lhundup2",
            publisher_image="",
            publisher_position="",
            publisher_organization=""
        )
    ]
    return SearchResponse(
        search=Search(text=query, type="sheet"),
        sheets=sheets,
        skip=0,
        limit=10,
        total=20
    )

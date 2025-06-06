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


async def get_search_results(query: str, type: SearchType) -> SearchResponse:
    if type.value == "source":
        hits: SearchResponse = await _source_search_(query)
        return hits
        
    elif type.value == "sheet":
        hits: SearchResponse = await _sheet_search_(query)
        return hits
   

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

async def _source_search_(query: str) -> SearchResponse:
    sources = await _mock_source_data_()
    return SearchResponse(
        search=Search(text=query, type="source"),
        sources=sources,
        skip=0,
        limit=10,
        total=2
    )

async def _sheet_search_(query: str) -> SearchResponse:
    sheets = await _mock_sheet_data_()
    return SearchResponse(
        search=Search(text=query, type="sheet"),
        sheets=sheets,
        skip=0,
        limit=10,
        total=20
    )

async def _mock_source_data_():
    return [
            Source(
                text=Text(
                    text_id="59769286-2787-4181-953d-9149cdeef959",
                    language="en",
                    title="The Way of the Bodhisattva",
                    published_date="12-02-2025"
                ),
                segment_match=[
                    SegmentMatch(
                        segment_id="6376cd2b-127f-4230-ab1b-e132bfae493f",
                        content="From the moment one properly takes up<br>That resolve with an irreversible mind<br>For the purpose of liberating<br>The limitless realm of beings..."
                    ),
                    SegmentMatch(
                        segment_id="6a59a87c-9f79-4e0d-9094-72623cf31ec2",
                        content="From this time forth, even while sleeping<br>Or being heedless, the force of merit<br>Flows forth continuously in numerous streams<br>Equal to the expanse of space."
                    )
                ]
            ),
            Source(
                text=Text(
                    text_id="e6370d09-aa0c-4a41-96ef-deffb89c7810",
                    language="en",
                    title="The Way of the Bodhisattva Claude AI Draft",
                    published_date="12-02-2025"
                ),
                segment_match=[
                    SegmentMatch(
                        segment_id="6dd83d79-8300-49fa-84b8-74933b17b2dd",
                        content="From the mind of aspiration for enlightenment,<br>Great results arise while in samsara.<br>However, unlike the mind of actual engagement,<br>It does not produce a continuous stream of merit."
                    )
                ]
            )
        ]

async def _mock_sheet_data_():
    return [
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

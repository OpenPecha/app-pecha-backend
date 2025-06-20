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

from typing import List
   
MAX_SEARCH_LIMIT = 30

async def get_search_results(query: str, search_type: SearchType, text_id: str = None, skip: int = 0, limit: int = 10) -> SearchResponse:
    if SearchType.SOURCE == search_type:
        source_search_response: SearchResponse = await _source_search(
            query=query,
            text_id=text_id,
            skip=skip,
            limit=limit
        )
        return source_search_response

    elif SearchType.SHEET == search_type:
        sheet_search_response: SearchResponse = _sheet_search(
            query=query,
            skip=skip,
            limit=limit
        )
        return sheet_search_response

async def _source_search(
        query: str, 
        text_id: str, 
        skip: int, 
        limit: int
) -> SearchResponse:
    client = search_client()
    search_query = _generate_search_query(
        query=query,
        text_id=text_id,
        page=skip,
        size=limit
    )
    query_response: ObjectApiResponse = await client.search(
        index=get("ELASTICSEARCH_SEGMENT_INDEX"),
        **search_query
    )
    search_response: SearchResponse = _process_source_search_response(
        query, 
        query_response, 
        skip, 
        limit)
    return search_response


def _process_source_search_response(query: str, search_response: ObjectApiResponse, skip: int, limit: int) -> SearchResponse:
    hits = search_response["hits"]["hits"]
    total = search_response["hits"]["total"]["value"] if "total" in search_response["hits"] else 0
    source_dict, text_dict = _group_sources_by_text_id(hits=hits)
    sources: List[SourceResultItem] = _get_source_result_items_(text_dict=text_dict, source_dict=source_dict)
    return SearchResponse(
        search=Search(
            text=query,
            type=SearchType.SOURCE
        ),
        sources=sources,
        skip=skip,
        limit=limit,
        total=min(MAX_SEARCH_LIMIT, total)
    )

def _get_source_result_items_(text_dict: dict, source_dict: dict) -> List[SourceResultItem]:
    sources: List[SourceResultItem] = []
    for source_key in source_dict.keys():
        text = TextIndex(
            text_id=text_dict[source_key].text_id,
            language=text_dict[source_key].language,
            title=text_dict[source_key].title,
            published_date=text_dict[source_key].published_date
        )
        segment_matches: List[SegmentMatch] = []
        for data in source_dict[source_key]:
            segment_matches.append(
                SegmentMatch(
                    segment_id=data["id"],
                    content=data["content"]
                )
            )
        sources.append(
            SourceResultItem(
                text=text,
                segment_match=segment_matches
            )
        )
    return sources

def _group_sources_by_text_id(hits: list) -> tuple[dict, dict]:
    source_dict = {}
    text_dict = {}
    for result in hits:
        source = result["_source"]
        text = source["text"]
        text_id = source["text_id"]
        text_index = TextIndex(
            text_id=text_id,
            language=text["language"],
            title=text["title"],
            published_date=text["published_date"]
        )
        if text_id not in source_dict:
            source_dict[text_id] = [source]
            text_dict[text_id] = text_index
        else:
            source_dict[text_id].append(source)
    return source_dict, text_dict

def _generate_search_query(
        query: str, 
        text_id: str, 
        page: int, 
        size: int
):
    search_query = {
        "query": {
            "bool": {
                "must": [],
                "should": [
                    {
                        "match": {
                            "content": {
                                "query": query
                            }
                        }
                    }
                ]
            }
        },
        "from": max(0, (page - 1)) * size,
        "size": size
    }
    if text_id:
        search_query["query"]["bool"]["must"].append({
            "term": {
                "text_id.keyword": text_id
            }
        })
    return search_query

def _sheet_search(query: str, skip: int, limit: int) -> SearchResponse:
    mock_sheet_data: List[SheetResultItem] = _mock_sheet_data_()
    return SearchResponse(
        search=Search(
            text=query,
            type=SearchType.SHEET
        ),
        sheets=mock_sheet_data,
        skip=skip,
        limit=limit,
        total=len(mock_sheet_data)
    )

def _mock_sheet_data_():
    return [
            SheetResultItem(
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
            SheetResultItem(
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
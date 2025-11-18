from elastic_transport import ObjectApiResponse

from .search_enums import SearchType
from .search_response_models import (
    SearchResponse,
    TextIndex,
    SegmentMatch,
    SourceResultItem,
    Search,
    SheetResultItem,
    ExternalSearchResponse,
    MultilingualSegmentMatch,
    MultilingualSourceResult,
    MultilingualSearchResponse
)
from .search_client import search_client
from pecha_api.config import get

from typing import List, Dict, Optional
import httpx
import logging

from pecha_api.texts.segments.segments_models import Segment
from pecha_api.texts.texts_models import Text

logger = logging.getLogger(__name__)

MAX_SEARCH_LIMIT = 30

async def get_search_results(query: str, search_type: SearchType, text_id: str = None, skip: int = 0, limit: int = 10) -> SearchResponse:

    if SearchType.SOURCE == search_type:
        response: SearchResponse = await _source_search(
            query=query,
            text_id=text_id,
            skip=skip,
            limit=limit
        )

    elif SearchType.SHEET == search_type:
        response: SearchResponse = _sheet_search(
            query=query,
            skip=skip,
            limit=limit
        )
    
    return response


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
        skip=skip,
        limit=limit
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
        skip: int, 
        limit: int
):
    search_query = {
        "query": {
            "bool": {
                "must": [
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
        "from": skip,
        "size": limit
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

async def get_multilingual_search_results(
    query: str,
    search_type: str = "hybrid",
    text_id: Optional[str] = None,
    limit: int = 10
) -> MultilingualSearchResponse:
    """
    Performs multilingual search by:
    1. Getting text title if text_id is provided (for individual search)
    2. Calling external multilingual search API
    3. Mapping external segmentation_ids to internal segment_ids
    4. Building enriched response with ranking
    
    Args:
        query: Search query text
        search_type: Type of search (hybrid, bm25, semantic, exact)
        text_id: Optional text_id for individual text search
        limit: Maximum number of results
        
    Returns:
        MultilingualSearchResponse with enriched segment data
    """
    try:
        # Step 1: Get text title if searching within individual text
        title = None
        if text_id:
            text = await Text.get_text(text_id)
            if text:
                title = text.title
            else:
                logger.warning(f"Text with ID {text_id} not found")
        
        # Step 2: Call external multilingual search API
        external_results = await _call_external_search_api(
            query=query,
            search_type=search_type,
            limit=limit,
            title=title
        )
        
        # Step 3: Extract segmentation_ids from external response
        segmentation_ids = []
        results_map = {}  # Map segmentation_id -> (distance, content)
        
        for result in external_results.results:
            if result.id:  # Now using id instead of segmentation_ids
                segmentation_ids.append(result.id)
                results_map[result.id] = {
                    "distance": result.distance,
                    "content": result.entity.text
                }
        
        if not segmentation_ids:
            logger.info("No segmentation IDs returned from external API")
            return MultilingualSearchResponse(
                query=query,
                search_type=search_type,
                sources=[],
                skip=0,
                limit=limit,
                total=0
            )
        
        # Step 4: Map external segmentation_ids to internal segments
        segments = await Segment.get_segments_by_pecha_ids(
            pecha_segment_ids=segmentation_ids,
            text_id=text_id
        )
        
        if not segments:
            logger.warning(f"No internal segments found for {len(segmentation_ids)} segmentation IDs")
            return MultilingualSearchResponse(
                query=query,
                search_type=search_type,
                sources=[],
                skip=0,
                limit=limit,
                total=0
            )
        
        # Step 5: Group segments by text_id and build response
        sources = await _build_multilingual_sources(segments, results_map)
        
        return MultilingualSearchResponse(
            query=query,
            search_type=search_type,
            sources=sources,
            skip=0,
            limit=limit,
            total=len(segments)
        )
        
    except Exception as e:
        logger.error(f"Error in multilingual search: {str(e)}", exc_info=True)
        raise


async def _call_external_search_api(
    query: str,
    search_type: str,
    limit: int,
    title: Optional[str] = None
) -> ExternalSearchResponse:

    print("test")
    external_api_url = "https://openpecha-search.onrender.com"   #"https://api-l25bgmwqoa-uc.a.run.app" 
    endpoint = f"{external_api_url}/search"

    print("endpoint", endpoint)
    
    params = {
        "query": query,
        "search_type": search_type,
        "limit": limit
    }
    
    if title:
        params["title"] = title
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            return ExternalSearchResponse(**data)
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error calling external search API: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error calling external search API: {str(e)}", exc_info=True)
        raise


async def _build_multilingual_sources(
    segments: List[Segment],
    results_map: Dict[str, Dict]
) -> List[MultilingualSourceResult]:
    """
    Groups segments by text and builds MultilingualSourceResult objects.
    
    Args:
        segments: List of Segment documents
        results_map: Mapping of pecha_segment_id to distance and content
        
    Returns:
        List of MultilingualSourceResult grouped by text
    """
    # Group segments by text_id
    text_segments_map: Dict[str, List[Segment]] = {}
    text_info_map: Dict[str, TextIndex] = {}
    
    for segment in segments:
        if segment.text_id not in text_segments_map:
            text_segments_map[segment.text_id] = []
        text_segments_map[segment.text_id].append(segment)
    
    # Get text information for each unique text_id
    for text_id in text_segments_map.keys():
        text = await Text.get_text(text_id)
        if text:
            text_info_map[text_id] = TextIndex(
                text_id=text_id,
                language=text.language,
                title=text.title,
                published_date=str(text.created_at) if hasattr(text, 'created_at') else ""
            )
    
    # Build sources list
    sources = []
    for text_id, text_segments in text_segments_map.items():
        if text_id not in text_info_map:
            continue
        
        # Build segment matches with ranking
        segment_matches = []
        for segment in text_segments:
            pecha_id = segment.pecha_segment_id
            if pecha_id and pecha_id in results_map:
                segment_matches.append(
                    MultilingualSegmentMatch(
                        segment_id=str(segment.id),
                        content=segment.content,
                        relevance_score=results_map[pecha_id]["distance"],
                        pecha_segment_id=pecha_id
                    )
                )
        
        # Sort by relevance score (lower distance = more relevant)
        segment_matches.sort(key=lambda x: x.relevance_score)
        
        sources.append(
            MultilingualSourceResult(
                text=text_info_map[text_id],
                segment_matches=segment_matches
            )
        )
    
    return sources
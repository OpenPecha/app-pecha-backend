
from typing import Union

from .search_response_models import (
    SearchResponse,
    Text,
    SegmentMatch,
    Source,
    Sheet,
    Search
)
from .search_enums import SearchType

async def get_search_results(query: str, type: SearchType) -> SearchResponse:
    if type.value == "source":
        hits: SearchResponse = await _source_search_(query)
        return hits
        
    elif type.value == "sheet":
        hits: SearchResponse = await _sheet_search_(query)
        return hits
    


async def _source_search_(query: str) -> SearchResponse:
    sources = [
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
    return SearchResponse(
        search=Search(text=query, type="source"),
        sources=sources,
        skip=0,
        limit=10,
        total=2
    )

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
from .search_response_models import (
    SearchResponse
)

async def get_search_results(query: str) -> SearchResponse:
    return {
        "search":{
            "text": "buddhist"
        },
        "sources": [
            {
                "text": {
                    "text_id": "91a616af-c8f4-4797-baf7-9772a3474cff",
                    "language": "bo",
                    "title": "མཐུ་སྟོབས།",
                    "published_date": "12-02-2025"
                },
                "segment_match": [
                    {
                        "segment_id": "a7391925-c9bd-4304-8287-c71b313b2fc6",
                        "content": "བོད་ཡིག་གི་ཚིག་གྲུབ་འདི་ནི་བུདྡྷེསཏ་རེད། buddhist"
                    },
                    {
                        "segment_id": "9dd7c2f4-eacc-46a7-80b0-4b24357cce58",
                        "content": "བོད་ཡིག་གི་ཚིག་གྲུབ་འདི་ནི་བུདྡྷེསཏ་རེད། བོད་ཡིག་གི་ཚིག་གྲུབ་འདི་ནི་བུདྡྷེསཏ་རེད། buddhist"
                    }
                ]
            },
            {
                "text": {
                    "text_id": "e597eeb8-3142-4937-b1c7-f211b8230f2c",
                    "language": "en",
                    "title": "The Buddhist Path",
                    "published_date": "12-02-2025"
                },
                "segment_match": [
                    {
                        "segment_id": "25e50dbe-9243-4732-b1cf-a25c5e3e25c0",
                        "content": "This text is all about Buddhist Path"
                    }
                ]
            }
        ],
        "sheets": [
            {
                "sheet_title": "བཟོད་པའི་མཐུ་སྟོབས།",
                "sheet_summary": "བཟོད་པའི་ཕན་ཡོན་དང་ཁོང་ཁྲོའི་ཉེས་དམིགས་ཀྱི་གཏམ་རྒྱུད་འདི། ད་ལྟའང་བོད་ཀྱི་གྲོང་གསེབ་དེར་གླེང་སྒྲོས་སུ་གྱུར་ཡོད་དོ།། །། Buddhist Path",
                "publisher_id": 48,
                "sheet_id": 114,
                "publisher_name": "Yeshi Lhundup",
                "publisher_url": "/profile/yeshi-lhundup",
                "publisher_image": "https://storage.googleapis.com/pecha-profile-img/yeshi-lhundup-1742619970-small.png",
                "publisher_position": "LCM",
                "publisher_organization": "pecha.org"
            },
            {
                "sheet_title": "Teaching 1st Jan 2025",
                "sheet_summary": "sadf asdfas dfas Buddhist Path",
                "publisher_id": 61,
                "sheet_id": 170,
                "publisher_name": "Yeshi Lhundup",
                "publisher_url": "/profile/yeshi-lhundup2",
                "publisher_image": "",
                "publisher_position": "",
                "publisher_organization": ""
            }
        ]
    }
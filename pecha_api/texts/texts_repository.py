import uuid


from .texts_models import Text, Segment
from .texts_response_models import CreateTextRequest, CreateSegmentRequest

import datetime

def get_texts_by_id():
    root_text = Text(
        id=uuid.uuid4(),
        titles={"en": "Root Text title", "bo": "Root གྲྭ་ཚན"},
        summaries={"en": "Root Summaries", "bo": "Root སྙིང་བསྡུས་"},
        default_language="bo"
    )
    versions = [
        Text(
            id=uuid.uuid4(),
            titles={"en": f"Version Topic {i}", "bo": f"Version གྲྭ་ཚན {i}"},
            summaries={"en": f"Version Summaries {i}", "bo": f"Version སྙིང་བསྡུས་ {i}"},
            default_language="bo"
        )
        for i in range(1, 6)
    ]
    return root_text, versions


async def create_text(create_text_request: CreateTextRequest) -> Text:
    new_text = Text(
        titles=create_text_request.titles,
        language=create_text_request.language,
        is_published=True,
        created_date=str(datetime.datetime.utcnow()),
        updated_date=str(datetime.datetime.utcnow()),
        published_date=str(datetime.datetime.utcnow()),
        published_by=create_text_request.published_by,
        type=create_text_request.type,
        categories=create_text_request.categories
    )
    saved_text = await new_text.insert()
    return saved_text

async def create_segment(create_segment_request: CreateSegmentRequest) -> Segment:
    new_segment = Segment(
        text_id=create_segment_request.text_id,
        content=create_segment_request.content,
        mapping=create_segment_request.mapping
    )
    saved_segment = await new_segment.insert()
    return saved_segment

async def get_texts_by_category(category: str, language: str, skip: int, limit: int):
    return [
        {
            "id": "uuid.v4",
            "title": "The Way of the Bodhisattva",
            "language": "en",
            "type": "root_text",
            "is_published": True,
            "created_date": "2021-09-01T00:00:00.000Z",
            "updated_date": "2021-09-01T00:00:00.000Z",
            "published_date": "2021-09-01T00:00:00.000Z",
            "published_by": "buddhist_tab"
        },
        {
            "id": "uuid.v4",
            "title": "Commentary on the difficult points of The Way of Bodhisattvas",
            "language": "en",
            "type": "commentary",
            "is_published": True,
            "created_date": "2021-09-01T00:00:00.000Z",
            "updated_date": "2021-09-01T00:00:00.000Z",
            "published_date": "2021-09-01T00:00:00.000Z",
            "published_by": "buddhist_tab"
        },
        {
            "id": "uuid.v4",
            "title": "Khenpo Kunpel's commentary on the Bodhicaryavatara",
            "language": "en",
            "type": "commentary",
            "is_published": True,
            "created_date": "2021-09-01T00:00:00.000Z",
            "updated_date": "2021-09-01T00:00:00.000Z",
            "published_date": "2021-09-01T00:00:00.000Z",
            "published_by": "buddhist_tab"
        }
    ]


import uuid

from .texts_models import Text, Segment
from .texts_response_models import CreateTextRequest, CreateSegmentRequest

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
        is_published=create_text_request.is_published,
        created_date=create_text_request.created_date,
        updated_date=create_text_request.updated_date,
        published_date=create_text_request.published_date,
        published_by=create_text_request.published_by,
        type=create_text_request.type,
        categories=create_text_request.categories
    )
    saved_text = await new_text.insert()
    return saved_text

async def create_segment(text_id: str, create_segment_request: CreateSegmentRequest) -> Segment:
    new_segment = Segment(
        text_id=text_id,
        content=create_segment_request.content,
        mapping=create_segment_request.mapping
    )
    saved_segment = await new_segment.insert()
    return saved_segment
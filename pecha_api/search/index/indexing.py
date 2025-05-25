from ..search_client import search_client
from pecha_api.config import get
from ...texts.segments.segments_models import Segment
from ...texts.texts_models import Text

async def index_text(text: Text):
    client = await search_client()

    # Convert UUID to string for serialization
    text_dict = {
        "id": str(text.id),
        "content_type": "text",
        "title": text.title,
        "language": text.language,
        "type": text.type,
        "categories": text.categories,
        "created_date": text.created_date,
        "updated_date": text.updated_date,
        "published_date": text.published_date,
        "is_published": text.is_published
    }

    await client.index(
        index=get("ELASTICSEARCH_CONTENT_INDEX"),
        id=str(text.id),
        document=text_dict
    )


async def index_segment(segment: Segment):
    """Index a segment document in Elasticsearch"""
    client = await search_client()
    # Get text details to enrich the segment
    text = await Text.get_text(text_id=segment.text_id)
    segment_dict = {
        "id": str(segment.id),
        "text_id": segment.text_id,
        "content": segment.content,
        "language": text.language if text else None,
        "mapping": [
            {
                "text_id": m.text_id,
                "segments": m.segments
            } for m in segment.mapping
        ]
    }

    await client.index(
        index=get("ELASTICSEARCH_SEGMENT_INDEX"),
        id=str(segment.id),
        document=segment_dict
    )
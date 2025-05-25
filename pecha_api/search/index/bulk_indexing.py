from ...texts.texts_models import Text
from ..index.indexing import index_text, index_segment
from ...texts.segments.segments_models import Segment
from ..search_client import search_client
from pecha_api.config import get

async def index_all_texts():
    """Index all existing texts in Elasticsearch"""
    print("Indexing all texts...")
    texts = await Text.find().to_list()
    count = 0
    for text in texts:
        await index_text(text)
        count += 1
        if count % 100 == 0:
            print(f"Indexed {count} texts")
    print(f"Indexed {count} texts in total")


async def index_all_segments():
    """Index all existing segments in Elasticsearch"""
    print("Indexing all segments...")
    # Process segments in batches to avoid memory issues
    batch_size = 500
    skip = 0
    total_indexed = 0

    while True:
        segments = await Segment.find().skip(skip).limit(batch_size).to_list()
        if not segments:
            break

        for segment in segments:
            await index_segment(segment)
            total_indexed += 1

        print(f"Indexed {total_indexed} segments")
        skip += batch_size

    print(f"Indexed {total_indexed} segments in total")


async def reindex_all():
    """Reindex all content in Elasticsearch"""
    # Delete existing indices
    es = await search_client()
    content_index = get("ELASTICSEARCH_CONTENT_INDEX")
    segment_index = get("ELASTICSEARCH_SEGMENT_INDEX")

    for index in [content_index, segment_index]:
        if await es.indices.exists(index=index):
            await es.indices.delete(index=index)
            print(f"Deleted index {index}")
            await es.indices.create(index=index)
            print(f"Recreated index {index}")

    # Reindex all content
    await index_all_texts()
    await index_all_segments()

    print("Reindexing complete!")
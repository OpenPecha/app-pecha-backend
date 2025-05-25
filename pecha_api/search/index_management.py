from .search_client import search_client
from pecha_api.config import get
async def setup_indices():
    client = await search_client()

    # Get index names from config
    content_index = get("ELASTICSEARCH_CONTENT_INDEX")
    segment_index = get("ELASTICSEARCH_SEGMENT_INDEX")

    for index_name in [content_index, segment_index]:
        if not await client.indices.exists(index=index_name):
            await client.indices.create(index=index_name)
            print(f"Created index {index_name}")
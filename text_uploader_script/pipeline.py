from text_uploader_script.collections.collection_service import CollectionService


async def pipeline():


    destination_url = DestinationURL.LOCAL.value
    # collection upload
    collection = CollectionService()
    await collection.upload_collections(destination_url)
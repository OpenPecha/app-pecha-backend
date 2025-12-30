from text_uploader_script.collections.collection_service import CollectionService
from text_uploader_script.constants import DestinationURL, OpenPechaAPIURL


async def pipeline():


    destination_url = DestinationURL.LOCAL.value
    openpecha_api_url = OpenPechaAPIURL.DEVELOPMENT.value
    # collection upload
    collection = CollectionService()
    await collection.upload_collections(destination_url, openpecha_api_url)
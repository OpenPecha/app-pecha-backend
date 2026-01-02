import asyncio
from fastapi import HTTPException
from starlette import status
from pecha_api.error_contants import ErrorConstants


from pecha_api.text_uploader.collections.collection_service import CollectionService
from pecha_api.text_uploader.text_metadata.text_metadata_service import TextMetadataService
from pecha_api.text_uploader.text_uploader_response_model import TextUploadRequest
from pecha_api.users.users_service import verify_admin_access


async def pipeline(text_upload_request: TextUploadRequest, token: str):

    is_admin = verify_admin_access(token=token)
    if not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.ADMIN_ERROR_MESSAGE)

    # collection upload
    # collection = CollectionService()
    # await collection.upload_collections(text_upload_request=text_upload_request, token=token)

    # text metadata upload
    text_metadata = TextMetadataService()
    await text_metadata.upload_text_metadata_service(text_upload_request=text_upload_request, token=token)
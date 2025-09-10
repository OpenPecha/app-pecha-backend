from fastapi import APIRouter, UploadFile, File, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .media_service import upload_media_file
from .media_response_models import MediaUploadResponse
from typing import Annotated

oauth2_scheme = HTTPBearer()

media_router = APIRouter(
    prefix="/cms/media",
    tags=["Media"]
)


@media_router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_media_image(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)], file: UploadFile = File()
) -> MediaUploadResponse:
    return upload_media_file(token=authentication_credential.credentials, file=file, plan_id=None)

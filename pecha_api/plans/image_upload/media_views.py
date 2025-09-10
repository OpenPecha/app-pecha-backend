from fastapi import APIRouter, UploadFile, File, status
from .media_service import upload_media_file
from .media_response_models import MediaUploadResponse


media_router = APIRouter(
    prefix="/cms/media",
    tags=["Media"]
)


@media_router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_media_image(
    file: UploadFile = File()
) -> MediaUploadResponse:
    return upload_media_file(file=file, plan_id=None)

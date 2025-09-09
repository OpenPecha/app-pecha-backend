from fastapi import APIRouter, UploadFile, File, Form, status
from typing import Annotated
from .media_service import upload_media_file
from .media_response_models import MediaUploadResponse, Error


media_router = APIRouter(
    prefix="/cms/media",
    tags=["Media"]
)


@media_router.post("/upload", status_code=status.HTTP_201_CREATED,
    response_model=MediaUploadResponse,
    responses={
        400: {
            "model": Error,
            "description": "Invalid file format or size",
            "content": {
                "application/json": {
                    "example": {
                        "error": "invalid_file",
                        "message": "Only JPEG, PNG, and WebP images are allowed. Maximum size: 5MB"
                    }
                }
            }
        },
        413: {
            "model": Error,
            "description": "File too large",
            "content": {
                "application/json": {
                    "example": {
                        "error": "file_too_large",
                        "message": "File size exceeds 5MB limit"
                    }
                }
            }
        }
    },
)

def upload_media_image(
    file: UploadFile = File(),
    path: str = Form()
) -> MediaUploadResponse:
    return upload_media_file(file=file, path=path)

from __future__ import annotations
from fastapi import APIRouter
from fastapi.security import HTTPBearer
from starlette import status

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated


from .sheets_service import create_new_sheet, upload_sheet_image_request
from .sheets_response_models import CreateSheetRequest

oauth2_scheme = HTTPBearer()
sheets_router = APIRouter(
    prefix="/sheets",
    tags=["Sheets"]
)


@sheets_router.post("", status_code=status.HTTP_201_CREATED)
async def create_sheet(
    create_sheet_request: CreateSheetRequest,
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
):
    return await create_new_sheet(
        create_sheet_request=create_sheet_request,
        token=authentication_credential.credentials
    )

@sheets_router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_sheet_image(sheet_id: Optional[str] = None, file: UploadFile = File(...)):
    return upload_sheet_image_request(sheet_id=sheet_id, file=file)


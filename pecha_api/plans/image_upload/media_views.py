from fastapi import APIRouter, UploadFile, File, status, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .media_services import upload_plan_image
from .media_response_models import PlanUploadResponse
from typing import Annotated, Optional

oauth2_scheme = HTTPBearer()

media_router = APIRouter(
    prefix="/cms/media",
    tags=["Media"]
)


@media_router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_media_image(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)], plan_id: Optional[str] = Query(None), file: UploadFile = File(...)) -> PlanUploadResponse:
    return upload_plan_image(token=authentication_credential.credentials, plan_id=plan_id, file=file)

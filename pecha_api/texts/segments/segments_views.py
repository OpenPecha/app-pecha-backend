from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import APIRouter, Depends
from starlette import status

from typing import Annotated, List

from .segments_service import create_new_segment
from .segments_response_models import CreateSegmentRequest

oauth2_scheme = HTTPBearer()
segment_router = APIRouter(
    prefix="/segments",
    tags=["Segments"]
)

@segment_router.post("", status_code=status.HTTP_201_CREATED)
async def create_segment(
    create_segment_request: CreateSegmentRequest,
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
    ):
    return await create_new_segment(create_segment_request=create_segment_request, token=authentication_credential.credentials)
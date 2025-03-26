from fastapi import APIRouter
from fastapi.security import HTTPBearer
from starlette import status

from texts.mappings.mappings_response_models import TextMappingRequest
from texts.mappings.mappings_service import update_segment_mapping

oauth2_scheme = HTTPBearer()

mapping_router = APIRouter(
    prefix="/mappings",
    tags=["Text Mapping"]
)


@mapping_router.post("",status_code=status.HTTP_201_CREATED)
async def create_text_mapping(text_mapping_request: TextMappingRequest):
    return await update_segment_mapping(text_mapping_request=text_mapping_request)
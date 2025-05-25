from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from .indexing_reponse_model import ReindexRequest, ReindexResponse
from .indexing_service import index_document

from typing import Annotated

oauth2_scheme = HTTPBearer()

index_router = APIRouter(
    prefix="/indeces",
    tags=["Indexing"]
)


@index_router.post("", status_code=status.HTTP_202_ACCEPTED)
async def reindex(
        background_tasks: BackgroundTasks,
        reindex_request: ReindexRequest,
        authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]
) -> ReindexResponse:
    return await index_document(
        background_tasks=background_tasks,
        reindex_request=reindex_request,
        token=authentication_credential.credentials
    )

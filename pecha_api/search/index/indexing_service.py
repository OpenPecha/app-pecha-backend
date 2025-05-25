
from ...users.users_service import verify_admin_access
from fastapi import HTTPException
from starlette import status
from pecha_api.error_contants import ErrorConstants
from .indexing_reponse_model import ReindexResponse, ReindexRequest
from .bulk_indexing import reindex_all
from fastapi import BackgroundTasks

async def index_document(
        background_tasks: BackgroundTasks,
        reindex_request:
        ReindexRequest, token: str
):
    is_admin = await verify_admin_access(token=token)
    if is_admin:
        background_tasks.add_task(
            reindex_all,
            recreate_indices=reindex_request.recreate_indices
        )
        return ReindexResponse(
            status="accepted",
            message="Reindexing all content in the background"
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.ADMIN_ERROR_MESSAGE)


from fastapi import APIRouter
from .plan_items_response_models import ItemDTO
from .plan_items_services import create_plan_item, delete_plan_day_by_id
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from starlette import status
from uuid import UUID
from typing import Annotated
oauth2_scheme = HTTPBearer()

items_router = APIRouter(
    prefix="/cms/plans",
    tags=["Items"],
)

@items_router.post("/{plan_id}/days", status_code=status.HTTP_201_CREATED, response_model=ItemDTO)
async def create_new_item(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
                      plan_id: UUID):

    return create_plan_item(
        token=authentication_credential.credentials,
        plan_id=plan_id
    )

@items_router.delete("/{plan_id}/days/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
                      plan_id: UUID,
                      day_id: UUID):
    return delete_plan_day_by_id(
        token=authentication_credential.credentials,
        plan_id=plan_id,
        day_id=day_id
    )

from typing import Optional

from starlette import status

from pecha_api.error_contants import ErrorConstants
from pecha_api.utils import Utils
from ..config import get
from ..collections.collections_response_models import CollectionModel, CollectionsResponse, Pagination, CreateCollectionRequest, UpdateCollectionRequest
from .collections_repository import get_child_count, get_collections_by_parent, create_collection, update_collection_titles, delete_collection, \
    get_collection_by_id
from ..users.users_service import verify_admin_access
from fastapi import HTTPException


async def get_all_collections(language: str, parent_id: Optional[str], skip: int, limit: int) -> CollectionsResponse:
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    total = await get_child_count(parent_id=parent_id)
    parent_collection = await get_collection(collection_id=parent_id,language=language)
    collections = await get_collections_by_parent(
        parent_id=parent_id,
        skip=skip,
        limit=limit
    )
    collection_list = [
        CollectionModel(
            id=str(collection.id),
            title=Utils.get_value_from_dict(values=collection.titles, language=language),
            description=Utils.get_value_from_dict(values=collection.descriptions, language=language),
            has_child=collection.has_sub_child,
            slug=collection.slug
        )
        for collection in collections
    ]   
    pagination = {
        "total": total,
        "skip": skip,
        "limit": limit
    }
    collection_response = CollectionsResponse(parent=parent_collection, pagination=pagination, collections=collection_list)
    return collection_response


async def create_new_collection(create_collection_request: CreateCollectionRequest, token: str, language: Optional[str]) -> CollectionModel:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        new_collection = await create_collection(create_collection_request=create_collection_request)
        if language is None:
            language = get("DEFAULT_LANGUAGE")
        return CollectionModel(
            id=str(new_collection.id),
            title=Utils.get_value_from_dict(values=new_collection.titles, language=language),
            description=Utils.get_value_from_dict(values=new_collection.descriptions, language=language),
            has_child=new_collection.has_sub_child,
            slug=new_collection.slug
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.ADMIN_ERROR_MESSAGE)

async def get_collection(collection_id: str,language: str) -> Optional[CollectionModel]:
    selected_collection = await get_collection_by_id(collection_id=collection_id)
    if selected_collection:
        return CollectionModel(
            id=collection_id,
            title=Utils.get_value_from_dict(values=selected_collection.titles, language=language),
            description=Utils.get_value_from_dict(values=selected_collection.descriptions, language=language),
            has_child=selected_collection.has_sub_child,
            slug=selected_collection.slug
        )
    return None

async def update_existing_collection(collection_id: str, update_collection_request: UpdateCollectionRequest, token: str,
                               language: Optional[str]) -> CollectionModel:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        updated_collection = await update_collection_titles(collection_id=collection_id, update_collection_request=update_collection_request)
        if language is None:
            language = get("DEFAULT_LANGUAGE")
        return CollectionModel(
            id=collection_id,
            title=Utils.get_value_from_dict(values=updated_collection.titles, language=language),
            description=Utils.get_value_from_dict(values=updated_collection.descriptions, language=language),
            has_child=updated_collection.has_sub_child,
            slug=updated_collection.slug
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.ADMIN_ERROR_MESSAGE)


async def delete_existing_collection(collection_id: str, token: str):
    is_admin = verify_admin_access(token=token)
    if is_admin:
        await delete_collection(collection_id=collection_id)
        return collection_id
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.ADMIN_ERROR_MESSAGE)

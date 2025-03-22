from fastapi import HTTPException
from starlette import status

from .texts_repository import get_contents_by_id_with_segments, get_texts_by_id, get_contents_by_id, get_text_by_id, get_versions_by_id, get_texts_by_category, get_versions_by_id, create_text
from .texts_repository import get_text_infos
from .texts_response_models import TableOfContentResponse, TextModel, TextVersionResponse, TextVersion, Category, TextsCategoryResponse, Text, CreateTextRequest
from .texts_response_models import TextInfosResponse
from ..users.users_service import verify_admin_access

from ..terms.terms_service import get_term

from typing import List

from ..constants import get_mapped_table_of_contents_segments
from pecha_api.config import get

async def get_texts_by_category_id(category: str, language: str, skip: int, limit: int):
    texts = await get_texts_by_category(category=category, language=language, skip=skip, limit=limit)
    text_list = [
        Text(
            id=text["id"],
            title=text["title"],
            language=text["language"],
            type=text["type"],
            is_published=text["is_published"],
            created_date=text["created_date"],
            updated_date=text["updated_date"],
            published_date=text["published_date"],
            published_by=text["published_by"]
        )
        for text in texts
    ]
    return text_list

async def get_texts_without_category(text_id: str) -> TextModel:
    text = await get_texts_by_id(text_id=text_id)
    if text is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Text not found")
    return TextModel(
        id=str(text.id),
        title=text.title,
        language=text.language,
        parent_id=text.parent_id,
        type=text.type,
        is_published=text.is_published,
        created_date=text.created_date,
        updated_date=text.updated_date,
        published_date=text.published_date,
        published_by=text.published_by,
        categories=text.categories
    )
  

async def get_text_by_term_or_category(
        text_id: str,
        category: str,
        language: str,
        skip: int,
        limit: int
    ):
    if language is None:
        language = get("DEFAULT_LANGUAGE")

    if category is not None:
        term = await get_term(term_id=category, language=language)
        texts = await get_texts_by_category_id(category=category, language=language, skip=skip, limit=limit)
        return TextsCategoryResponse(
            category=term,
            texts=texts,
            total=len(texts),
            skip=skip,
            limit=limit
        )
    else:
        return await get_texts_without_category(text_id=text_id)

async def get_contents_by_text_id(text_id: str, skip:int, limit: int) -> TableOfContentResponse:
    table_of_contents = await get_contents_by_id(text_id=text_id, skip=skip, limit=limit)
    return TableOfContentResponse(
        contents=table_of_contents
    )

async def get_contents_by_text_id_with_detail(text_id: str, content_id: str, skip: int, limit: int) -> TableOfContentResponse:
    table_of_contents = await get_contents_by_id_with_segments(text_id=text_id, content_id=content_id, skip=skip, limit=limit)
    table_of_contents_with_details = await get_mapped_table_of_contents_segments(table_of_contents=table_of_contents)
    return TableOfContentResponse(
        contents=table_of_contents_with_details
    )

async def get_versions_by_text_id(text_id: str, skip: int, limit: int) -> TextVersionResponse:
    root_text = await get_text_by_id(text_id=text_id)
    versions = await get_versions_by_id(text_id=text_id, skip=skip, limit=limit)
    list_of_version = [
        TextVersion(
            id=version["id"],
            title=version["title"],
            parent_id=version["parent_id"],
            priority=version["priority"],
            language=version["language"],
            type=version["type"],
            is_published=version["is_published"],
            created_date=version["created_date"],
            updated_date=version["updated_date"],
            published_date=version["published_date"],
            published_by=version["published_by"]
        )
        for version in versions
    ]
    return TextVersionResponse(
        text=root_text,
        versions=list_of_version
    )


async def create_new_text(
    create_text_request: CreateTextRequest,
    token: str
    ) -> TextModel:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        new_text = await create_text(create_text_request=create_text_request)
        return TextModel(
            id=str(new_text.id),
            title=new_text.title,
            language=new_text.language,
            type=new_text.type,
            is_published=new_text.is_published,
            created_date=new_text.created_date,
            updated_date=new_text.updated_date,
            published_date=new_text.published_date,
            published_by=new_text.published_by,
            categories=new_text.categories,
            parent_id=new_text.parent_id
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

async def get_infos_by_text_id(text_id: str, skip: int, limit: int) -> TextInfosResponse:
    text_infos = await get_text_infos(text_id=text_id, skip=skip, limit=limit)
    return TextInfosResponse(
        text_infos=text_infos
    )
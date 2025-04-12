
from fastapi import HTTPException
from starlette import status

from pecha_api.error_contants import ErrorConstants
from pecha_api.utils import Utils
from .texts_repository import (
    get_texts_by_id,
    get_texts_by_term, 
    get_versions_by_id, 
    create_text,
    create_table_of_content_detail,
    get_text_infos, 
    get_contents_by_id, 
    get_table_of_content_by_content_id
)
from .texts_response_models import (
    TableOfContent, 
    DetailTableOfContentResponse, 
    TableOfContentResponse, 
    TextModel, 
    TextVersionResponse, 
    TextVersion,
    TextsCategoryResponse, 
    Text, 
    CreateTextRequest, 
    TextDetailsRequest,
    TextInfosResponse, 
    TextInfos, 
    RelatedTexts
)
from .texts_utils import TextUtils
from ..users.users_service import verify_admin_access
from ..terms.terms_service import get_term
from .segments.segments_service import validate_segments_exists

from typing import List
from pecha_api.config import get



# These functions have been moved to the TextUtils class

async def get_texts_by_term_id(term_id: str, skip: int, limit: int):
    texts = await get_texts_by_term(term_id=term_id, skip=skip, limit=limit)
    text_list = [
        Text(
            id=str(text.id),
            title=text.title,
            language=text.language,
            type=text.type,
            is_published=text.is_published,
            created_date=text.created_date,
            updated_date=text.updated_date,
            published_date=text.published_date,
            published_by=text.published_by
        )
        for text in texts
    ]
    return text_list



async def get_text_detail_by_id(text_id: str) -> TextModel:
    if text_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.TEXT_OR_TERM_NOT_FOUND_MESSAGE)
    text = await get_texts_by_id(text_id=text_id)
    if text is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
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


async def get_text_by_text_id_or_term(
        text_id: str,
        term_id: str,
        language: str,
        skip: int,
        limit: int
):
    if language is None:
        language = get("DEFAULT_LANGUAGE")

    if term_id is not None:
        term = await get_term(term_id=term_id, language=language)
        texts = await get_texts_by_term_id(term_id=term_id, skip=skip, limit=limit)
        return TextsCategoryResponse(
            term=term,
            texts=texts,
            total=len(texts),
            skip=skip,
            limit=limit
        )
    else:
        return await get_text_detail_by_id(text_id=text_id)


async def get_table_of_contents_by_text_id(text_id: str, skip: int, limit: int) -> List[TableOfContent]:
    is_valid_text = await TextUtils.validate_text_exists(text_id=text_id)
    if not is_valid_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    text = await get_text_detail_by_id(text_id=text_id)
    table_of_contents = await get_contents_by_id(text_id=text_id, skip=skip, limit=limit)
    return TableOfContentResponse(
        text_detail=text,
        contents= [
            TableOfContent(
                id=str(content.id),
                text_id=content.text_id,
                sections=content.sections
            )
            for content in table_of_contents
        ]
    )

async def get_text_details_by_text_id(text_id: str, text_details_request: TextDetailsRequest) -> DetailTableOfContentResponse:
    if text_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.TEXT_OR_TERM_NOT_FOUND_MESSAGE)
    is_valid_text = await TextUtils.validate_text_exists(text_id=text_id)
    if is_valid_text:
        text = await get_text_detail_by_id(text_id=text_id)
        table_of_content = await get_table_of_content_by_content_id(content_id=text_details_request.content_id)
        total_sections = len(table_of_content.sections)
        if table_of_content is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TABLE_OF_CONTENT_NOT_FOUND_MESSAGE)
        table_of_content.sections = table_of_content.sections[text_details_request.skip:text_details_request.skip+text_details_request.limit]
        detail_table_of_content = await TextUtils.convert_to_detail_table_of_content(table_of_content)
        return DetailTableOfContentResponse(
            text_detail=text,
            contents=[
                detail_table_of_content
            ],
            skip=text_details_request.skip,
            limit=text_details_request.limit,
            total=total_sections
        )
            
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)



async def get_versions_by_text_id(text_id: str, skip: int, limit: int) -> TextVersionResponse:
    root_text = await get_text_detail_by_id(text_id=text_id)
    if root_text is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    versions = await get_versions_by_id(text_id=text_id, skip=skip, limit=limit)
    list_of_version = [
        TextVersion(
            id=str(version.id),
            title=version.title,
            parent_id=version.parent_id,
            language=version.language,
            type=version.type,
            is_published=version.is_published,
            created_date=version.created_date,
            updated_date=version.updated_date,
            published_date=version.published_date,
            published_by=version.published_by
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


async def get_infos_by_text_id(text_id: str, language: str, skip: int, limit: int) -> TextInfosResponse:
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    text_infos = await get_text_infos(text_id=text_id, language=language, skip=skip, limit=limit)
    related_text = [
        RelatedTexts(
            id=text_info["id"],
            title=Utils.get_value_from_dict(text_info["title"], language),
            count=text_info["count"]
        )
        for text_info in text_infos
    ]
    return TextInfosResponse(
        text_infos= TextInfos(
            text_id=text_id,
            about_text="",
            translations=30,
            related_texts=related_text,
            sheets=3,
            web_pages=2,
            short_url=""
        )
    )

async def create_table_of_content(table_of_content_request: TableOfContent, token: str):
    is_admin = verify_admin_access(token=token)
    if is_admin:
        valid_text = await TextUtils.validate_text_exists(text_id=table_of_content_request.text_id)
        if valid_text:
            segment_ids = TextUtils.get_all_segment_ids(table_of_content=table_of_content_request)
            valid_segments = await validate_segments_exists(segment_ids=segment_ids)
            if not valid_segments:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
            table_of_content = await create_table_of_content_detail(table_of_content_request=table_of_content_request)
            return table_of_content
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.ADMIN_ERROR_MESSAGE)



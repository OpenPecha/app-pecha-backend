
from fastapi import HTTPException
from starlette import status

from pecha_api.error_contants import ErrorConstants
from pecha_api.utils import Utils
from .texts_repository import (
    get_texts_by_term, 
    get_versions_by_id, 
    create_text,
    create_table_of_content_detail,
    get_contents_by_id, 
    get_table_of_content_by_content_id,
    get_sections_count_of_table_of_content
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
    TextDetailsRequest
)
from .texts_utils import TextUtils
from ..users.users_service import verify_admin_access
from ..terms.terms_service import get_term
from .segments.segments_utils import SegmentUtils

from typing import List
from pecha_api.config import get


# These functions have been moved to the TextUtils class

async def get_texts_by_term_id(term_id: str, skip: int, limit: int) -> List[Text]:
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



# This function has been moved to TextUtils class


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
        return await TextUtils.get_text_detail_by_id(text_id=text_id)


async def get_table_of_contents_by_text_id(text_id: str, skip: int, limit: int) -> TableOfContentResponse:
    is_valid_text = await TextUtils.validate_text_exists(text_id=text_id)
    if not is_valid_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    text = await TextUtils.get_text_detail_by_id(text_id=text_id)
    table_of_contents = await get_contents_by_id(text_id=text_id)
    table_of_contents = TextUtils.remove_segments_from_list_of_table_of_content(table_of_content=table_of_contents)
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
        text = await TextUtils.get_text_detail_by_id(text_id=text_id)
        if text_details_request.segment_id is not None:
            table_of_content = await TextUtils.get_table_of_content_id_and_section_number_by_segment_id(text_id=text_id, segment_id=text_details_request.segment_id)
        else:
            table_of_content = await get_table_of_content_by_content_id(content_id=text_details_request.content_id, skip=text_details_request.skip, limit=text_details_request.limit)
        total_sections = await get_sections_count_of_table_of_content(content_id=table_of_content.id)
        if table_of_content is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TABLE_OF_CONTENT_NOT_FOUND_MESSAGE)
        detail_table_of_content = await SegmentUtils.get_mapped_segment_content(table_of_content=table_of_content, version_id=text_details_request.version_id)
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
    root_text = await TextUtils.get_text_detail_by_id(text_id=text_id)
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


async def create_table_of_content(table_of_content_request: TableOfContent, token: str) -> TableOfContent:
    is_admin = verify_admin_access(token=token)
    if is_admin:
        valid_text = await TextUtils.validate_text_exists(text_id=table_of_content_request.text_id)
        if valid_text:
            segment_ids = TextUtils.get_all_segment_ids(table_of_content=table_of_content_request)
            valid_segments = await SegmentUtils.validate_segments_exists(segment_ids=segment_ids)
            if not valid_segments:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)
            table_of_content = await create_table_of_content_detail(table_of_content_request=table_of_content_request)
            return table_of_content
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.ADMIN_ERROR_MESSAGE)



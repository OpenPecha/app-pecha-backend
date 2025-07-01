from __future__ import annotations

import logging
from typing import List, Optional, Dict
from uuid import UUID

from beanie.exceptions import CollectionWasNotInitialized
from pecha_api.constants import Constants
from .texts_response_models import (
    CreateTextRequest, 
    TableOfContent, 
    TextDTO,
    UpdateTextRequest
)
from .texts_models import Text, TableOfContent
from datetime import datetime, timezone
from pecha_api.utils import Utils

async def get_sections_count_of_table_of_content(content_id: str) -> int:
    return await TableOfContent.get_sections_count(content_id=content_id)

async def get_texts_by_id(text_id: str) -> Text | None:
    try:
        text = await Text.get_text(text_id=text_id)
        return text
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return None

async def get_texts_by_ids(text_ids: List[str]) -> Dict[str, TextDTO]:
    list_of_texts_detail = await Text.get_texts_by_ids(text_ids=text_ids)
    return {
        str(text.id): TextDTO(
            id=str(text.id),
            title=text.title,
            language=text.language,
            type=text.type,
            group_id=text.group_id,
            is_published=text.is_published,
            created_date=text.created_date,
            updated_date=text.updated_date,
            published_date=text.published_date,
            published_by=text.published_by,
            categories=text.categories,
            views=text.views
        )
        for text in list_of_texts_detail
    }

async def get_sheets(published_by: Optional[str] = None, is_published: bool = None, skip: int = 0, limit: int = 10) -> List[TextDTO]:
    sheets = await Text.get_sheets(published_by=published_by, is_published=is_published, skip=skip, limit=limit)
    return [
        TextDTO(
            id=str(sheet.id),
            title=sheet.title,
            language=sheet.language,
            group_id=sheet.group_id,
            type=sheet.type,
            is_published=sheet.is_published,
            created_date=sheet.created_date,
            updated_date=sheet.updated_date,
            published_date=sheet.published_date,
            published_by=sheet.published_by,
            categories=sheet.categories,
            views=sheet.views
        )
        for sheet in sheets
    ]



async def check_text_exists(text_id: UUID) -> bool:
    try:
        is_text_exits = await Text.check_exists(text_id=text_id)
        return is_text_exits
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return False

async def check_all_text_exists(text_ids: List[UUID]) -> bool:
    try:
        is_text_exits = await Text.exists_all(text_ids=text_ids,batch_size=Constants.QUERY_BATCH_SIZE)
        return is_text_exits
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return False

async def get_texts_by_term(term_id: str, language: str, skip: int, limit: int) -> List[Text]:
    return await Text.get_texts_by_term_id(term_id=term_id, language=language, skip=skip, limit=limit)

async def get_texts_by_group_id(group_id: str, skip: int, limit: int) -> List[TextDTO]:
    texts = await Text.get_texts_by_group_id(group_id=group_id, skip=skip, limit=limit)
    return [
        TextDTO(
            id=str(text.id),
            title=text.title,
            language=text.language,
            group_id=text.group_id,
            type=text.type,
            is_published=text.is_published,
            created_date=text.created_date,
            updated_date=text.updated_date,
            published_date=text.published_date,
            published_by=text.published_by,
            categories=text.categories,
            views=text.views
        )
        for text in texts
    ]

async def get_texts_by_type(text_type: str, is_published: Optional[bool] = None, skip: int = 0, limit: int = 10) -> List[TextDTO]:
    from .texts_enums import TextType
    texts = await Text.get_texts_by_type(text_type=TextType(text_type), is_published=is_published, skip=skip, limit=limit)
    return [
        TextDTO(
            id=str(text.id),
            title=text.title,
            language=text.language,
            group_id=text.group_id,
            type=text.type,
            is_published=text.is_published,
            created_date=text.created_date,
            updated_date=text.updated_date,
            published_date=text.published_date,
            published_by=text.published_by,
            categories=text.categories,
            views=text.views
        )
        for text in texts
    ]


async def create_text(create_text_request: CreateTextRequest) -> Text:
    new_text = Text(
        title=create_text_request.title,
        language=create_text_request.language,
        group_id=create_text_request.group_id,
        is_published=create_text_request.isPublished,
        created_date=str(datetime.now(timezone.utc)),
        updated_date=str(datetime.now(timezone.utc)),
        published_date=str(datetime.now(timezone.utc)),
        published_by=create_text_request.published_by,
        type=create_text_request.type,
        categories=create_text_request.categories,
        views=create_text_request.views
    )
    saved_text = await new_text.insert()
    return saved_text

async def create_table_of_content_detail(table_of_content_request: TableOfContent):
    new_table_of_content = TableOfContent(
        text_id=table_of_content_request.text_id,
        sections=table_of_content_request.sections
    )
    saved_table_of_content = await new_table_of_content.insert()
    return saved_table_of_content

async def get_contents_by_id(text_id: str) -> List[TableOfContent]:
    return await TableOfContent.get_table_of_contents_by_text_id(text_id=text_id)
    
async def get_table_of_content_by_content_id(content_id: str, skip: int, limit: int) -> Optional[TableOfContent]:
    return await TableOfContent.get_table_of_content_by_content_id(content_id=content_id, skip=skip, limit=limit)


async def delete_table_of_content_by_text_id(text_id: str):
    return await TableOfContent.delete_table_of_content_by_text_id(text_id=text_id)

async def update_text_details_by_id(text_id: str, update_text_request: UpdateTextRequest) -> TextDTO:
    text_details = await Text.get_text(text_id=text_id)
    text_details.title = update_text_request.title
    text_details.is_published = update_text_request.is_published
    text_details.updated_date = Utils.get_utc_date_time()
    await text_details.save()
    return text_details

async def delete_text_by_id(text_id: str):
    try:
        text_uuid = UUID(text_id)
        await Text.delete_text_by_id(text_id=text_uuid)
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return None
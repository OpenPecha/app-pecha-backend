from __future__ import annotations

import logging
from typing import List, Optional, Dict
from uuid import UUID

from beanie.exceptions import CollectionWasNotInitialized
from pecha_api.constants import Constants
from .texts_response_models import CreateTextRequest, TableOfContent, TextModel
from .texts_models import Text, TableOfContent
from datetime import datetime, timezone

async def get_sections_count_of_table_of_content(content_id: str) -> int:
    return await TableOfContent.get_sections_count(content_id=content_id)

async def get_texts_by_id(text_id: str) -> Text | None:
    try:
        text = await Text.get_text(text_id=text_id)
        return text
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return None

async def get_texts_by_ids(text_ids: List[str]) -> Dict[str, TextModel]:
    list_of_texts_detail = await Text.get_texts_by_ids(text_ids=text_ids)
    return {
        str(text.id): TextModel(
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
        for text in list_of_texts_detail
    }


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

async def get_versions_by_id(text_id: str, skip: int, limit: int) -> List[Text]:
    return await Text.get_versions_by_text_id(text_id=text_id, skip=skip, limit=limit)


async def create_text(create_text_request: CreateTextRequest) -> Text:
    new_text = Text(
        title=create_text_request.title,
        language=create_text_request.language,
        parent_id=create_text_request.parent_id,
        is_published=True,
        created_date=str(datetime.now(timezone.utc)),
        updated_date=str(datetime.now(timezone.utc)),
        published_date=str(datetime.now(timezone.utc)),
        published_by=create_text_request.published_by,
        type=create_text_request.type,
        categories=create_text_request.categories
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

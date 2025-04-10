from __future__ import annotations

import logging
import uuid
from typing import List
from uuid import UUID

from beanie.exceptions import CollectionWasNotInitialized
from pecha_api.constants import Constants
from .texts_response_models import CreateTextRequest, TextDetailsRequest, TableOfContent
from .texts_models import Text, TableOfContent
from datetime import datetime, timezone



async def get_texts_by_id(text_id: str) -> Text | None:
    try:
        text = await Text.get_text(text_id=text_id)
        return text
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return None


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

async def get_texts_by_term(term_id: str, skip: int, limit: int):
    return await Text.get_texts_by_term_id(term_id=term_id, skip=skip, limit=limit)

async def get_versions_by_id(text_id: str, skip: int, limit: int):
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

async def get_contents_by_id(text_id: str, skip: int, limit: int) -> List[TableOfContent]:
    return await TableOfContent.get_table_of_content_by_text_id(text_id=text_id)
    
async def get_table_of_content_by_id(content_id: str):
    return await TableOfContent.get_table_of_content_by_id(content_id=content_id)

async def get_text_infos(text_id: str, language: str, skip: int, limit: int):
    return [
        {
            "id": str(uuid.uuid4()),
            "title": {
                "en": "commentary",
                "bo": "འགྲེལ་བརྗོད།"
            },
            "count": 1
        }
    ]

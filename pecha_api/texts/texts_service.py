
import asyncio
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from starlette import status

from pecha_api.utils import Utils
from .segments.segments_repository import get_segments_by_list_of_id
from .texts_repository import (get_contents_by_id_with_segments, get_texts_by_id, get_contents_by_id, get_text_by_id,
                               get_texts_by_category, get_versions_by_id, create_text, check_all_text_exists,
                               check_text_exists)
from .texts_repository import get_text_infos
from .texts_response_models import TableOfContentResponse, TextModel, TextVersionResponse, TextVersion, \
     TextsCategoryResponse, Text, CreateTextRequest, Section
from .texts_response_models import TextInfosResponse, TextInfos, RelatedTexts
from ..users.users_service import verify_admin_access

from ..terms.terms_service import get_term

from typing import List
from pecha_api.config import get



async def validate_text_exits(text_id: str):
    uuid_text_id = UUID(text_id)
    is_exists =  await check_text_exists(text_id=uuid_text_id)
    if not is_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Text not found')


async def validate_texts_exits(text_ids: List[str]):
    uuid_text_ids = [UUID(text_id) for text_id in text_ids]
    all_exists =  await check_all_text_exists(text_ids=uuid_text_ids)
    if not all_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Text not found")


async def get_texts_by_category_id(category: str, language: str, skip: int, limit: int):
    texts = await get_texts_by_category(category=category, language=language, skip=skip, limit=limit)
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
        return await get_texts_by_id(text_id=text_id)


async def get_contents_by_text_id(text_id: str, skip: int, limit: int) -> TableOfContentResponse:
    table_of_contents = await get_contents_by_id(text_id=text_id, skip=skip, limit=limit)
    return TableOfContentResponse(
        text_detail=TextModel(
            id=str(uuid.uuid4()),
            title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
            language="bo",
            type="root_text",
            is_published=True,
            created_date="2021-09-01T00:00:00.000Z",
            updated_date="2021-09-01T00:00:00.000Z",
            published_date="2021-09-01T00:00:00.000Z",
            published_by="pecha",
            categories=[str(uuid.uuid4())],
            parent_id=None
        ),
        contents=table_of_contents
    )


async def get_contents_by_text_id_with_detail(text_id: str, content_id: str, skip: int,
                                              limit: int) -> TableOfContentResponse:
    table_of_contents = await get_contents_by_id_with_segments(text_id=text_id, content_id=content_id, skip=skip,
                                                               limit=limit)
    table_of_contents_with_details = await get_mapped_table_of_contents_segments(table_of_contents=table_of_contents)
    return TableOfContentResponse(
        text_detail=TextModel(
            id=str(uuid.uuid4()),
            title="བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
            language="bo",
            type="root_text",
            is_published=True,
            created_date="2021-09-01T00:00:00.000Z",
            updated_date="2021-09-01T00:00:00.000Z",
            published_date="2021-09-01T00:00:00.000Z",
            published_by="pecha",
            categories=[str(uuid.uuid4())],
            parent_id=None
        ),
        contents=table_of_contents_with_details
    )


async def get_versions_by_text_id(text_id: str, skip: int, limit: int) -> TextVersionResponse:
    root_text = await get_texts_by_id(text_id=text_id)
    if root_text is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Text not found")
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

async def replace_segments_id_with_segment_details_in_section(section: Optional[Section] = None) -> None:
    if section and section.segments:
        list_segment_id = [segment.segment_id for segment in section.segments if segment.segment_id]
        if list_segment_id:
            segments = await get_segments_by_list_of_id(segment_ids=list_segment_id)
            for segment in section.segments:
                segment_detail = segments.get(segment.segment_id)
                if segment_detail:
                    segment.content = segment_detail.content
                    segment.mapping = segment_detail.mapping
    if section.sections:
        await asyncio.gather(*[replace_segments_id_with_segment_details_in_section(section=sub_section) for sub_section in section.sections])


async def get_mapped_table_of_contents_segments(table_of_contents: List[Section]) -> List[Section]:
    return table_of_contents
    await asyncio.gather(*[replace_segments_id_with_segment_details_in_section(section) for section in table_of_contents])
    return table_of_contents

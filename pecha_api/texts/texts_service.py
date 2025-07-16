from fastapi import HTTPException
from starlette import status

from pecha_api.error_contants import ErrorConstants
from .texts_repository import (
    get_texts_by_term,
    get_texts_by_group_id,
    create_text,
    create_table_of_content_detail,
    get_contents_by_id,
    get_table_of_content_by_content_id,
    get_sections_count_of_table_of_content,
    delete_table_of_content_by_text_id,
    update_text_details_by_id,
    delete_text_by_id,
    fetch_sheets_from_db
)
from .texts_response_models import (
    TableOfContent,
    DetailTableOfContentResponse,
    TableOfContentResponse,
    TextDTO,
    TextVersionResponse,
    TextVersion,
    TextsCategoryResponse,
    CreateTextRequest,
    TextDetailsRequest,
    UpdateTextRequest,
    TextDetailsRequest,
    Section,
    DetailTableOfContentResponse
)
from .groups.groups_service import (
    validate_group_exists
)
from pecha_api.texts.texts_cache_service import (
    set_text_details_cache,
    get_text_details_cache,
    get_text_by_text_id_or_term_cache,
    set_text_by_text_id_or_term_cache,
    get_table_of_contents_by_text_id_cache,
    set_table_of_contents_by_text_id_cache,
    get_text_versions_by_group_id_cache,
    set_text_versions_by_group_id_cache
)
from pecha_api.sheets.sheets_enum import (
    SortBy,
    SortOrder
)

from .texts_utils import TextUtils
from pecha_api.users.users_service import (
    validate_user_exists
)
from pecha_api.terms.terms_service import get_term
from .segments.segments_utils import SegmentUtils

from typing import List, Dict, Optional, Tuple, Set
from pecha_api.config import get
from pecha_api.utils import Utils
from .texts_enums import PaginationDirection


async def get_text_by_text_id_or_term(
        text_id: str,
        term_id: str,
        language: str,
        skip: int,
        limit: int
) -> TextsCategoryResponse | TextDTO:
    if language is None:
        language = get("DEFAULT_LANGUAGE")

    cached_data: TextsCategoryResponse | TextDTO = get_text_by_text_id_or_term_cache(
        text_id = text_id,
        term_id = term_id,
        language = language,
        skip = skip,
        limit = limit
    )

    if cached_data is not None:
        return cached_data

    if term_id is not None:
        term = await get_term(term_id=term_id, language=language)
        texts = await _get_texts_by_term_id(term_id=term_id, language=language, skip=skip, limit=limit)
        response = TextsCategoryResponse(
            term=term,
            texts=texts,
            total=len(texts),
            skip=skip,
            limit=limit
        )
    else:
        response =await TextUtils.get_text_detail_by_id(text_id=text_id)
    
    set_text_by_text_id_or_term_cache(
        text_id = text_id,
        term_id = term_id,
        language = language,
        skip = skip,
        limit = limit,
        data = response
    )

    return response


async def get_sheet(published_by: Optional[str] = None, is_published: Optional[bool] = None, sort_by: Optional[SortBy] = None, sort_order: Optional[SortOrder] = None, skip: int = 0, limit: int = 10):
    
    sheets = await fetch_sheets_from_db(
        published_by=published_by,
        is_published=is_published,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )
    return sheets

async def get_table_of_contents_by_text_id(text_id: str, language: str, skip: int = 0, limit: int = 10) -> TableOfContentResponse:
    
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    
    cached_data: TableOfContentResponse = get_table_of_contents_by_text_id_cache(
        text_id = text_id,
        language = language,
        skip = skip,
        limit = limit
    )
    if False and cached_data is not None:
        return cached_data
    
    is_valid_text: bool = await TextUtils.validate_text_exists(text_id=text_id)
    if not is_valid_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    
    text_detail: TextDTO = await TextUtils.get_text_detail_by_id(text_id=text_id)
    group_id: str = text_detail.group_id
    texts: List[TextDTO] = await get_texts_by_group_id(group_id=group_id, skip=skip, limit=limit)
    filtered_text_on_root_and_version = TextUtils.filter_text_on_root_and_version(texts=texts, language=language)
    root_text: TextDTO = filtered_text_on_root_and_version["root_text"]
    if root_text is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    table_of_contents: List[TableOfContent] = await get_contents_by_id(text_id=root_text.id)
    response = TableOfContentResponse(
        text_detail=root_text,
        contents=[
            TableOfContent(
                id=str(content.id),
                text_id=content.text_id,
                sections=content.sections
            )
            for content in table_of_contents
        ]
    )

    set_table_of_contents_by_text_id_cache(
        text_id = text_id,
        language = language,
        skip = skip,
        limit = limit,
        data = response
    )
    
    return response

async def remove_table_of_content_by_text_id(text_id: str):
    is_valid_text = await TextUtils.validate_text_exists(text_id=text_id)
    if not is_valid_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    return await delete_table_of_content_by_text_id(text_id=text_id)


# NEW TEXT DETAILS SERVICE
async def get_text_details_by_text_id(
        text_id: str,
        text_details_request: TextDetailsRequest
) -> DetailTableOfContentResponse:
    
    await _validate_text_detail_request(
        text_id=text_id,
        text_details_request=text_details_request
    )
    selected_text = await TextUtils.get_text_detail_by_id(text_id=text_id)
    
    table_of_content: TableOfContent = await _receive_table_of_content(
        text_id=text_id,
        text_details_request=text_details_request
    )

    segments_with_position: List[Tuple[str, int]] = _get_segments_with_position_(
        table_of_content=table_of_content,
    )
    total_segments = len(segments_with_position)
    trimmed_segment_dict = _get_trimmed_segment_dict_(
        segments_with_position=segments_with_position,
        segment_id=text_details_request.segment_id,
        direction=text_details_request.direction,
        size=text_details_request.size
    )
    current_segment_position = trimmed_segment_dict.get(text_details_request.segment_id)
    paginated_table_of_content: TableOfContent = _generate_paginated_table_of_content_by_segments_(
        table_of_content = table_of_content,
        segment_dict = trimmed_segment_dict
    )

    detail_table_of_content: DetailTableOfContentResponse = await _mapping_table_of_content(
        text=selected_text,
        table_of_content=paginated_table_of_content,
        version_id=text_details_request.version_id,
        size=text_details_request.size,
        total_segments=total_segments,
        current_segment_position=current_segment_position,
        pagination_direction=text_details_request.direction
    )

    return detail_table_of_content


async def get_text_versions_by_group_id(text_id: str, language: str, skip: int, limit: int) -> TextVersionResponse:
    '''
    This function will first retrive the group_id from the text_id details
    It will retrieve all the texts with same group_id
    Then root text will be determined by the language provied
    Left texts will be considered as versions
    '''
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    
    cached_data: TextVersionResponse = get_text_versions_by_group_id_cache(
        text_id = text_id,
        language = language,
        skip = skip,
        limit = limit
    )
    if cached_data is not None:
        return cached_data
    
    root_text = await TextUtils.get_text_detail_by_id(text_id=text_id)
    group_id = root_text.group_id
    texts = await get_texts_by_group_id(group_id=group_id, skip=skip, limit=limit)
    filtered_text_on_root_and_version = TextUtils.filter_text_on_root_and_version(texts=texts, language=language)
    root_text = filtered_text_on_root_and_version["root_text"]
    versions = filtered_text_on_root_and_version["versions"]

    versions_table_of_content_id_dict: Dict[str, List[str]] = await _get_table_of_content_by_version_text_id(versions=versions)

    list_of_version = _get_list_of_text_version_response_model(versions=versions, versions_table_of_content_id_dict=versions_table_of_content_id_dict)

    response = TextVersionResponse(
        text=root_text,
        versions=list_of_version
    )

    set_text_versions_by_group_id_cache(
        text_id = text_id,
        language = language,
        skip = skip,
        limit = limit,
        data = response
    )

    return response


async def create_new_text(
        create_text_request: CreateTextRequest,
        token: str
) -> TextDTO:
    is_valid_user = validate_user_exists(token=token)
    if is_valid_user:
        valid_group = await validate_group_exists(group_id=create_text_request.group_id)
        if not valid_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.GROUP_NOT_FOUND_MESSAGE)
        new_text = await create_text(create_text_request=create_text_request)
        return TextDTO(
            id=str(new_text.id),
            title=new_text.title,
            language=new_text.language,
            group_id=new_text.group_id,
            type=new_text.type,
            is_published=new_text.is_published,
            created_date=new_text.created_date,
            updated_date=new_text.updated_date,
            published_date=new_text.published_date,
            published_by=new_text.published_by,
            categories=new_text.categories,
            views=new_text.views
        )
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)


async def create_table_of_content(table_of_content_request: TableOfContent, token: str) -> TableOfContent:
    is_valid_user = validate_user_exists(token=token)
    if is_valid_user:
        await TextUtils.validate_text_exists(text_id=table_of_content_request.text_id)
        segment_ids = TextUtils.get_all_segment_ids(table_of_content=table_of_content_request)
        await SegmentUtils.validate_segments_exists(segment_ids=segment_ids)
        table_of_content = await create_table_of_content_detail(table_of_content_request=table_of_content_request)
        return table_of_content
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)


# PRIVATE FUNCTIONS

async def _mapping_table_of_content(
        text: TextDTO, 
        table_of_content: TableOfContent,
        version_id: str,
        size: int,
        total_segments: int,
        current_segment_position: int,
        pagination_direction: PaginationDirection,
) -> DetailTableOfContentResponse:
    detail_table_of_content = await SegmentUtils.get_mapped_segment_content_for_table_of_content(
        table_of_content=table_of_content,
        version_id=version_id
    )
    detail_table_of_content = DetailTableOfContentResponse(
        text_detail=text,
        content=detail_table_of_content,
        size=size,
        pagination_direction=pagination_direction,
        current_segment_position=current_segment_position,
        total_segments=total_segments
    )
    return detail_table_of_content


async def _validate_text_detail_request(text_id: str, text_details_request: TextDetailsRequest) -> bool:
    # Check if text_id is provided
    if text_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorConstants.TEXT_OR_TERM_NOT_FOUND_MESSAGE
        )

    # Check if valid version_id is provided
    if text_details_request.version_id is not None:
        await TextUtils.validate_text_exists(
            text_id=text_details_request.version_id
        )

    # Check if valid segment_id is provided
    if text_details_request.segment_id is not None:
        await SegmentUtils.validate_segment_exists(
            segment_id=text_details_request.segment_id
        )

    await TextUtils.validate_text_exists(text_id=text_id)


async def _get_texts_by_term_id(term_id: str, language: str, skip: int, limit: int) -> List[TextDTO]:
    texts = await get_texts_by_term(term_id=term_id, language=language, skip=skip, limit=limit)
    filter_text_base_on_group_id_type = await TextUtils.filter_text_base_on_group_id_type(texts=texts,
                                                                                          language=language)
    root_text = filter_text_base_on_group_id_type["root_text"]
    commentary = filter_text_base_on_group_id_type["commentary"]
    text_list = [
        TextDTO(
            id=str(text.id),
            title=text.title,
            language=text.language,
            group_id=text.group_id,
            type="commentary",
            is_published=text.is_published,
            created_date=text.created_date,
            updated_date=text.updated_date,
            published_date=text.published_date,
            published_by=text.published_by,
            categories=text.categories
        )
        for text in commentary
    ]
    if root_text is not None:
        text_list.append(
            TextDTO(
                id=str(root_text.id),
                title=root_text.title,
                language=root_text.language,
                group_id=root_text.group_id,
                type="root_text",
                is_published=root_text.is_published,
                created_date=root_text.created_date,
                updated_date=root_text.updated_date,
                published_date=root_text.published_date,
                published_by=root_text.published_by,
                categories=root_text.categories
            )
        )
    return text_list

async def _get_table_of_content_by_version_text_id(versions: List[TextDTO]) -> Dict[str, List[str]]:
    versions_table_of_content_id_dict = {}
    for version in versions:
        list_of_table_of_contents = await get_contents_by_id(text_id=str(version.id))
        list_of_table_of_contents_ids = []
        for table_of_content in list_of_table_of_contents:
            list_of_table_of_contents_ids.append(str(table_of_content.id))
        versions_table_of_content_id_dict[str(version.id)] = list_of_table_of_contents_ids
    return versions_table_of_content_id_dict

def _get_list_of_text_version_response_model(versions: List[TextDTO], versions_table_of_content_id_dict: Dict[str, List[str]]) -> List[TextVersion]:
    list_of_version = [
        TextVersion(
            id=str(version.id),
            title=version.title,
            language=version.language,
            type=version.type,
            group_id=version.group_id,
            table_of_contents=versions_table_of_content_id_dict.get(str(version.id), []),
            is_published=version.is_published,
            created_date=version.created_date,
            updated_date=version.updated_date,
            published_date=version.published_date,
            published_by=version.published_by
        )
        for version in versions
    ]
    return list_of_version

async def update_text_details(text_id: str, update_text_request: UpdateTextRequest):
    is_valid_text = await TextUtils.validate_text_exists(text_id=text_id)
    if not is_valid_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    text_details = await TextUtils.get_text_detail_by_id(text_id=text_id)
    text_details.updated_date = Utils.get_utc_date_time()
    text_details.title = update_text_request.title
    text_details.is_published = update_text_request.is_published
    return await update_text_details_by_id(text_id=text_id, update_text_request=update_text_request)

async def delete_text_by_text_id(text_id: str):
    is_valid_text = await TextUtils.validate_text_exists(text_id=text_id)
    if not is_valid_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    await delete_text_by_id(text_id=text_id)


def _filter_single_section_(section: Section, wanted_segment_ids: Set[str]) -> Section | None:
    kept_segments = []
    for segment in section.segments:
        if segment.segment_id in wanted_segment_ids:
            kept_segments.append(segment)
    
    kept_subsections = []
    if section.sections:
        for subsection in section.sections:
            filtered_subsection = _filter_single_section_(subsection, wanted_segment_ids)
            if filtered_subsection is not None:
                kept_subsections.append(filtered_subsection)
    
    has_wanted_segments = len(kept_segments) > 0
    has_valid_subsections = len(kept_subsections) > 0
    
    if has_wanted_segments or has_valid_subsections:
        new_section = Section(
            id=section.id,
            title=section.title,
            section_number=section.section_number,
            parent_id=section.parent_id,
            segments=kept_segments,
            sections=kept_subsections if kept_subsections else None,
            created_date=section.created_date,
            updated_date=section.updated_date,
            published_date=section.published_date
        )
        return new_section
    else:
        return None

def _generate_paginated_table_of_content_by_segments_(
    table_of_content: TableOfContent,
    segment_dict: Dict[str, int]
) -> TableOfContent:

    wanted_segment_ids = set(segment_dict.keys())
    
    filtered_sections = []
    for section in table_of_content.sections:
        filtered_section = _filter_single_section_(section=section, wanted_segment_ids=wanted_segment_ids)
        if filtered_section is not None:
            filtered_sections.append(filtered_section)
    
    paginated_table_of_content = TableOfContent(
        id=str(table_of_content.id),
        text_id=table_of_content.text_id,
        sections=filtered_sections
    )
    
    return paginated_table_of_content


def _get_trimmed_segment_dict_(segments_with_position:List[Tuple[str,int]], segment_id: str, direction: PaginationDirection, size: int) -> Dict[str, int]:
    

    dict_segment_id_with_position: Dict[str, int] = dict(segments_with_position)

    segment_position = dict_segment_id_with_position.get(segment_id) - 1

    total_segments = len(segments_with_position)

    if direction == PaginationDirection.NEXT:
        trimmed_segments_with_position = segments_with_position[segment_position : min(segment_position + size, total_segments)]

    else:
        trimmed_segments_with_position = segments_with_position[max(0, segment_position - size) : segment_position + 1]
    
    trimmed_segments_with_position = dict(trimmed_segments_with_position)

    return trimmed_segments_with_position

def _get_segments_with_position_(table_of_content: TableOfContent) -> List[Tuple[str, int]]:
    segments_with_position: List[Tuple[str, int]] = []
    position = 1
    
    def get_segment_from_section(section: Section):
        nonlocal position
        
        for segment in section.segments:
            segments_with_position.append((segment.segment_id, position))
            position += 1
        
        if section.sections:
            for sub_section in section.sections: 
                get_segment_from_section(sub_section)
    
    for section in table_of_content.sections:
        get_segment_from_section(section)
    return segments_with_position


async def _receive_table_of_content(text_id: str, text_details_request: TextDetailsRequest) -> TableOfContent:
    table_of_content = None
    if text_details_request.content_id is not None:
        table_of_content:TableOfContent = await get_table_of_content_by_content_id(
            content_id=text_details_request.content_id
        )
    else:
        table_of_contents: List[TableOfContent] = await get_contents_by_id(text_id=text_id)
        table_of_content: TableOfContent = _search_table_of_content_where_segment_id_exists(table_of_contents=table_of_contents, segment_id=text_details_request.segment_id)
    if table_of_content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorConstants.TABLE_OF_CONTENT_NOT_FOUND_MESSAGE
        )
    return table_of_content

def _search_section_(sections: List[Section], segment_id: str) -> bool:
    for section in sections:
        for segment in section.segments:
            if segment.segment_id == segment_id:
                return True
        
        if section.sections:
            result = _search_section_(sections=section.sections, segment_id=segment_id)
            if result:  
                return result
    
    return False

def _search_table_of_content_where_segment_id_exists(table_of_contents: List[TableOfContent], segment_id: str) -> TableOfContent:
    for table_of_content in table_of_contents:
        result = _search_section_(sections=table_of_content.sections, segment_id=segment_id)
        if result:
            return table_of_content
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorConstants.TABLE_OF_CONTENT_NOT_FOUND_MESSAGE
    )
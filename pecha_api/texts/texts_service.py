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
    DetailTextMapping,
    UpdateTextRequest,
    Section
)
from .groups.groups_service import (
    validate_group_exists
)
from pecha_api.cache.cache_service import (
    set_text_details_cache,
    get_text_details_cache
)

from pecha_api.sheets.sheets_response_models import (
    SheetDTO,
    SheetDTOResponse,
    Publisher
)
from pecha_api.sheets.sheets_enum import (
    SortBy,
    SortOrder
)

from .texts_utils import TextUtils
from pecha_api.users.users_service import (
    validate_user_exists,
    fetch_user_by_email
)
from pecha_api.users.user_response_models import (
    UserInfoResponse
)
from pecha_api.texts.texts_response_models import (
    PaginationDirection
)

from pecha_api.terms.terms_service import get_term
from .segments.segments_utils import SegmentUtils

from typing import List, Dict, Optional, Tuple
from pecha_api.config import get
from pecha_api.utils import Utils


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
        texts = await _get_texts_by_term_id(term_id=term_id, language=language, skip=skip, limit=limit)
        return TextsCategoryResponse(
            term=term,
            texts=texts,
            total=len(texts),
            skip=skip,
            limit=limit
        )
    else:
        return await TextUtils.get_text_detail_by_id(text_id=text_id)

async def get_sheets(published_by: Optional[str] = None, is_published: Optional[bool] = None, sort_by: Optional[SortBy] = None, sort_order: Optional[SortOrder] = None, skip: int = 0, limit: int = 10) -> SheetDTOResponse:
    
    sheets = await fetch_sheets_from_db(
        published_by=published_by,
        is_published=is_published,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )
    
    sheets = [
        SheetDTO(
            id=str(sheet.id),
            title=sheet.title,
            summary="",
            published_date=sheet.published_date,
            time_passed=Utils.time_passed(published_time=sheet.published_date, language=sheet.language),
            views=str(sheet.views),
            likes=[],
            publisher=_create_publisher_object_(published_by=sheet.published_by),
            language=sheet.language
        )
        for sheet in sheets
    ]
    return SheetDTOResponse(
        sheets= sheets,
        skip=skip,
        limit=limit,
        total=len(sheets)
    )

async def get_table_of_contents_by_text_id(text_id: str) -> TableOfContentResponse:
    is_valid_text: bool = await TextUtils.validate_text_exists(text_id=text_id)
    if not is_valid_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    text = await TextUtils.get_text_detail_by_id(text_id=text_id)
    table_of_contents = await get_contents_by_id(text_id=text_id)
    return TableOfContentResponse(
        text_detail=text,
        contents=[
            TableOfContent(
                id=str(content.id),
                text_id=content.text_id,
                sections=content.sections
            )
            for content in table_of_contents
        ]
    )

async def remove_table_of_content_by_text_id(text_id: str):
    is_valid_text = await TextUtils.validate_text_exists(text_id=text_id)
    if not is_valid_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
    return await delete_table_of_content_by_text_id(text_id=text_id)

async def get_text_details_by_text_id(
        text_id: str,
        text_details_request: TextDetailsRequest
) -> DetailTableOfContentResponse:
    
    await _validate_text_detail_request(text_id=text_id, text_details_request=text_details_request)

    selected_text = await TextUtils.get_text_detail_by_id(text_id=text_id)
    
    table_of_content = await _receive_table_of_content(
        text_id=text_id,
        text_details_request=text_details_request
    )
    
    segments: List[Tuple[str, int]] = _fetch_all_segment_ids_from_table_of_content_with_position_(table_of_content = table_of_content)

    position_of_segment_id_requested = _get_position_of_segment_id_requested_(segments = segments, segment_id = text_details_request.segment_id)

    trimed_segment: List[Tuple[str, int]] = _trim_segment_base_on_pagination_(
        segments = segments, 
        position_of_segment_id_requested = position_of_segment_id_requested, 
        size = text_details_request.size, 
        direction = text_details_request.direction
    )

    paginated_table_of_content = _paginate_table_of_content_(table_of_content = table_of_content, segments = trimed_segment)

    detail_table_of_content = await _mapping_table_of_content_segments_(
        text=selected_text,
        table_of_content=paginated_table_of_content,
        text_details_request=text_details_request,
        size=text_details_request.size
    )
    return detail_table_of_content

def _trim_segment_base_on_pagination_(segments: List[Tuple[str, int]], position_of_segment_id_requested: int, size: int, direction: PaginationDirection) -> List[Tuple[str, int]]:
    if direction == PaginationDirection.NEXT:
        starting_index = position_of_segment_id_requested - 1
        ending_index = min(starting_index + size - 1, len(segments))
        return segments[starting_index:ending_index]
    elif direction == PaginationDirection.PREVIOUS:
        starting_index = max(0,position_of_segment_id_requested - 1 - size)
        ending_index = position_of_segment_id_requested
        return segments[starting_index:ending_index]
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.INVALID_PAGINATION_DIRECTION_MESSAGE)

def _get_position_of_segment_id_requested_(segments: List[Tuple[str, int]], segment_id: str) -> int:
    for segment in segments:
        if segment[0] == segment_id:
            return segment[1]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.SEGMENT_NOT_FOUND_MESSAGE)

def _fetch_all_segment_ids_from_table_of_content_with_position_(table_of_content: TableOfContent) -> List[Tuple[str, int]]:
    
    segments_with_positions = []
    position = 0
    
    def traverse_section(section: Section):
        nonlocal position
        
        for segment in section.segments:
            segments_with_positions.append((segment.segment_id, position))
            position += 1
        
        if section.sections:
            for subsection in section.sections:
                traverse_section(subsection)
    
    for section in table_of_content.sections:
        traverse_section(section)

    return segments_with_positions


async def get_text_versions_by_group_id(text_id: str, language: str, skip: int, limit: int) -> TextVersionResponse:
    '''
    This function will first retrive the group_id from the text_id details
    It will retrieve all the texts with same group_id
    Then root text will be determined by the language provied
    Left texts will be considered as versions
    '''
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    root_text = await TextUtils.get_text_detail_by_id(text_id=text_id)
    group_id = root_text.group_id
    texts = await get_texts_by_group_id(group_id=group_id, skip=skip, limit=limit)
    filtered_text_on_root_and_version = TextUtils.filter_text_on_root_and_version(texts=texts, language=language)
    root_text = filtered_text_on_root_and_version["root_text"]
    versions = filtered_text_on_root_and_version["versions"]

    versions_table_of_content_id_dict: Dict[str, List[str]] = await _get_table_of_content_by_version_text_id(versions=versions)

    list_of_version = _get_list_of_text_version_response_model(versions=versions, versions_table_of_content_id_dict=versions_table_of_content_id_dict)

    return TextVersionResponse(
        text=root_text,
        versions=list_of_version
    )


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

async def _mapping_table_of_content_segments_(text: TextDTO, table_of_content: TableOfContent,
                                    text_details_request: TextDetailsRequest, size: int):
    total_segment: int = _get_segment_count_in_table_of_content_(table_of_content = table_of_content)
    detail_table_of_content = await SegmentUtils.get_mapped_segment_content_for_table_of_content(
        table_of_content=table_of_content,
        version_id=text_details_request.version_id
    )
    detail_table_of_content = DetailTableOfContentResponse(
        text_detail=text,
        mapping=DetailTextMapping(
            segment_id=text_details_request.segment_id,
            section_id=text_details_request.section_id
        ),
        content=detail_table_of_content,
        size=size,
        current_segment_number = -1,
        total=total_segment
    )
    return detail_table_of_content

def _paginate_table_of_content_(table_of_content: TableOfContent, segments: List[Tuple[str, int]]) -> TableOfContent:

    filtered_sections = _filter_sections_recursively_(sections = table_of_content.sections, allowed_segments = segments)

    paginated_table_of_content = TableOfContent(
        id=table_of_content.id,
        text_id=table_of_content.text_id,
        sections=filtered_sections
    )

    return paginated_table_of_content

def _filter_sections_recursively_(sections: List[Section], allowed_segments: List[Tuple[str, int]]) -> List[Section]:

    filtered_sections = []
    
    for section in sections:
        filtered_section = _filter_segments_in_section_(section, allowed_segments)
        
        if section.sections:
            filtered_subsections = _filter_sections_recursively_(section.sections, allowed_segments)
            filtered_section.sections = filtered_subsections if filtered_subsections else None
        
        if filtered_section.segments or (filtered_section.sections and len(filtered_section.sections) > 0):
            filtered_sections.append(filtered_section)
    
    return filtered_sections

def _filter_segments_in_section_(section: Section, allowed_segments: List[Tuple[str, int]]) -> Section:
    allowed_ids = {seg_id for seg_id, _ in allowed_segments}
    
    filtered_segments = [seg for seg in section.segments if seg.segment_id in allowed_ids]
    
    filtered_section = Section(
        id=section.id,
        title=section.title,
        section_number=section.section_number,
        parent_id=section.parent_id,
        segments=filtered_segments,
        sections=section.sections,
        created_date=section.created_date,
        updated_date=section.updated_date,
        published_date=section.published_date
    )
    
    return filtered_section
def _get_segment_count_in_table_of_content_(table_of_content: TableOfContent) -> int:
    
    total_segment = 0
    
    def traverse_section(section: Section):
        nonlocal total_segment
        
        total_segment += len(section.segments)

        if section.sections:
            for subsection in section.sections:
                traverse_section(subsection)
    

    for section in table_of_content.sections:
        traverse_section(section)
    
    return total_segment

async def _receive_table_of_content(text_id: str, text_details_request: TextDetailsRequest):
    table_of_content = None
    if text_details_request.content_id is not None:
        table_of_content = await get_table_of_content_by_content_id(
            content_id=text_details_request.content_id,
            skip=text_details_request.skip,
            limit=text_details_request.limit
        )
    elif text_details_request.segment_id is not None:
        table_of_content = await TextUtils.get_table_of_content_id_and_respective_section_by_segment_id(
            text_id=text_id,
            segment_id=text_details_request.segment_id
        )
        text_details_request.skip = max(0, table_of_content.sections[0].section_number - 1)
        text_details_request.limit = 1
    if table_of_content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorConstants.TABLE_OF_CONTENT_NOT_FOUND_MESSAGE
        )
    return table_of_content


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


def _create_publisher_object_(published_by: str) -> Publisher:

    user_profile: UserInfoResponse = fetch_user_by_email(email=published_by)
    
    return Publisher(
        name=f"{user_profile.firstname} {user_profile.lastname}".strip() or user_profile.username,
        username=user_profile.username,
        email=user_profile.email,
        avatar_url=user_profile.avatar_url
    )
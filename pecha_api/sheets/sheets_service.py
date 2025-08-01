import os
import uuid
from typing import Optional, Dict, List
import hashlib
from fastapi import UploadFile, HTTPException, status


from pecha_api.texts.texts_models import Text
from pecha_api.error_contants import ErrorConstants
from pecha_api.config import get
from .sheets_response_models import CreateSheetRequest, SheetImageResponse, Publisher
from ..uploads.S3_utils import upload_bytes, generate_presigned_upload_url
from pecha_api.image_utils import ImageUtils
from pecha_api.utils import Utils
from pecha_api.texts.texts_utils import TextUtils

from pecha_api.users.users_models import Users

from .sheets_enum import (
    SortBy, 
    SortOrder
)

from pecha_api.users.users_service import (
    validate_user_exists,
    get_user_info
)
from pecha_api.users.user_response_models import UserInfoResponse

from pecha_api.texts.groups.groups_response_models import (
    CreateGroupRequest,
    GroupDTO
)
from pecha_api.texts.groups.groups_enums import GroupType
from pecha_api.texts.groups.groups_service import (
    create_new_group,
    delete_group_by_group_id
)

from pecha_api.texts.texts_response_models import (
    CreateTextRequest,
    UpdateTextRequest
)
from pecha_api.texts.texts_service import (
    create_new_text,
    create_table_of_content,
    remove_table_of_content_by_text_id,
    update_text_details,
    delete_text_by_text_id,
    get_sheet,
    get_table_of_content_by_sheet_id
)

from pecha_api.users.users_service import (
    validate_and_extract_user_details,
    fetch_user_by_email
)
from pecha_api.texts.texts_enums import TextType
from pecha_api.texts.texts_response_models import (
    TextDTO,
    TableOfContent,
    Section,
    TextSegment
)

from pecha_api.texts.segments.segments_models import SegmentType
from pecha_api.texts.segments.segments_response_models import (
    CreateSegment,
    CreateSegmentRequest,
    SegmentResponse,
    SegmentDTO
)
from pecha_api.texts.segments.segments_service import (
    create_new_segment,
    remove_segments_by_text_id,
    get_segments_details_by_ids
)

from pecha_api.sheets.sheets_response_models import (
    SheetIdResponse,
    SheetDetailDTO,
    Publisher,
    SheetSection,
    SheetSegment,
    SheetDTOResponse,
    SheetDTO
)
from pecha_api.texts.texts_cache_service import (
    delete_text_details_by_id_cache,
    delete_table_of_content_by_sheet_id_cache
)
from pecha_api.texts.segments.segments_cache_service import (
    delete_segments_details_by_ids_cache
)

from pecha_api.cache.cache_enums import CacheType

DEFAULT_SHEET_SECTION_NUMBER = 1

async def fetch_sheets(
    token: Optional[str] = None,
    language: Optional[str] = None,
    email: Optional[str] = None,
    sort_by: Optional[SortBy] = None,
    sort_order: Optional[SortOrder] = None,
    skip: int = 0,
    limit: int = 10
) -> SheetDTOResponse:

    if email is None:
        # Case 1: Community page - show all published sheets filtered by language
        sheets = await get_sheet(
            is_published=True,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
    else:
        sheets = await _fetch_user_sheets_(
            token = token,
            email = email,
            sort_by = sort_by,
            sort_order = sort_order,
            skip = skip,
            limit = limit
        )
    

    sheets: SheetDTOResponse = _generate_sheet_dto_response_(sheets = sheets, skip = skip, limit = limit)
      
    return sheets


async def get_sheet_by_id(sheet_id: str, skip: int, limit: int) -> SheetDetailDTO:
    sheet_details: TextDTO = await TextUtils.get_text_details_by_id(text_id=sheet_id)
    user_details: UserInfoResponse = fetch_user_by_email(email=sheet_details.published_by)
    sheet_table_of_content: Optional[TableOfContent] = await get_table_of_content_by_sheet_id(
        sheet_id=sheet_id
    )
    if sheet_table_of_content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TABLE_OF_CONTENT_NOT_FOUND_MESSAGE)

    sections = sheet_table_of_content.sections if sheet_table_of_content else []
    sheet_dto: SheetDetailDTO = await _generate_sheet_detail_dto_(
        sheet_details=sheet_details,
        user_details=user_details,
        sheet_sections=sections,
        skip=skip,
        limit=limit
    )
    return sheet_dto

async def _generate_sheet_detail_dto_(
    sheet_details: TextDTO,
    user_details: UserInfoResponse,
    sheet_sections: List[Section],
    views: int,
    skip: int,
    limit: int
) -> SheetDetailDTO:
    publisher = Publisher(
        name=f"{user_details.firstname} {user_details.lastname}",
        username=user_details.username,
        email=user_details.email,
        avatar_url=user_details.avatar_url
    )
    segment_ids = _get_all_segment_ids_in_table_of_content_(sheet_sections=sheet_sections)
    segments_dict: Dict[str, SegmentDTO] = await get_segments_details_by_ids(segment_ids=segment_ids)

    sheet_section: Optional[SheetSection] = None
    if sheet_sections:
        sheet_section = await _generate_sheet_section_(
            segments=sheet_sections[0].segments,
            segments_dict=segments_dict
        )
    return SheetDetailDTO(
        id=sheet_details.id,
        sheet_title=sheet_details.title,
        created_date=sheet_details.created_date,
        publisher=publisher,
        content=sheet_section,
        is_published=sheet_details.is_published,
        views=views,
        skip=skip,
        limit=limit,
        total=len(sheet_sections),
    )


async def create_new_sheet(create_sheet_request: CreateSheetRequest, token: str) -> SheetIdResponse:
    group_id =  await _create_sheet_group_(token=token)
    text_id = await _create_sheet_text_(
        title=create_sheet_request.title, 
        token=token, 
        group_id=group_id
    )
    sheet_segments: Dict[str, str] = await _process_and_upload_sheet_segments(
        create_sheet_request=create_sheet_request,
        text_id=text_id,
        token=token
    )
    await _generate_and_upload_sheet_table_of_content(
        create_sheet_request=create_sheet_request,
        text_id=text_id,
        segment_dict=sheet_segments,
        token=token
    )
    return SheetIdResponse(sheet_id=text_id)

async def update_sheet_by_id(
        sheet_id: str, 
        update_sheet_request: CreateSheetRequest, 
        token: str
    ) -> SheetIdResponse:

    is_valid_user = validate_user_exists(token=token)
    if not is_valid_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)

    await delete_text_details_by_id_cache(text_id=sheet_id, cache_type=CacheType.TEXT_DETAIL)
    sheet_table_of_content: Optional[TableOfContent] = await get_table_of_content_by_sheet_id(sheet_id=sheet_id)
    if sheet_table_of_content is not None:
        await delete_table_of_content_by_sheet_id_cache(sheet_id=sheet_id, cache_type=CacheType.TEXT_TABLE_OF_CONTENTS)
    
    sections = sheet_table_of_content.sections if sheet_table_of_content else []
    segment_ids = _get_all_segment_ids_in_table_of_content_(sheet_sections=sections)
    await delete_segments_details_by_ids_cache(segment_ids=segment_ids)
    

    await remove_segments_by_text_id(text_id=sheet_id)

    await remove_table_of_content_by_text_id(text_id=sheet_id)

    await _update_text_details_(sheet_id=sheet_id, update_sheet_request=update_sheet_request)

    sheet_segments: Dict[str, str] = await _process_and_upload_sheet_segments(
        create_sheet_request=update_sheet_request,
        text_id=sheet_id,
        token=token
    )
    await _generate_and_upload_sheet_table_of_content(
        create_sheet_request=update_sheet_request,
        text_id=sheet_id,
        segment_dict=sheet_segments,
        token=token
    )
    # delete_sheet_by_id_cache(
    #     sheet_id=sheet_id
    # )
    return SheetIdResponse(sheet_id=sheet_id)

async def delete_sheet_by_id(sheet_id: str, token: str):
    is_valid_user = validate_user_exists(token=token)
    if not is_valid_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
    
    
    sheet_details: TextDTO = await TextUtils.get_text_details_by_id(text_id=sheet_id)

    user_details: UserInfoResponse = await get_user_info(token=token)

    if user_details.email != sheet_details.published_by:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorConstants.FORBIDDEN_ERROR_MESSAGE
        )

    await delete_group_by_group_id(group_id=sheet_details.group_id)
    await remove_segments_by_text_id(text_id=sheet_id)
    await remove_table_of_content_by_text_id(text_id=sheet_id)
    await delete_text_by_text_id(text_id=sheet_id)

    # delete_sheet_by_id_cache(
    #     sheet_id=sheet_id
    # )

def upload_sheet_image_request(sheet_id: Optional[str], file: UploadFile) -> SheetImageResponse:
    # Validate and compress the uploaded image
    image_utils = ImageUtils()
    compressed_image = image_utils.validate_and_compress_image(file=file, content_type=file.content_type)
    file_name, ext = os.path.splitext(file.filename)
    unique_id = str(uuid.uuid4())
    
    # If no id is provided, use a random UUID as the folder name
    path = "images/sheet_images"
    image_path_full = f"{path}/{sheet_id}/{unique_id}" if sheet_id is not None else f"{path}/{unique_id}"
    sheet_image_name = f"{image_path_full}/{file_name}{ext}"
    upload_key = upload_bytes(
        bucket_name=get("AWS_BUCKET_NAME"),
        s3_key=sheet_image_name,
        file=compressed_image,
        content_type=file.content_type
    )
    presigned_url = generate_presigned_upload_url(
        bucket_name=get("AWS_BUCKET_NAME"),
        s3_key=upload_key
    )
    
    return SheetImageResponse(url=presigned_url, key=upload_key)


async def _generate_sheet_detail_dto_(
    sheet_details: TextDTO,
    user_details: UserInfoResponse,
    sheet_sections: List[Section],
    skip: int,
    limit: int
) -> SheetDetailDTO:
    publisher = Publisher(
        name=f"{user_details.firstname} {user_details.lastname}",
        username=user_details.username,
        email=user_details.email,
        avatar_url=user_details.avatar_url
    )
    segment_ids = _get_all_segment_ids_in_table_of_content_(sheet_sections=sheet_sections)
    segments_dict: Dict[str, SegmentDTO] = await get_segments_details_by_ids(segment_ids=segment_ids)

    sheet_section: Optional[SheetSection] = None
    if sheet_sections:
        sheet_section = await _generate_sheet_section_(
            segments=sheet_sections[0].segments,
            segments_dict=segments_dict
        )

    return SheetDetailDTO(
        id=sheet_details.id,
        sheet_title=sheet_details.title,
        created_date=sheet_details.created_date,
        is_published=sheet_details.is_published,
        publisher=publisher,
        content=sheet_section,
        skip=skip,
        limit=limit,
        total=len(sheet_sections),
    )

async def _fetch_user_sheets_(token: str, email: str, sort_by: SortBy, sort_order: SortOrder, skip: int, limit: int):
    if token == "None":
            _is_sheet_published_ = True
    else:
        current_user: Users = validate_and_extract_user_details(token=token)
        _is_sheet_published_ = None if current_user.email == email else True
    sheets = await get_sheet(
        published_by=email,
        is_published=_is_sheet_published_,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )
    return sheets

def _generate_sheet_dto_response_(sheets, skip: int, limit: int) -> SheetDTOResponse:
    sheets_dto = [
        SheetDTO(
            id = str(sheet.id),
            title = sheet.title,
            summary = "summary",
            published_date = sheet.published_date,
            time_passed = Utils.time_passed(published_time=sheet.published_date, language=sheet.language),
            views = sheet.views,
            likes = sheet.likes or [],
            publisher = _create_publisher_object_(published_by=sheet.published_by),
            language = sheet.language
        )
        for sheet in sheets
    ]
    return SheetDTOResponse(
        sheets = sheets_dto,
        skip = skip,
        limit = limit,
        total = len(sheets)
    )

def _create_publisher_object_(published_by: str) -> Publisher:

    user_profile: UserInfoResponse = fetch_user_by_email(email=published_by)
    
    return Publisher(
        name=f"{user_profile.firstname} {user_profile.lastname}".strip() or user_profile.username,
        username=user_profile.username,
        email=user_profile.email,
        avatar_url=user_profile.avatar_url
    )

async def _generate_sheet_section_(segments: List[TextSegment], segments_dict: Dict[str, SegmentDTO]) -> SheetSection:
    sheet_segments = []
    for segment in segments:
        segment_details: SegmentDTO = segments_dict[segment.segment_id]
        if segment_details.type == SegmentType.SOURCE:
            segment_text_details: TextDTO = await TextUtils.get_text_details_by_id(text_id=segment_details.text_id)
            sheet_segments.append(
                SheetSegment(
                    segment_id=segment.segment_id,
                    segment_number=segment.segment_number,
                    content=segment_details.content,
                    language=segment_text_details.language,
                    text_title=segment_text_details.title,
                    type=segment_details.type
                )
            )
        else:
            s3_key = None
            if segment_details.type == SegmentType.IMAGE:
                s3_key = segment_details.content
                segment_details.content = generate_presigned_upload_url(
                    bucket_name=get("AWS_BUCKET_NAME"),
                    s3_key=segment_details.content
                )
            sheet_segments.append(
                SheetSegment(
                    segment_id=segment.segment_id,
                    segment_number=segment.segment_number,
                    content=segment_details.content,
                    type=segment_details.type,
                    key=s3_key
                )
            )

    return SheetSection(
        section_number=DEFAULT_SHEET_SECTION_NUMBER,
        segments=sheet_segments
    )


def _get_all_segment_ids_in_table_of_content_(sheet_sections: Section) -> List[str]:
    segment_ids = []
    for section in sheet_sections:
        for segment in section.segments:
            segment_ids.append(segment.segment_id)
    return segment_ids

async def _update_text_details_(sheet_id: str, update_sheet_request: CreateSheetRequest):
    update_text_request = UpdateTextRequest(
        title=update_sheet_request.title,
        is_published=update_sheet_request.is_published
    )
    await update_text_details(text_id=sheet_id, update_text_request=update_text_request)


async def _generate_and_upload_sheet_table_of_content(
        create_sheet_request: CreateSheetRequest,
        text_id: str,
        segment_dict: Dict[str, str],
        token: str
):
    sheet_table_of_content = _generate_sheet_table_of_content_(
        create_sheet_request=create_sheet_request, 
        text_id=text_id,
        segment_dict=segment_dict
    )
    await create_table_of_content(
        table_of_content_request=sheet_table_of_content,
        token=token
    )
    return sheet_table_of_content

async def _process_and_upload_sheet_segments(
        create_sheet_request: CreateSheetRequest,
        text_id: str,
        token: str
) -> Dict[str, str]:
    create_segment_request_payload: CreateSegmentRequest = _generate_segment_creation_request_payload_(
        create_sheet_request=create_sheet_request,
        text_id=text_id
    )
    new_segments: SegmentResponse = await create_new_segment(
        create_segment_request=create_segment_request_payload,
        token=token
    )
    segment_dict: Dict[str, str] = _generate_segment_dictionary_(new_segments=new_segments)
    return segment_dict

def _generate_sheet_table_of_content_(create_sheet_request: CreateSheetRequest, text_id: str, segment_dict: Dict[str, str]) -> TableOfContent:
    section = Section(
        id=str(uuid.uuid4()),
        section_number=1,
        segments=[],
        created_date=Utils.get_utc_date_time(),
        updated_date=Utils.get_utc_date_time()
    )
    for source in create_sheet_request.source:
        if source.type == SegmentType.SOURCE:
            segment = TextSegment(
                segment_number = source.position,
                segment_id = source.content
            )
        else:
            content_hash_value = hashlib.sha256(source.content.encode()).hexdigest()
            segment = TextSegment(
                segment_number = source.position,
                segment_id = segment_dict[content_hash_value]
            )
        section.segments.append(segment)

    table_of_content = TableOfContent(
        text_id=text_id,
        sections=[section]
    )
    
    return table_of_content


def _generate_segment_dictionary_(new_segments: SegmentResponse) -> Dict[str, str]:
    segment_dict = {}
    for segment in new_segments.segments:
        if segment.type != SegmentType.SOURCE:
            content_hash_value = hashlib.sha256(segment.content.encode()).hexdigest()
            segment_dict[content_hash_value] = segment.id
    return segment_dict

def _generate_segment_creation_request_payload_(create_sheet_request: CreateSheetRequest, text_id: str) -> CreateSegmentRequest:
    create_segment_request = CreateSegmentRequest(
        text_id=text_id,
        segments=[]
    )
    for source in create_sheet_request.source:
        if source.type == SegmentType.SOURCE:
            continue
        create_segment_request.segments.append(
            CreateSegment(
                content=source.content,
                type=source.type
            )
        )
    return create_segment_request

async def _create_sheet_text_(title: str, token: str, group_id: str) -> str:
    user_details = validate_and_extract_user_details(token=token)
    create_text_request = CreateTextRequest(
        title=title,
        group_id=group_id,
        language=None,
        published_by=user_details.email,
        type=TextType.SHEET
    )
    new_text: TextDTO = await create_new_text(create_text_request=create_text_request, token=token)
    return new_text.id


async def _create_sheet_group_(token: str) -> str:
    create_group_request = CreateGroupRequest(
        type=GroupType.SHEET
    )
    new_group: GroupDTO = await create_new_group(create_group_request=create_group_request, token=token)

    return new_group.id




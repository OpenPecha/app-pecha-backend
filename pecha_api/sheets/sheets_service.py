import os
import uuid
from typing import Optional, Dict, List
import hashlib
from fastapi import UploadFile, HTTPException, status


from pecha_api.error_contants import ErrorConstants
from pecha_api.config import get
from .sheets_response_models import CreateSheetRequest, SheetImageResponse
from ..uploads.S3_utils import upload_bytes, generate_presigned_upload_url
from pecha_api.image_utils import ImageUtils
from pecha_api.utils import Utils
from pecha_api.texts.texts_utils import TextUtils


from pecha_api.users.users_service import validate_user_exists

from pecha_api.texts.groups.groups_response_models import (
    CreateGroupRequest,
    GroupDTO
)
from pecha_api.texts.groups.groups_enums import GroupType
from pecha_api.texts.groups.groups_service import create_new_group

from pecha_api.texts.texts_response_models import (
    CreateTextRequest,
    UpdateTextRequest
)
from pecha_api.texts.texts_service import (
    create_new_text,
    create_table_of_content,
    remove_table_of_content_by_text_id,
    update_text_details
)

from pecha_api.users.users_service import (
    validate_and_extract_user_details
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
    SegmentResponse
)
from pecha_api.texts.segments.segments_service import (
    create_new_segment,
    remove_segments_by_text_id
)

from pecha_api.sheets.sheets_response_models import SheetIdResponse

    
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
    return SheetIdResponse(sheet_id=sheet_id)

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
    
    return SheetImageResponse(url=presigned_url)

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
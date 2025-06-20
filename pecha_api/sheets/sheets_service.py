import os
import uuid
from typing import Optional, Dict
import hashlib

from fastapi import APIRouter, Depends, UploadFile, File

from pecha_api.config import get
from .sheets_repository import get_sheets_by_topic, get_users_sheets, create_sheet
from .sheets_response_models import SheetModel, Publisher, SheetsResponse, CreateSheetRequest, SheetImageResponse, SheetIdRequest, CreateSheetResponse
from ..users.users_repository import get_user_by_username
from ..db.database import SessionLocal
from ..uploads.S3_utils import upload_bytes, generate_presigned_upload_url
from ..topics.topics_repository import get_topic_by_id

from pecha_api.utils import Utils
from pecha_api.image_utils import ImageUtils

from pecha_api.texts.groups.groups_response_models import (
    CreateGroupRequest,
    GroupDTO
)
from pecha_api.texts.groups.groups_enums import GroupType
from pecha_api.texts.groups.groups_service import create_new_group

from pecha_api.texts.texts_response_models import (
    CreateTextRequest
)
from pecha_api.texts.texts_service import create_new_text

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
from pecha_api.texts.segments.segments_service import create_new_segment

async def get_sheets(topic_id: str,language: str) -> SheetsResponse:
    sheets = get_sheets_by_topic(topic_id=topic_id)
    publisher = Publisher(
        id=str(uuid.uuid4()),
        name='Person Name',
        profile_url="",
        image_url=""
    )
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    sheets_list = [
        SheetModel(
            id=str(sheet.id),
            title=sheet.titles.get(language, ""),
            summary=sheet.summaries.get(language, ""),
            publisher=publisher
        )
        for sheet in sheets
    ]
    sheet_response = SheetsResponse(sheets=sheets_list)
    return sheet_response

# new service for get_sheet_by_id
async def get_sheets_by_userID(user_id: str, language: str, skip: int, limit: int) -> SheetsResponse:
    if language is None:
        language = get("DEFAULT_LANGUAGE")
    publisher = None
    with SessionLocal() as db_session:
        publisher = get_user_by_username(db=db_session, username=user_id)
        publisher = Publisher(
            id=str(publisher.id),
            name=publisher.firstname + " " + publisher.lastname,
            profile_url="",
            image_url=""
        )
    sheets = await get_users_sheets(user_id=user_id, language=language, skip=skip, limit=limit)
    sheets_list = []
    for sheet in sheets:
        topic_list = []
        for topic_id in sheet.topic_id:
            topic = await get_topic_by_id(topic_id)
            topic_list.append(topic.titles)
        sheets_list.append(
            SheetModel(
                id=str(sheet.id),
                title=sheet.titles,
                summary=sheet.summaries,
                publisher=publisher,
                published_date=sheet.published_date,
                time_passed=sheet.published_date,
                views=sheet.views,
                likes=sheet.likes,
                topics=topic_list,
                language=language
            )
        )
    sheet_response = SheetsResponse(sheets=sheets_list)
    return sheet_response
    
async def create_new_sheet(create_sheet_request: CreateSheetRequest, token: str) -> CreateSheetResponse:
    group_id =  await _create_group_(token=token)
    text_id = await _create_text_(
        title=create_sheet_request.title, 
        token=token, 
        group_id=group_id
    )
    sheet_segments: Dict[str, str] = await _process_and_upload_sheet_segments(
        create_sheet_request=create_sheet_request,
        text_id=text_id,
        token=token
    )


async def _process_and_upload_sheet_segments(
        create_sheet_request: CreateSheetRequest,
        text_id: str,
        token: str
) -> Dict[str, str]:
    create_segment_request_payload = _generate_segment_creation_request_payload_(
        create_sheet_request=create_sheet_request,
        text_id=text_id
    )
    new_segments: SegmentResponse = await create_new_segment(
        create_segment_request=create_segment_request_payload,
        token=token
    )
    segment_dict = _generate_segment_dictionary_(new_segments=new_segments)
    table_of_content = _generate_table_of_content_(create_sheet_request=create_sheet_request, text_id=text_id)

def _generate_table_of_content_(create_sheet_request: CreateSheetRequest, text_id: str):
    table_of_content

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
            create_segment_request.segments.append(
                CreateSegment(
                    content=source.content,
                    type=source.type,
                    mapping=[]
                )
            )
    return create_segment_request

async def _create_text_(title: str, token: str, group_id: str) -> str:
    user_details = validate_and_extract_user_details(token=token)
    create_text_request = CreateTextRequest(
        title=title,
        language=get("DEFAULT_LANGUAGE"),
        group_id=group_id,
        published_by=user_details.username,
        type=TextType.SHEET
    )
    new_text: TextDTO = await create_new_text(create_text_request=create_text_request, token=token)
    return new_text.id


async def _create_group_(token: str) -> str:
    create_group_request = CreateGroupRequest(
        type=GroupType.SHEET
    )
    new_group: GroupDTO = await create_new_group(create_group_request=create_group_request, token=token)
    return new_group.id


def upload_sheet_image_request(sheet_id: Optional[str], file: UploadFile) -> SheetImageResponse:
    # Validate and compress the uploaded image
    image_utils = ImageUtils()
    compressed_image = image_utils.validate_and_compress_image(file=file, content_type=file.content_type)
    file_name, ext = os.path.splitext(file.filename)
    unique_id = str(uuid.uuid4())
    
    # If no id is provided, use a random UUID as the folder name
    path = f"images/sheet_images"
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

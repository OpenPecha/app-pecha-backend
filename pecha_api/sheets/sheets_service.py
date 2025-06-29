import os
import uuid
from typing import Optional

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
    
async def create_new_sheet(create_sheet_request: CreateSheetRequest) -> CreateSheetResponse:
    new_sheet = await create_sheet(create_sheet_request=create_sheet_request)
    return new_sheet
    

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

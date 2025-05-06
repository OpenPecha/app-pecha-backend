import uuid

from pecha_api.config import get
from .sheets_repository import get_sheets_by_topic, get_users_sheets, create_sheet
from .sheets_response_models import SheetModel, Publisher, SheetsResponse, CreateSheetRequest
from ..users.users_repository import get_user_by_username
from ..db.database import SessionLocal
from ..topics.topics_repository import get_topic_by_id

async def get_sheets(topic_id: str,language: str):
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
async def get_sheets_by_userID(user_id: str, language: str, skip: int, limit: int):
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
    
async def create_new_sheet(create_sheet_request: CreateSheetRequest):
    new_sheet = await create_sheet(create_sheet_request=create_sheet_request)
    return new_sheet
    
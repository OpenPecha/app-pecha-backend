import uuid

from pecha_api.config import get
from .sheets_repository import get_sheets_by_topic, get_users_sheets
from .sheets_response_models import SheetModel, Publisher, SheetsResponse


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
    publisher = Publisher(
        id=str(uuid.uuid4()),
        name='Tenzin',
        profile_url="",
        image_url=""
    )
    sheets = await get_users_sheets(user_id=user_id, language=language, skip=skip, limit=limit)
    sheets_list = [
        SheetModel(
            id=str(sheet.id),
            title=sheet.titles.get(language, ""),
            summary=sheet.summaries.get(language, ""),
            date=sheet.date,
            views=sheet.views,
            topics=sheet.topics,
            published_time=sheet.published_time,
            publisher=publisher,
            language=language
        )
        for sheet in sheets
    ]
    sheet_response = SheetsResponse(sheets=sheets_list)
    return sheet_response

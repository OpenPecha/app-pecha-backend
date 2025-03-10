import uuid
import logging

from .sheets_models import Sheet
from .sheets_response_models import CreateSheetRequest, Publisher
from beanie.exceptions import CollectionWasNotInitialized
from ..constants import get_current_date, get_current_time_in_millisecond

def get_sheets_by_topic(topic_id : str):
    return [
        Sheet(
            titles={"en": f"Topic {i}", "bo": f"གྲྭ་ཚན {i}"},
            summaries={"en": f"Summaries {i}", "bo": f"སྙིང་བསྡུས་ {i}"},
            publisher_id=str(uuid.uuid4())
        )
        for i in range(1, 6)
    ]

async def get_users_sheets(user_id: str, language: str, skip: int, limit: int):
    try:
        sheets = await Sheet.get_sheets_by_user_id(user_id=user_id, skip=skip, limit=limit)
        return sheets
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return []

async def create_sheet(create_sheet_request: CreateSheetRequest):
    new_sheet = Sheet(
        titles=create_sheet_request.titles,
        summaries=create_sheet_request.summaries,
        source=create_sheet_request.source,
        topic_id=create_sheet_request.topic_id,
        publisher_id=create_sheet_request.publisher_id,
        creation_date=get_current_date(),
        modified_date=get_current_date(),
        published_date=get_current_time_in_millisecond(),
        views=0,
        likes=[],
        collection=[],
        sheetLanguage=create_sheet_request.sheetLanguage
    )
    saved_sheet = await new_sheet.insert()
    return saved_sheet
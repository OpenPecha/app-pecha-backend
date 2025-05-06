import uuid
import logging
from datetime import datetime, timezone

from .sheets_models import Sheet
from .sheets_response_models import CreateSheetRequest
from beanie.exceptions import CollectionWasNotInitialized

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
        creation_date=str(datetime.now(timezone.utc)),
        modified_date=str(datetime.now(timezone.utc)),
        published_date=int(datetime.now(timezone.utc).timestamp()),
        views=0,
        likes=[],
        collection=[],
        sheetLanguage=create_sheet_request.sheetLanguage
    )
    saved_sheet = await new_sheet.insert()
    return saved_sheet
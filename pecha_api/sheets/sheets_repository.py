import uuid

from .sheets_models import Sheet
from .sheets_response_models import CreateSheetRequest, Publisher

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
    return [
        Sheet(
            titles={"en": f"Topic {i}", "bo": f"གྲྭ་ཚན {i}"},
            summaries={"en": f"Summaries {i}", "bo": f"སྙིང་བསྡུས་ {i}"},
            published_date="2021-01-01",
            views=str(i),
            topics=[
                {
                    "en": f"en {i}",
                    "bo": f"bo {i}"
                },
                {
                    "en": f"en {i+1}",
                    "bo": f"bo {i+1}"
                }
            ],
            published_time=1741096363711,
            publisher_id=str(uuid.uuid4())
        )
        for i in range(1, 6)
    ]

async def create_sheet(create_sheet_request: CreateSheetRequest):
    new_sheet = Sheet(
        titles=create_sheet_request.titles,
        summaries=create_sheet_request.summaries,
        source=create_sheet_request.source,
        topic_id=create_sheet_request.topic_id,
        publisher_id=create_sheet_request.publisher_id,
        creation_date=get_current_date(),
        modified_date=get_current_date(),
        published_date=get_current_date(),
        published_time=get_current_time_in_millisecond(),
        views="0",
        likes=[],
        collection=[],
    )
    saved_sheet = await new_sheet.insert()
    return saved_sheet
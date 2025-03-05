import uuid

from .sheets_models import Sheet

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
            date="2021-01-01",
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
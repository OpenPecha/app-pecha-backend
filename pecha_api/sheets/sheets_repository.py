import uuid

from sheets.sheets_models import Sheet


def get_sheets_by_topic(topic_id : str):
    return [
        Sheet(
            titles={"en": f"Topic {i}", "bo": f"གྲྭ་ཚན {i}"},
            summaries={"en": f"Summaries {i}", "bo": f"སྙིང་བསྡུས་ {i}"},
            publisher_id=str(uuid.uuid4())
        )
        for i in range(1, 6)
    ]
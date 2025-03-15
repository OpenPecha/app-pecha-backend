import uuid

from .texts_models import Text
from .texts_response_models import Category

def get_texts_by_id():
    root_text = Text(
        id=uuid.uuid4(),
        titles={"en": "Root Text title", "bo": "Root གྲྭ་ཚན"},
        summaries={"en": "Root Summaries", "bo": "Root སྙིང་བསྡུས་"},
        default_language="bo"
    )
    versions = [
        Text(
            id=uuid.uuid4(),
            titles={"en": f"Version Topic {i}", "bo": f"Version གྲྭ་ཚན {i}"},
            summaries={"en": f"Version Summaries {i}", "bo": f"Version སྙིང་བསྡུས་ {i}"},
            default_language="bo"
        )
        for i in range(1, 6)
    ]
    return root_text, versions

async def get_texts_by_category(category: str, language: str, skip: int, limit: int):
    return [
        {
            "id": "uuid.v4",
            "title": "The Way of the Bodhisattva",
            "language": "en",
            "type": "root_text",
            "is_published": True,
            "created_date": "2021-09-01T00:00:00.000Z",
            "updated_date": "2021-09-01T00:00:00.000Z",
            "published_date": "2021-09-01T00:00:00.000Z",
            "published_by": "buddhist_tab"
        },
        {
            "id": "uuid.v4",
            "title": "Commentary on the difficult points of The Way of Bodhisattvas",
            "language": "en",
            "type": "commentary",
            "is_published": True,
            "created_date": "2021-09-01T00:00:00.000Z",
            "updated_date": "2021-09-01T00:00:00.000Z",
            "published_date": "2021-09-01T00:00:00.000Z",
            "published_by": "buddhist_tab"
        },
        {
            "id": "uuid.v4",
            "title": "Khenpo Kunpel's commentary on the Bodhicaryavatara",
            "language": "en",
            "type": "commentary",
            "is_published": True,
            "created_date": "2021-09-01T00:00:00.000Z",
            "updated_date": "2021-09-01T00:00:00.000Z",
            "published_date": "2021-09-01T00:00:00.000Z",
            "published_by": "buddhist_tab"
        }
    ]
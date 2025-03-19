import uuid
import logging
from beanie.exceptions import CollectionWasNotInitialized

from .texts_response_models import Section, SegmentResponse, RootText, CreateTextRequest
from .texts_models import Text

import datetime


async def get_texts_by_id(text_id: str):
    try:
        text = await Text.get_text(text_id=text_id)
        return text
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return []

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

async def get_versions_by_id(text_id: str, skip: int, limit: int):
    return [
        {
            "id": "uuid.v4",
            "title": "शबोधिचर्यावतार[sa]",
            "parent_id": "d19338e",
            "priority": 1,
            "language": "sa",
            "type": "translation",
            "is_published": True,
            "created_date": "2021-09-01T00:00:00.000Z",
            "updated_date": "2021-09-01T00:00:00.000Z",
            "published_date": "2021-09-01T00:00:00.000Z",
            "published_by": "buddhist_tab"
        },
        {
            "id": "uuid.v4",
            "title": "བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།",
            "language": "bo",
            "parent_id": "d19338e",
            "priority": 2,
            "type": "translation",
            "is_published": True,
            "created_date": "2021-09-01T00:00:00.000Z",
            "updated_date": "2021-09-01T00:00:00.000Z",
            "published_date": "2021-09-01T00:00:00.000Z",
            "published_by": "buddhist_tab"
        },
        {
            "id": "uuid.v4",
            "title": "The Way of the Bodhisattva Monlam AI Draft",
            "language": "en",
            "parent_id": "d19338e",
            "priority": 3,
            "type": "translation",
            "is_published": True,
            "created_date": "2021-09-01T00:00:00.000Z",
            "updated_date": "2021-09-01T00:00:00.000Z",
            "published_date": "2021-09-01T00:00:00.000Z",
            "published_by": "buddhist_tab"
        }
    ]


async def get_contents_by_id(text_id: str, skip: int, limit: int):
    return [
        Section(
            id="d19338e4-da52-4ea2-800e-3414eac8167e",
            title="A brief presentation of the ground path and result",
            section_number=1,
            parent_id=None,
            sections=[
                Section(
                    id="39965c2a-e89e-4834-83bb-e3a294a8f705",
                    title="",
                    section_number=1,
                    parent_id="d19338e4-da52-4ea2-800e-3414eac8167e",
                    created_date="2021-09-01T00:00:00.000Z",
                    updated_date="2021-09-01T00:00:00.000Z",
                    published_date="2021-09-01T00:00:00.000Z",
                    sections=[]
                )
            ],
            created_date="2021-09-01T00:00:00.000Z",
            updated_date="2021-09-01T00:00:00.000Z",
            published_date="2021-09-01T00:00:00.000Z"
        ),
        Section(
            id="b48dad38-da6d-45c3-ad12-97bca590769c",
            title="The detailed explanation of the divisions of reality",
            section_number=2,
            parent_id=None,
            sections=[
                Section(
                    id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                    title="Basis",
                    section_number=1,
                    parent_id="b48dad38-da6d-45c3-ad12-97bca590769c",
                    created_date="2021-09-01T00:00:00.000Z",
                    updated_date="2021-09-01T00:00:00.000Z",
                    published_date="2021-09-01T00:00:00.000Z",
                    sections=[
                        Section(
                            id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                            title="The extensive explanation of the abiding nature of the ground",
                            section_number=1,
                            parent_id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                            created_date="2021-09-01T00:00:00.000Z",
                            updated_date="2021-09-01T00:00:00.000Z",
                            published_date="2021-09-01T00:00:00.000Z",
                            sections=[]
                        )
                    ]
                )
            ],
            created_date="2021-09-01T00:00:00.000Z",
            updated_date="2021-09-01T00:00:00.000Z",
            published_date="2021-09-01T00:00:00.000Z"
        )
    ]

async def get_text_by_id(text_id: str):
    return RootText(
        id= "d19338e",
        title= "Bodhicaryavatara",
        language= "en",
        type= "root_text",
        has_child= False
    )

async def create_text(create_text_request: CreateTextRequest) -> Text:
    new_text = Text(
        title=create_text_request.title,
        language=create_text_request.language,
        parent_id=create_text_request.parent_id,
        is_published=True,
        created_date=str(datetime.datetime.utcnow()),
        updated_date=str(datetime.datetime.utcnow()),
        published_date=str(datetime.datetime.utcnow()),
        published_by=create_text_request.published_by,
        type=create_text_request.type,
        categories=create_text_request.categories
    )
    saved_text = await new_text.insert()
    return saved_text


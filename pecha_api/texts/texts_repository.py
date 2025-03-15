import uuid

from .texts_response_models import Section, SegmentResponse, RootText, CreateTextRequest, CreateSegmentRequest
from .texts_models import Text, Segment

import datetime


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
            segments=[],
            sections=[
                Section(
                    id="39965c2a-e89e-4834-83bb-e3a294a8f705",
                    title="",
                    section_number=1,
                    parent_id="d19338e4-da52-4ea2-800e-3414eac8167e",
                    created_date="2021-09-01T00:00:00.000Z",
                    updated_date="2021-09-01T00:00:00.000Z",
                    published_date="2021-09-01T00:00:00.000Z",
                    segments=[
                        SegmentResponse(
                            segment_id="8bac2031-e8c6-4c5b-981f-ed17dbc755fb",
                            segment_number=1
                        ),
                        SegmentResponse(
                            segment_id="b3dc7cec-0e18-4238-8184-9b59bc6b114d",
                            segment_number=2
                        ),
                        SegmentResponse(
                            segment_id="606135bf-1f71-41fd-8c12-1cc037a768d5",
                            segment_number=3
                        ),
                        SegmentResponse(
                            segment_id="980ab7e0-aefc-4120-8817-ff0873ed429c",
                            segment_number=4
                        ),
                        SegmentResponse(
                            segment_id="b0e4578c-e604-44a9-a302-fe9fb5b08626",
                            segment_number=5
                        ),
                        SegmentResponse(
                            segment_id="af8d904f-26b7-4725-9d00-ede7939a6baf",
                            segment_number=6
                        ),
                        SegmentResponse(
                            segment_id="84a9d639-0a17-4525-ac4e-12527cc925c8",
                            segment_number=7
                        )
                    ],
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
            segments=[],
            sections=[
                Section(
                    id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                    title="Basis",
                    section_number=1,
                    parent_id="b48dad38-da6d-45c3-ad12-97bca590769c",
                    created_date="2021-09-01T00:00:00.000Z",
                    updated_date="2021-09-01T00:00:00.000Z",
                    published_date="2021-09-01T00:00:00.000Z",
                    segments=[],
                    sections=[
                        Section(
                            id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                            title="The extensive explanation of the abiding nature of the ground",
                            section_number=1,
                            parent_id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                            created_date="2021-09-01T00:00:00.000Z",
                            updated_date="2021-09-01T00:00:00.000Z",
                            published_date="2021-09-01T00:00:00.000Z",
                            segments=[
                                SegmentResponse(
                                    segment_id="5894c3b8-4c52-4964-b0d1-9498a71fd1e0",
                                    segment_number=1
                                ),
                                SegmentResponse(
                                    segment_id="d2fabe6c-a112-4e09-a265-5d43078467b1",
                                    segment_number=2
                                ),
                                SegmentResponse(
                                    segment_id="b66daafd-8451-4cd2-9743-ceabb62661a1",
                                    segment_number=3
                                ),
                                SegmentResponse(
                                    segment_id="ec911cd3-afd0-4052-8928-0984f8f37acd",
                                    segment_number=4
                                ),
                                SegmentResponse(
                                    segment_id="007f2197-5a37-4696-b34e-f67eca870830",
                                    segment_number=5
                                )
                            ],
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
        titles=create_text_request.titles,
        language=create_text_request.language,
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

async def create_segment(create_segment_request: CreateSegmentRequest) -> Segment:
    new_segment = Segment(
        text_id=create_segment_request.text_id,
        content=create_segment_request.content,
        mapping=create_segment_request.mapping
    )
    saved_segment = await new_segment.insert()
    return saved_segment




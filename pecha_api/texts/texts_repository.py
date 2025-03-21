import uuid
import logging
from beanie.exceptions import CollectionWasNotInitialized

from .texts_response_models import TableOfContent, Section, TableOfContentSegmentResponse, RootText, CreateTextRequest
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
        TableOfContent(
            id="abh7u8e4-da52-4ea2-800e-3414emk8uy67",
            text_id=text_id,
            segments=[
                Section(
                    id="d19338e4-da52-4ea2-800e-3414eac8167e",
                    title="A brief presentation of the ground path and result",
                    section_number=1,
                    parent_id=None,
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
                                    id="at8ujke7-8491-4cfe-9720-dac1acb967y7",
                                    title="The extensive explanation of the abiding nature of the ground",
                                    section_number=1,
                                    parent_id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                                    created_date="2021-09-01T00:00:00.000Z",
                                    updated_date="2021-09-01T00:00:00.000Z",
                                    published_date="2021-09-01T00:00:00.000Z"
                                )
                            ]
                        )
                    ],
                    created_date="2021-09-01T00:00:00.000Z",
                    updated_date="2021-09-01T00:00:00.000Z",
                    published_date="2021-09-01T00:00:00.000Z"
                )
            ]
        )
    ]
async def get_contents_by_id_with_segments(text_id: str, content_id: str, skip: int, limit: int):
    return [
        TableOfContent(
            id="abh7u8e4-da52-4ea2-800e-3414emk8uy67",
            text_id=text_id,
            segments=[
                Section(
                    id="d19338e4-da52-4ea2-800e-3414eac8167e",
                    title="A brief presentation of the ground path and result",
                    section_number=1,
                    parent_id=None,
                    segments=[
                        TableOfContentSegmentResponse(
                            segment_id="n876yt56-51de-4a42-9d49-580b729dnb66",
                            segment_number=1,
                            content="༄༅༅།།རྒྱ་གར་སྐད་དུ། བོ་<sup class=\"footnote-marker\">*</sup><i class=\"footnote\">བོ་] Q བོད་</i>དྷི་སཏྭ་ཙརྱ་<sup class=\"footnote-marker\">*</sup><i class=\"footnote\">སཏྭ་ཙརྱ་] I སཏྭ་ཙཪྻ་ N སཏྭ་ཙརྱྭ་ Q སཏྭ་ཙམླཻ་; The reading སཏྭ་ཙརྱ་ is supported by both GDR and TS commentaries which gloss ཙརྱ་ as སྤྱོད་པ་</i>ཨ་བ་ཏཱ་<sup class=\"footnote-marker\">*</sup><i class=\"footnote\">ཏཱ་] C ཏ་; The long vowel ཏཱ་ is confirmed by KP and TS who consistently use the form ཨ་བ་ཏ་ར་ in their commentaries</i>ར།",
                        ),
                        TableOfContentSegmentResponse(
                            segment_id="98i7y654-0d28-41e9-bff1-83ef53bfbad1",
                            segment_number=2,
                            content="བོད་སྐད་དུ། བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།"
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
                    segments=[
                        TableOfContentSegmentResponse(
                            segment_id="abeb0072-51de-4a42-9d49-580b729dd6aa",
                            segment_number=1,
                            content="༄༅༅།།རྒྱ་གར་སྐད་དུ། བོ་<sup class=\"footnote-marker\">*</sup><i class=\"footnote\">བོ་] Q བོད་</i>དྷི་སཏྭ་ཙརྱ་<sup class=\"footnote-marker\">*</sup><i class=\"footnote\">སཏྭ་ཙརྱ་] I སཏྭ་ཙཪྻ་ N སཏྭ་ཙརྱྭ་ Q སཏྭ་ཙམླཻ་; The reading སཏྭ་ཙརྱ་ is supported by both GDR and TS commentaries which gloss ཙརྱ་ as སྤྱོད་པ་</i>ཨ་བ་ཏཱ་<sup class=\"footnote-marker\">*</sup><i class=\"footnote\">ཏཱ་] C ཏ་; The long vowel ཏཱ་ is confirmed by KP and TS who consistently use the form ཨ་བ་ཏ་ར་ in their commentaries</i>ར།",
                        ),
                        TableOfContentSegmentResponse(
                            segment_id="aa45121f5-0d28-41e9-bff1-83ef53bf99d1",
                            segment_number=2,
                            content="བོད་སྐད་དུ། བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།"
                        )
                    ],
                    sections=[
                        Section(
                            id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                            title="Basis",
                            section_number=1,
                            parent_id="b48dad38-da6d-45c3-ad12-97bca590769c",
                            segments=[
                                TableOfContentSegmentResponse(
                                    segment_id="52eb0072-51de-4a42-9d49-580b729d7658",
                                    segment_number=1,
                                    content="༄༅༅།།རྒྱ་གར་སྐད་དུ། བོ་<sup class=\"footnote-marker\">*</sup><i class=\"footnote\">བོ་] Q བོད་</i>དྷི་སཏྭ་ཙརྱ་<sup class=\"footnote-marker\">*</sup><i class=\"footnote\">སཏྭ་ཙརྱ་] I སཏྭ་ཙཪྻ་ N སཏྭ་ཙརྱྭ་ Q སཏྭ་ཙམླཻ་; The reading སཏྭ་ཙརྱ་ is supported by both GDR and TS commentaries which gloss ཙརྱ་ as སྤྱོད་པ་</i>ཨ་བ་ཏཱ་<sup class=\"footnote-marker\">*</sup><i class=\"footnote\">ཏཱ་] C ཏ་; The long vowel ཏཱ་ is confirmed by KP and TS who consistently use the form ཨ་བ་ཏ་ར་ in their commentaries</i>ར།",
                                ),
                                TableOfContentSegmentResponse(
                                    segment_id="202121f5-0d28-41e9-bff1-83ef53bfbad1",
                                    segment_number=2,
                                    content="བོད་སྐད་དུ། བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།"
                                )
                            ],
                            created_date="2021-09-01T00:00:00.000Z",
                            updated_date="2021-09-01T00:00:00.000Z",
                            published_date="2021-09-01T00:00:00.000Z",
                            sections=[
                                Section(
                                    id="abv6578i-8491-4cfe-9720-dac1acb9824d",
                                    title="The extensive explanation of the abiding nature of the ground",
                                    section_number=1,
                                    parent_id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                                    segments=[
                                        TableOfContentSegmentResponse(
                                            segment_id="52eb0072-51de-4a42-9d49-580b729dcvgt",
                                            segment_number=1,
                                            content="༄༅༅།།རྒྱ་གར་སྐད་དུ། བོ་<sup class=\"footnote-marker\">*</sup><i class=\"footnote\">བོ་] Q བོད་</i>དྷི་སཏྭ་ཙརྱ་<sup class=\"footnote-marker\">*</sup><i class=\"footnote\">སཏྭ་ཙརྱ་] I སཏྭ་ཙཪྻ་ N སཏྭ་ཙརྱྭ་ Q སཏྭ་ཙམླཻ་; The reading སཏྭ་ཙརྱ་ is supported by both GDR and TS commentaries which gloss ཙརྱ་ as སྤྱོད་པ་</i>ཨ་བ་ཏཱ་<sup class=\"footnote-marker\">*</sup><i class=\"footnote\">ཏཱ་] C ཏ་; The long vowel ཏཱ་ is confirmed by KP and TS who consistently use the form ཨ་བ་ཏ་ར་ in their commentaries</i>ར།",
                                        ),
                                        TableOfContentSegmentResponse(
                                            segment_id="202121f5-0d28-41e9-bff1-83ef53bfabcd",
                                            segment_number=2,
                                            content="བོད་སྐད་དུ། བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པ།"
                                        )
                                    ],
                                    created_date="2021-09-01T00:00:00.000Z",
                                    updated_date="2021-09-01T00:00:00.000Z",
                                    published_date="2021-09-01T00:00:00.000Z"
                                )
                            ]
                        )
                    ],
                    created_date="2021-09-01T00:00:00.000Z",
                    updated_date="2021-09-01T00:00:00.000Z",
                    published_date="2021-09-01T00:00:00.000Z"
                )
            ]
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


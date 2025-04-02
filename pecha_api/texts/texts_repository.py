from __future__ import annotations

import logging
import uuid
from typing import List
from uuid import UUID

from beanie.exceptions import CollectionWasNotInitialized
from pecha_api.constants import Constants
from .texts_response_models import TableOfContent, Section, CreateTextRequest, TextDetailsRequest, Translation, TextSegment
from .texts_models import Text
from datetime import datetime, timezone

from .segments.segments_models import Segment



async def get_texts_by_id(text_id: str) -> Text | None:
    try:
        text = await Text.get_text(text_id=text_id)
        return text
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return None


async def check_text_exists(text_id: UUID) -> bool:
    try:
        is_text_exits = await Text.check_exists(text_id=text_id)
        return is_text_exits
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return False

async def check_all_text_exists(text_ids: List[UUID]) -> bool:
    try:
        is_text_exits = await Text.exists_all(text_ids=text_ids,batch_size=Constants.QUERY_BATCH_SIZE)
        return is_text_exits
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return False

async def get_texts_by_term(term_id: str, skip: int, limit: int):
    return await Text.get_texts_by_term_id(term_id=term_id, skip=skip, limit=limit)

async def get_versions_by_id(text_id: str, skip: int, limit: int):
    return await Text.get_versions_by_text_id(text_id=text_id, skip=skip, limit=limit)

async def get_segment_details_by_id(segment_id: str):
    return await Segment.get_segment_details(segment_id=segment_id)

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


async def get_text_details(text_id: str, text_details_request: TextDetailsRequest):
    if text_details_request.version_id is not None:
        return [
        TableOfContent(
            id="abh7u8e4-da52-4ea2-800e-3414emk8uy67",
            text_id=text_id,
            segments=[
                Section(
                    id="d19338e4-da52-4ea2-800e-3414eac8167e",
                    title="ཟང་ཐལ་གྱི་རྒྱུད་ཆེན་ལས་བྱུང་བའི་ཀུན་བཟང་སྨོན་ལམ་གྱི་རྣམ་བཤད། ཀུན་བཟང་ཉེ་ལམ་འོད་སྣང་གསལ་བའི་སྒྲོན་མ།",
                    section_number=1,
                    parent_id=None,
                    segments=[
                        TextSegment(
                            segment_id="2176yt56-51de-4a42-9d49-580b729dnb66",
                            segment_number=1,
                            content="<span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།",
                            translation=Translation(
                                text_id=text_details_request.version_id,
                                language="zh",
                                content="비파시불, 시기불, 비사부불, <br>  구류손불, 구나함모니불, 가섭불, <br>  그리고 석가모니불 - 고타마, 모든 신들의 신께, <br>  이 일곱 용사 같은 부처님들께 예배드립니다!"
                            )
                        )
                    ],
                    sections=None,
                    created_date="2021-09-01T00:00:00.000Z",
                    updated_date="2021-09-01T00:00:00.000Z",
                    published_date="2021-09-01T00:00:00.000Z"
                ),
                Section(
                    id="b48dad38-da6d-45c3-ad12-97bca590769c",
                    title="ཟང་ཐལ་གྱི་རྒྱུད་ཆེན་ལས་བྱུང་བའི་ཀུན་བཟང་སྨོན་ལམ་གྱི་རྣམ་བཤད། ཀུན་བཟང་ཉེ་ལམ་འོད་སྣང་གསལ་བའི་སྒྲོན་མ།",
                    section_number=2,
                    parent_id=None,
                    sections=[
                        Section(
                            id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                            title="Basis",
                            section_number=1,
                            parent_id="b48dad38-da6d-45c3-ad12-97bca590769c",
                            segments=[
                                TextSegment(
                                    segment_id="2176yt56-51de-4a42-9d49-580b729dnb66",
                                    segment_number=1,
                                    content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།",
                                    translation=Translation(
                                        text_id=text_details_request.version_id,
                                        language="zh",
                                        content="비파시불, 시기불, 비사부불, <br>  구류손불, 구나함모니불, 가섭불, <br>  그리고 석가모니불 - 고타마, 모든 신들의 신께, <br>  이 일곱 용사 같은 부처님들께 예배드립니다!"
                                    )
                                ),
                                TextSegment(
                                    segment_id="2176yt56-51de-4a42-9d49-580b729dnb66",
                                    segment_number=2,
                                    content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།",
                                    translation=Translation(
                                        text_id=text_details_request.version_id,
                                        language="zh",
                                        content="비파시불, 시기불, 비사부불, <br>  구류손불, 구나함모니불, 가섭불, <br>  그리고 석가모니불 - 고타마, 모든 신들의 신께, <br>  이 일곱 용사 같은 부처님들께 예배드립니다!"
                                    )
                                )
                            ],
                            created_date="2021-09-01T00:00:00.000Z",
                            updated_date="2021-09-01T00:00:00.000Z",
                            published_date="2021-09-01T00:00:00.000Z",
                            sections=[
                                Section(
                                    id="at8ujke7-8491-4cfe-9720-dac1acb967y7",
                                    title="ཟང་ཐལ་གྱི་རྒྱུད་ཆེན་ལས་བྱུང་བའི་ཀུན་བཟང་སྨོན་ལམ་གྱི་རྣམ་བཤད། ཀུན་བཟང་ཉེ་ལམ་འོད་སྣང་གསལ་བའི་སྒྲོན་མ།",
                                    section_number=1,
                                    parent_id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                                    segments=[
                                        TextSegment(
                                            segment_id="2176yt56-51de-4a42-9d49-580b729dnb66",
                                            segment_number=1,
                                            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།",
                                            translation=Translation(
                                                text_id=text_details_request.version_id,
                                                language="zh",
                                                content="비파시불, 시기불, 비사부불, <br>  구류손불, 구나함모니불, 가섭불, <br>  그리고 석가모니불 - 고타마, 모든 신들의 신께, <br>  이 일곱 용사 같은 부처님들께 예배드립니다!"
                                            )
                                        ),
                                        TextSegment(
                                            segment_id="2176yt56-51de-4a42-9d49-580b729dnb66",
                                            segment_number=2,
                                            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།",
                                            translation=Translation(
                                                text_id=text_details_request.version_id,
                                                language="zh",
                                                content="비파시불, 시기불, 비사부불, <br>  구류손불, 구나함모니불, 가섭불, <br>  그리고 석가모니불 - 고타마, 모든 신들의 신께, <br>  이 일곱 용사 같은 부처님들께 예배드립니다!"
                                            )
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
    return [
        TableOfContent(
            id="abh7u8e4-da52-4ea2-800e-3414emk8uy67",
            text_id=text_id,
            segments=[
                Section(
                    id="d19338e4-da52-4ea2-800e-3414eac8167e",
                    title="བྱང་གཏེར་དགོངས་པ་ཟང་ཐལ་གྱི་རྒྱུད་ཆེན་ལས་བྱུང་བའི་ཀུན་བཟང་སྨོན་ལམ་གྱི་རྣམ་བཤད། ཀུན་བཟང་ཉེ་ལམ་འོད་སྣང་གསལ་བའི་སྒྲོན་མ།",
                    section_number=1,
                    parent_id=None,
                    segments=[
                        TextSegment(
                            segment_id="2176yt56-51de-4a42-9d49-580b729dnb66",
                            segment_number=1,
                            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།",
                            translation=Translation(
                                text_id=text_details_request.version_id,
                                language="zh",
                                content="비파시불, 시기불, 비사부불, <br>  구류손불, 구나함모니불, 가섭불, <br>  그리고 석가모니불 - 고타마, 모든 신들의 신께, <br>  이 일곱 용사 같은 부처님들께 예배드립니다!"
                            )
                        )
                    ],
                    sections=None,
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
                            segments=[
                                TextSegment(
                                    segment_id="2176yt56-51de-4a42-9d49-580b729dnb66",
                                    segment_number=1,
                                    content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།",
                                    translation=Translation(
                                        text_id=text_details_request.version_id,
                                        language="zh",
                                        content="비파시불, 시기불, 비사부불, <br>  구류손불, 구나함모니불, 가섭불, <br>  그리고 석가모니불 - 고타마, 모든 신들의 신께, <br>  이 일곱 용사 같은 부처님들께 예배드립니다!"
                                    )
                                ),
                                TextSegment(
                                    segment_id="2176yt56-51de-4a42-9d49-580b729dnb66",
                                    segment_number=2,
                                    content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།",
                                    translation=Translation(
                                        text_id=text_details_request.version_id,
                                        language="zh",
                                        content="비파시불, 시기불, 비사부불, <br>  구류손불, 구나함모니불, 가섭불, <br>  그리고 석가모니불 - 고타마, 모든 신들의 신께, <br>  이 일곱 용사 같은 부처님들께 예배드립니다!"
                                    )
                                )
                            ],
                            created_date="2021-09-01T00:00:00.000Z",
                            updated_date="2021-09-01T00:00:00.000Z",
                            published_date="2021-09-01T00:00:00.000Z",
                            sections=[
                                Section(
                                    id="at8ujke7-8491-4cfe-9720-dac1acb967y7",
                                    title="The extensive explanation of the abiding nature of the ground",
                                    section_number=1,
                                    parent_id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                                    segments=[
                                        TextSegment(
                                            segment_id="2176yt56-51de-4a42-9d49-580b729dnb66",
                                            segment_number=1,
                                            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།",
                                            translation=Translation(
                                                text_id=text_details_request.version_id,
                                                language="zh",
                                                content="비파시불, 시기불, 비사부불, <br>  구류손불, 구나함모니불, 가섭불, <br>  그리고 석가모니불 - 고타마, 모든 신들의 신께, <br>  이 일곱 용사 같은 부처님들께 예배드립니다!"
                                            )
                                        ),
                                        TextSegment(
                                            segment_id="2176yt56-51de-4a42-9d49-580b729dnb66",
                                            segment_number=2,
                                            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།",
                                            translation=Translation(
                                                text_id=text_details_request.version_id,
                                                language="zh",
                                                content="비파시불, 시기불, 비사부불, <br>  구류손불, 구나함모니불, 가섭불, <br>  그리고 석가모니불 - 고타마, 모든 신들의 신께, <br>  이 일곱 용사 같은 부처님들께 예배드립니다!"
                                            )
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



async def create_text(create_text_request: CreateTextRequest) -> Text:
    new_text = Text(
        title=create_text_request.title,
        language=create_text_request.language,
        parent_id=create_text_request.parent_id,
        is_published=True,
        created_date=str(datetime.now(timezone.utc)),
        updated_date=str(datetime.now(timezone.utc)),
        published_date=str(datetime.now(timezone.utc)),
        published_by=create_text_request.published_by,
        type=create_text_request.type,
        categories=create_text_request.categories
    )
    saved_text = await new_text.insert()
    return saved_text

async def get_text_infos(text_id: str, language: str, skip: int, limit: int):
    return [
            {
                "id": str(uuid.uuid4()),
                "title": {
                    "en": "commentary",
                    "bo": "འགྲེལ་བརྗོད།"
                },
                "count": 1
            },
            {
                "id": str(uuid.uuid4()),
                "title": {
                    "en": "Happiness",
                    "bo": "སྤྲོ་སྣང་།"
                },
                "count": 3
            },
            {
                "id": str(uuid.uuid4()),
                "title": {
                    "en": "Kindness",
                    "bo": "སྙིང་རྗེ།"
                },
                "count": 5
            },
            {
                "id": str(uuid.uuid4()),
                "title": {
                    "en": "Patience",
                    "bo": "བཟོད་པ།།"
                },
                "count": 7
            }
        ]
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
                    title="བྱང་གཏེར་དགོངས་པ་ཟང་ཐལ་གྱི་རྒྱུད་ཆེན་ལས་བྱུང་བའི་ཀུན་བཟང་སྨོན་ལམ་གྱི་རྣམ་བཤད། ཀུན་བཟང་ཉེ་ལམ་འོད་སྣང་གསལ་བའི་སྒྲོན་མ།",
                    section_number=1,
                    parent_id=None,
                    segments=[
                        TableOfContentSegmentResponse(
                            segment_id="2176yt56-51de-4a42-9d49-580b729dnb66",
                            segment_number=1,
                            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།"
                        ),
                        TableOfContentSegmentResponse(
                            segment_id="koi7y654-0d28-41e9-bff1-83ef53bfbad1",
                            segment_number=2,
                            content="འདི་ལྟར་བློའི་ཡུལ་དུ་བྱ་རུང་བའི་ཆོས་རང་ངོས་ནས་བདེན་པར་མ་གྲུབ་པས་<span class=\"text-citation-style\">སྣང༵་</span>བ་ཙམ་དུ་ཟད་ཅིང་།གང་སྣང་ཐ་སྙད་ཙམ་དུ་བསླུ་བ་མེད་པར་གནས་པས་སྣང་ཙམ་དུ་<span class=\"text-citation-style\">སྲི༵ད་</span>ཅིང་ཡོད་པའི་མ་དག་ཀུན་ཉོན་འཁྲུལ་བའི་<span class=\"text-citation-style\">འཁོ༵ར་</span>བའི་སྣོད་བཅུད་རྒྱུ་འབྲས་ཀྱི་སྒྱུ་འཕྲུལ་སྣ་ཚོགས་ཀྱི་བཀོད་པ་འདི་དང་།དག་པ་རྣམ་བྱང་མྱང་<span class=\"text-citation-style\">འད༵ས་</span>ཀྱི་གྲོལ་བ་ཐར་པའི་ཡེ་ཤེས་ཡོན་ཏན་ཕྲིན་ལས་ཀྱི་རོལ་གར་བསམ་ལས་འདས་པའི་འཁྲུལ་གྲོལ་གྱི་ཆོས་འདི་<span class=\"text-citation-style\">ཐམ༵ས་</span><span class=\"text-citation-style\">ཅ༵ད་</span><span class=\"text-citation-style\">ཀུན༵</span>།"
                        ),
                        TableOfContentSegmentResponse(
                            segment_id="74ju7846-0d28-41e9-bff1-83ef53bfbju7",
                            segment_number=3,
                            content="འབྱུང་ཞིང་མཆེད་པའི་འབྱུང་གཞི།ཐིམ་ཞིང་སྡུད་པའི་སྡུད་གཞི།མཐར་ཐུག་ནི་སེམས་ཅན་རང་ཉིད་ཀྱི་སེམས་ཀྱི་གཤིས་ལུགས་ཕྲ་བ་གཉུག་མ་སེམས་ཀྱི་རྡོ་རྗེ་བྱང་ཆུབ་ཀྱི་སེམས་ངོ་བོའི་ཆ་ནས་སྟོང་ཞིང་ཀ་ནས་དག་པས།དངོས་པོ་རང་མཚན་གྱི་སྤྲོས་པའི་ཕྱོགས་ཀུན་དང་བྲལ་བ།རང་བཞིན་ཆ་ནས་གཏིང་གསལ་འགགས་པ་མེད་པའི་རང་བཞིན་ལྷུན་གྲུབ་ཀྱི་ཡོན་ཏན་འདུ་འབྲལ་སྤང་བས།"
                        ),
                        TableOfContentSegmentResponse(
                            segment_id="9876yt56-51de-4a42-9d49-580b729dnb66",
                            segment_number=1,
                            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།"
                        ),
                        TableOfContentSegmentResponse(
                            segment_id="m9i7y654-0d28-41e9-bff1-83ef53bfbad1",
                            segment_number=2,
                            content="འདི་ལྟར་བློའི་ཡུལ་དུ་བྱ་རུང་བའི་ཆོས་རང་ངོས་ནས་བདེན་པར་མ་གྲུབ་པས་<span class=\"text-citation-style\">སྣང༵་</span>བ་ཙམ་དུ་ཟད་ཅིང་།གང་སྣང་ཐ་སྙད་ཙམ་དུ་བསླུ་བ་མེད་པར་གནས་པས་སྣང་ཙམ་དུ་<span class=\"text-citation-style\">སྲི༵ད་</span>ཅིང་ཡོད་པའི་མ་དག་ཀུན་ཉོན་འཁྲུལ་བའི་<span class=\"text-citation-style\">འཁོ༵ར་</span>བའི་སྣོད་བཅུད་རྒྱུ་འབྲས་ཀྱི་སྒྱུ་འཕྲུལ་སྣ་ཚོགས་ཀྱི་བཀོད་པ་འདི་དང་།དག་པ་རྣམ་བྱང་མྱང་<span class=\"text-citation-style\">འད༵ས་</span>ཀྱི་གྲོལ་བ་ཐར་པའི་ཡེ་ཤེས་ཡོན་ཏན་ཕྲིན་ལས་ཀྱི་རོལ་གར་བསམ་ལས་འདས་པའི་འཁྲུལ་གྲོལ་གྱི་ཆོས་འདི་<span class=\"text-citation-style\">ཐམ༵ས་</span><span class=\"text-citation-style\">ཅ༵ད་</span><span class=\"text-citation-style\">ཀུན༵</span>།"
                        ),
                        TableOfContentSegmentResponse(
                            segment_id="bbju7846-0d28-41e9-bff1-83ef53bfbju7",
                            segment_number=3,
                            content="འབྱུང་ཞིང་མཆེད་པའི་འབྱུང་གཞི།ཐིམ་ཞིང་སྡུད་པའི་སྡུད་གཞི།མཐར་ཐུག་ནི་སེམས་ཅན་རང་ཉིད་ཀྱི་སེམས་ཀྱི་གཤིས་ལུགས་ཕྲ་བ་གཉུག་མ་སེམས་ཀྱི་རྡོ་རྗེ་བྱང་ཆུབ་ཀྱི་སེམས་ངོ་བོའི་ཆ་ནས་སྟོང་ཞིང་ཀ་ནས་དག་པས།དངོས་པོ་རང་མཚན་གྱི་སྤྲོས་པའི་ཕྱོགས་ཀུན་དང་བྲལ་བ།རང་བཞིན་ཆ་ནས་གཏིང་གསལ་འགགས་པ་མེད་པའི་རང་བཞིན་ལྷུན་གྲུབ་ཀྱི་ཡོན་ཏན་འདུ་འབྲལ་སྤང་བས།"
                        )
                    ],
                    created_date="2021-09-01T00:00:00.000Z",
                    updated_date="2021-09-01T00:00:00.000Z",
                    published_date="2021-09-01T00:00:00.000Z"
                ),
                Section(
                    id="b48dad38-da6d-45c3-ad12-97bca590769c",
                    title="ཐོག་མར་གཞི་ལམ་འབྲས་བུའི་རྣམ་བཞག་མདོར་བསྡུས་ཏེ་བསྟན་པ།",
                    section_number=2,
                    parent_id=None,
                    segments=[
                        TableOfContentSegmentResponse(
                            segment_id="tbeb0072-51de-4a42-9d49-580b729dd6aa",
                            segment_number=1,
                            content="འབྱུང་ཞིང་མཆེད་པའི་འབྱུང་གཞི།ཐིམ་ཞིང་སྡུད་པའི་སྡུད་གཞི།མཐར་ཐུག་ནི་སེམས་ཅན་རང་ཉིད་ཀྱི་སེམས་ཀྱི་གཤིས་ལུགས་ཕྲ་བ་གཉུག་མ་སེམས་ཀྱི་རྡོ་རྗེ་བྱང་ཆུབ་ཀྱི་སེམས་ངོ་བོའི་ཆ་ནས་སྟོང་ཞིང་ཀ་ནས་དག་པས།དངོས་པོ་རང་མཚན་གྱི་སྤྲོས་པའི་ཕྱོགས་ཀུན་དང་བྲལ་བ།རང་བཞིན་ཆ་ནས་གཏིང་གསལ་འགགས་པ་མེད་པའི་རང་བཞིན་ལྷུན་གྲུབ་ཀྱི་ཡོན་ཏན་འདུ་འབྲལ་སྤང་བས།"
                        ),
                        TableOfContentSegmentResponse(
                            segment_id="ad45121f5-0d28-41e9-bff1-83ef53bf99d1",
                            segment_number=2,
                            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།"
                        ),
                        TableOfContentSegmentResponse(
                            segment_id="kji8yt56-51de-4a42-9d49-580b729dnb66",
                            segment_number=1,
                            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།"
                        ),
                        TableOfContentSegmentResponse(
                            segment_id="9jja7y654-0d28-41e9-bff1-83ef53bfbad1",
                            segment_number=2,
                            content="འདི་ལྟར་བློའི་ཡུལ་དུ་བྱ་རུང་བའི་ཆོས་རང་ངོས་ནས་བདེན་པར་མ་གྲུབ་པས་<span class=\"text-citation-style\">སྣང༵་</span>བ་ཙམ་དུ་ཟད་ཅིང་།གང་སྣང་ཐ་སྙད་ཙམ་དུ་བསླུ་བ་མེད་པར་གནས་པས་སྣང་ཙམ་དུ་<span class=\"text-citation-style\">སྲི༵ད་</span>ཅིང་ཡོད་པའི་མ་དག་ཀུན་ཉོན་འཁྲུལ་བའི་<span class=\"text-citation-style\">འཁོ༵ར་</span>བའི་སྣོད་བཅུད་རྒྱུ་འབྲས་ཀྱི་སྒྱུ་འཕྲུལ་སྣ་ཚོགས་ཀྱི་བཀོད་པ་འདི་དང་།དག་པ་རྣམ་བྱང་མྱང་<span class=\"text-citation-style\">འད༵ས་</span>ཀྱི་གྲོལ་བ་ཐར་པའི་ཡེ་ཤེས་ཡོན་ཏན་ཕྲིན་ལས་ཀྱི་རོལ་གར་བསམ་ལས་འདས་པའི་འཁྲུལ་གྲོལ་གྱི་ཆོས་འདི་<span class=\"text-citation-style\">ཐམ༵ས་</span><span class=\"text-citation-style\">ཅ༵ད་</span><span class=\"text-citation-style\">ཀུན༵</span>།"
                        ),
                        TableOfContentSegmentResponse(
                            segment_id="ji897846-0d28-41e9-bff1-83ef53bfbju7",
                            segment_number=3,
                            content="འབྱུང་ཞིང་མཆེད་པའི་འབྱུང་གཞི།ཐིམ་ཞིང་སྡུད་པའི་སྡུད་གཞི།མཐར་ཐུག་ནི་སེམས་ཅན་རང་ཉིད་ཀྱི་སེམས་ཀྱི་གཤིས་ལུགས་ཕྲ་བ་གཉུག་མ་སེམས་ཀྱི་རྡོ་རྗེ་བྱང་ཆུབ་ཀྱི་སེམས་ངོ་བོའི་ཆ་ནས་སྟོང་ཞིང་ཀ་ནས་དག་པས།དངོས་པོ་རང་མཚན་གྱི་སྤྲོས་པའི་ཕྱོགས་ཀུན་དང་བྲལ་བ།རང་བཞིན་ཆ་ནས་གཏིང་གསལ་འགགས་པ་མེད་པའི་རང་བཞིན་ལྷུན་གྲུབ་ཀྱི་ཡོན་ཏན་འདུ་འབྲལ་སྤང་བས།"
                        )
                    ],
                    sections=[
                        Section(
                            id="0971f07a-8491-4cfe-9720-dac1acb9824d",
                            title="དེ་ཉིད་སོ་སོར་ཕྱེ་སྟེ་རྒྱས་པར་འཆད་པ།",
                            section_number=1,
                            parent_id="b48dad38-da6d-45c3-ad12-97bca590769c",
                            segments=[
                                TableOfContentSegmentResponse(
                                    segment_id="kjib0072-51de-4a42-9d49-580b729d7658",
                                    segment_number=1,
                                    content="འདི་ལྟར་བློའི་ཡུལ་དུ་བྱ་རུང་བའི་ཆོས་རང་ངོས་ནས་བདེན་པར་མ་གྲུབ་པས་<span class=\"text-citation-style\">སྣང༵་</span>བ་ཙམ་དུ་ཟད་ཅིང་།གང་སྣང་ཐ་སྙད་ཙམ་དུ་བསླུ་བ་མེད་པར་གནས་པས་སྣང་ཙམ་དུ་<span class=\"text-citation-style\">སྲི༵ད་</span>ཅིང་ཡོད་པའི་མ་དག་ཀུན་ཉོན་འཁྲུལ་བའི་<span class=\"text-citation-style\">འཁོ༵ར་</span>བའི་སྣོད་བཅུད་རྒྱུ་འབྲས་ཀྱི་སྒྱུ་འཕྲུལ་སྣ་ཚོགས་ཀྱི་བཀོད་པ་འདི་དང་།དག་པ་རྣམ་བྱང་མྱང་<span class=\"text-citation-style\">འད༵ས་</span>ཀྱི་གྲོལ་བ་ཐར་པའི་ཡེ་ཤེས་ཡོན་ཏན་ཕྲིན་ལས་ཀྱི་རོལ་གར་བསམ་ལས་འདས་པའི་འཁྲུལ་གྲོལ་གྱི་ཆོས་འདི་<span class=\"text-citation-style\">ཐམ༵ས་</span><span class=\"text-citation-style\">ཅ༵ད་</span><span class=\"text-citation-style\">ཀུན༵</span>།"
                                ),
                                TableOfContentSegmentResponse(
                                    segment_id="mk8121f5-0d28-41e9-bff1-83ef53bfbad1",
                                    segment_number=2,
                                    content="འབྱུང་ཞིང་མཆེད་པའི་འབྱུང་གཞི།ཐིམ་ཞིང་སྡུད་པའི་སྡུད་གཞི།མཐར་ཐུག་ནི་སེམས་ཅན་རང་ཉིད་ཀྱི་སེམས་ཀྱི་གཤིས་ལུགས་ཕྲ་བ་གཉུག་མ་སེམས་ཀྱི་རྡོ་རྗེ་བྱང་ཆུབ་ཀྱི་སེམས་ངོ་བོའི་ཆ་ནས་སྟོང་ཞིང་ཀ་ནས་དག་པས།དངོས་པོ་རང་མཚན་གྱི་སྤྲོས་པའི་ཕྱོགས་ཀུན་དང་བྲལ་བ།རང་བཞིན་ཆ་ནས་གཏིང་གསལ་འགགས་པ་མེད་པའི་རང་བཞིན་ལྷུན་གྲུབ་ཀྱི་ཡོན་ཏན་འདུ་འབྲལ་སྤང་བས།"
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
                                            segment_id="jheb0072-51de-4a42-9d49-580b729dcvgt",
                                            segment_number=1,
                                            content="འདི་ལྟར་བློའི་ཡུལ་དུ་བྱ་རུང་བའི་ཆོས་རང་ངོས་ནས་བདེན་པར་མ་གྲུབ་པས་<span class=\"text-citation-style\">སྣང༵་</span>བ་ཙམ་དུ་ཟད་ཅིང་།གང་སྣང་ཐ་སྙད་ཙམ་དུ་བསླུ་བ་མེད་པར་གནས་པས་སྣང་ཙམ་དུ་<span class=\"text-citation-style\">སྲི༵ད་</span>ཅིང་ཡོད་པའི་མ་དག་ཀུན་ཉོན་འཁྲུལ་བའི་<span class=\"text-citation-style\">འཁོ༵ར་</span>བའི་སྣོད་བཅུད་རྒྱུ་འབྲས་ཀྱི་སྒྱུ་འཕྲུལ་སྣ་ཚོགས་ཀྱི་བཀོད་པ་འདི་དང་།དག་པ་རྣམ་བྱང་མྱང་<span class=\"text-citation-style\">འད༵ས་</span>ཀྱི་གྲོལ་བ་ཐར་པའི་ཡེ་ཤེས་ཡོན་ཏན་ཕྲིན་ལས་ཀྱི་རོལ་གར་བསམ་ལས་འདས་པའི་འཁྲུལ་གྲོལ་གྱི་ཆོས་འདི་<span class=\"text-citation-style\">ཐམ༵ས་</span><span class=\"text-citation-style\">ཅ༵ད་</span><span class=\"text-citation-style\">ཀུན༵</span>།"
                                        ),
                                        TableOfContentSegmentResponse(
                                            segment_id="st2121f5-0d28-41e9-bff1-83ef53bfabcd",
                                            segment_number=2,
                                            content="འབྱུང་ཞིང་མཆེད་པའི་འབྱུང་གཞི།ཐིམ་ཞིང་སྡུད་པའི་སྡུད་གཞི།མཐར་ཐུག་ནི་སེམས་ཅན་རང་ཉིད་ཀྱི་སེམས་ཀྱི་གཤིས་ལུགས་ཕྲ་བ་གཉུག་མ་སེམས་ཀྱི་རྡོ་རྗེ་བྱང་ཆུབ་ཀྱི་སེམས་ངོ་བོའི་ཆ་ནས་སྟོང་ཞིང་ཀ་ནས་དག་པས།དངོས་པོ་རང་མཚན་གྱི་སྤྲོས་པའི་ཕྱོགས་ཀུན་དང་བྲལ་བ།རང་བཞིན་ཆ་ནས་གཏིང་གསལ་འགགས་པ་མེད་པའི་རང་བཞིན་ལྷུན་གྲུབ་ཀྱི་ཡོན་ཏན་འདུ་འབྲལ་སྤང་བས།"
                                        ),
                                        TableOfContentSegmentResponse(
                                            segment_id="te76yt56-51de-4a42-9d49-580b729dnb66",
                                            segment_number=1,
                                            content="<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།"
                                        ),
                                        TableOfContentSegmentResponse(
                                            segment_id="ati7y654-0d28-41e9-bff1-83ef53bfbad1",
                                            segment_number=2,
                                            content="འདི་ལྟར་བློའི་ཡུལ་དུ་བྱ་རུང་བའི་ཆོས་རང་ངོས་ནས་བདེན་པར་མ་གྲུབ་པས་<span class=\"text-citation-style\">སྣང༵་</span>བ་ཙམ་དུ་ཟད་ཅིང་།གང་སྣང་ཐ་སྙད་ཙམ་དུ་བསླུ་བ་མེད་པར་གནས་པས་སྣང་ཙམ་དུ་<span class=\"text-citation-style\">སྲི༵ད་</span>ཅིང་ཡོད་པའི་མ་དག་ཀུན་ཉོན་འཁྲུལ་བའི་<span class=\"text-citation-style\">འཁོ༵ར་</span>བའི་སྣོད་བཅུད་རྒྱུ་འབྲས་ཀྱི་སྒྱུ་འཕྲུལ་སྣ་ཚོགས་ཀྱི་བཀོད་པ་འདི་དང་།དག་པ་རྣམ་བྱང་མྱང་<span class=\"text-citation-style\">འད༵ས་</span>ཀྱི་གྲོལ་བ་ཐར་པའི་ཡེ་ཤེས་ཡོན་ཏན་ཕྲིན་ལས་ཀྱི་རོལ་གར་བསམ་ལས་འདས་པའི་འཁྲུལ་གྲོལ་གྱི་ཆོས་འདི་<span class=\"text-citation-style\">ཐམ༵ས་</span><span class=\"text-citation-style\">ཅ༵ད་</span><span class=\"text-citation-style\">ཀུན༵</span>།"
                                        ),
                                        TableOfContentSegmentResponse(
                                            segment_id="abcdu7846-0d28-41e9-bff1-83ef53bfbju7",
                                            segment_number=3,
                                            content="འབྱུང་ཞིང་མཆེད་པའི་འབྱུང་གཞི།ཐིམ་ཞིང་སྡུད་པའི་སྡུད་གཞི།མཐར་ཐུག་ནི་སེམས་ཅན་རང་ཉིད་ཀྱི་སེམས་ཀྱི་གཤིས་ལུགས་ཕྲ་བ་གཉུག་མ་སེམས་ཀྱི་རྡོ་རྗེ་བྱང་ཆུབ་ཀྱི་སེམས་ངོ་བོའི་ཆ་ནས་སྟོང་ཞིང་ཀ་ནས་དག་པས།དངོས་པོ་རང་མཚན་གྱི་སྤྲོས་པའི་ཕྱོགས་ཀུན་དང་བྲལ་བ།རང་བཞིན་ཆ་ནས་གཏིང་གསལ་འགགས་པ་མེད་པའི་རང་བཞིན་ལྷུན་གྲུབ་ཀྱི་ཡོན་ཏན་འདུ་འབྲལ་སྤང་བས།"
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


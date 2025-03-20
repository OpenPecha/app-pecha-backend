
import logging
from typing import Optional, List
import asyncio

from beanie import PydanticObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from starlette import status
from time import time
import uuid
import datetime

from .texts.texts_repository import get_texts_by_id
from .texts.texts_response_models import Section
from .texts.segments.segments_repository import get_segments_by_list_of_id

number_language = {
    "bo": {
        "0": "༠",
        "1": "༡",
        "2": "༢",
        "3": "༣",
        "4": "༤",
        "5": "༥",
        "6": "༦",
        "7": "༧",
        "8": "༨",
        "9": "༩"
    },
    "en": {
        "0": "0",
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9"
    }
}

time_passed_word = {
    "Now" : {
        "en": "Now",
        "bo": "དད་ལྟ།"
    },
    "Min": {
        "en": "Min",
        "bo": "སྐར་མ།"
    },
    "Hr": {
        "en": "Hr",
        "bo": "ཆུ་ཚོད།"
    },
    "Day": {
        "en": "Day",
        "bo": "ཉིནམ།"
    },
    "Week": {
        "en": "Week",
        "bo": "གཟའ་འཁོར།"
    },
    "Month": {
        "en": "Month",
        "bo": "ཟླ་བ།"
    },
    "Year": {
        "en": "Year",
        "bo": "ལོ།"
    }
}

MINUTE_IN_SECONDS = 60
HOUR_IN_SECONDS = 3600
DAY_IN_SECONDS = 86400
WEEK_IN_SECONDS = 604800
MONTH_IN_SECONDS = 2592000
YEAR_IN_SECONDS = 31536000

async def replace_segments_id_with_segment_details_in_section(section: Optional[Section] = None) -> None:
    if section and section.segments:
        list_segment_id = [segment.segment_id for segment in section.segments if segment.segment_id]
        if list_segment_id:
            segments = await get_segments_by_list_of_id(segment_ids=list_segment_id)
            for segment in section.segments:
                segment_detail = segments.get(segment.segment_id)
                if segment_detail:
                    segment.content = segment_detail.content
                    segment.mapping = segment_detail.mapping
    if section.sections:
        await asyncio.gather(*[replace_segments_id_with_segment_details_in_section(section=sub_section) for sub_section in section.sections])


async def get_mapped_table_of_contents_segments(table_of_contents: List[Section]):
    await asyncio.gather(*[replace_segments_id_with_segment_details_in_section(section) for section in table_of_contents])
    return table_of_contents


def get_word(word: str, language: str):
    return get_value_from_dict(time_passed_word[word], language)

def divide(numerator: int, denominator: int):
    return numerator // denominator

def filter_number_by_language(value: str, language: str) -> str:
    return "".join([number_language[language][char] if "0" <= char <="9" else char for char in str(value)])

def time_passed(published_time: int, language: str):
    current_time_in_millisecond = int(time() * 1000)
    time_difference = (current_time_in_millisecond - published_time) // 1000

    if time_difference < MINUTE_IN_SECONDS:
        return get_word("Now", language)
    elif time_difference < HOUR_IN_SECONDS:
        time_passed_value = filter_number_by_language(str(divide(time_difference, 60)), language)
        return f"{time_passed_value} {get_word('Min', language)}"
    elif time_difference < DAY_IN_SECONDS:
        time_passed_value = filter_number_by_language(str(divide(time_difference,3600)), language)
        return f"{time_passed_value} {get_word('Hr', language)}"
    elif time_difference < WEEK_IN_SECONDS:
        time_passed_value = filter_number_by_language(str(divide(time_difference,86400)), language)
        return f"{time_passed_value} {get_word('Day', language)}"
    elif time_difference < MONTH_IN_SECONDS:
        time_passed_value = filter_number_by_language(str(divide(time_difference,604800)), language)
        return f"{time_passed_value} {get_word('Week', language)}"
    elif time_difference < YEAR_IN_SECONDS:
        time_passed_value = filter_number_by_language(str(divide(time_difference,2592000)), language)
        return f"{time_passed_value} {get_word('Month', language)}"
    else:
        time_passed_value = filter_number_by_language(str(divide(time_difference,31536000)), language)
        return f"{time_passed_value} {get_word('Year', language)}"

def get_current_date():
    return str(datetime.datetime.utcnow())

def millisecond_to_seconds(milliseconds: int) -> int:
    return milliseconds // 1000

def milliseconds_to_datetime(milliseconds: int) -> str:
    dt_object = datetime.datetime.utcfromtimestamp(millisecond_to_seconds(milliseconds))
    formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return str(formatted_time)

def get_current_time_in_millisecond():
    return int(time() * 1000)

async def valid_text(text_id: str) -> bool:
    text_detail = await get_texts_by_id(text_id=text_id)
    if text_detail is None:
        return False
    return True

def get_value_from_dict(values: dict[str, str], language: str):
    value = "" if not isinstance(values, dict) or not values else values.get(language, "")
    return value

def get_parent_id(parent_id: Optional[str]):
    topic_parent_id = None
    if parent_id is not None:
        try:
            topic_parent_id = PydanticObjectId(parent_id)
        except InvalidId as e:
            logging.debug("error with id: {}", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Parent id")

    return topic_parent_id

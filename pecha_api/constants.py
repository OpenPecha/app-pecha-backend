import logging
from typing import Optional

from beanie import PydanticObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from starlette import status
from time import time

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

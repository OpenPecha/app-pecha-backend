import logging
from typing import Optional

from beanie import PydanticObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from starlette import status


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

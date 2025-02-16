from typing import Optional

from beanie import PydanticObjectId


def get_value_from_dict(values: dict[str, str], language: str):
    value = "" if not isinstance(values, dict) or not values else values.get(language, "")
    return value

def get_parent_id(parent_id: Optional[str]):
    topic_parent_id = None
    if parent_id is not None:
        topic_parent_id = PydanticObjectId(parent_id)
    return topic_parent_id

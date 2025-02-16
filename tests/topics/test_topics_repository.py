from beanie import PydanticObjectId

from pecha_api.topics.topics_repository import  get_parent_id


def test_get_parent_id_not_none():
    parent_id = get_parent_id(parent_id="60d21b4667d0d8992e610c85")
    assert parent_id == PydanticObjectId("60d21b4667d0d8992e610c85")


def test_get_parent_id_none():
    parent_id = get_parent_id(parent_id=None)
    assert parent_id is None

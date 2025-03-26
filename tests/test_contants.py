from beanie import PydanticObjectId
from fastapi import HTTPException
from starlette import status

from pecha_api.utils import Utils


def test_get_parent_id_not_none():
    parent_id = Utils.get_parent_id(parent_id="60d21b4667d0d8992e610c85")
    assert parent_id == PydanticObjectId("60d21b4667d0d8992e610c85")

def test_get_parent_id_invalid_id():
    try:
        Utils.get_parent_id(parent_id="60d21b4667d0d8992e610c8")
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST


def test_get_parent_id_none():
    parent_id = Utils.get_parent_id(parent_id=None)
    assert parent_id is None

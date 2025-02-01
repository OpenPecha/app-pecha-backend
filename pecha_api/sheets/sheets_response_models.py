from typing import List

from pydantic import BaseModel


class Publisher(BaseModel):
    id: str
    name: str
    profile_url: str
    image_url: str

class SheetModel(BaseModel):
    id: str
    title: str
    summary: str
    publisher: Publisher

class SheetsResponse(BaseModel):
    sheets: List[SheetModel]



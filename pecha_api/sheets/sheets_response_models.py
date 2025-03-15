from typing import List, Dict, Union

from pydantic import BaseModel, model_validator
from ..constants import filter_number_by_language, get_value_from_dict, time_passed, milliseconds_to_datetime
from .sheets_models import Source, Text, Media

class Publisher(BaseModel):
    id: str
    name: str
    profile_url: str | None
    image_url: str | None

class CreateSheetRequest(BaseModel):
    titles: str
    summaries: str
    source: List[Union[Source, Text, Media]]
    publisher_id: str
    topic_id: List[str]
    sheetLanguage: str


class SheetModel(BaseModel):
    id: str
    title: str
    summary: str
    published_date: str
    time_passed: str
    views: str
    likes: List[str]
    topics: List[str]
    publisher: Publisher
    language: str

    @model_validator(mode = "before")
    @classmethod
    def filter_model_language(cls, values):
        values["topics"] = [get_value_from_dict(topic, values["language"]) for topic in values["topics"]]
        values["views"] = filter_number_by_language(str(values["views"]), values["language"])
        values["time_passed"] = time_passed(values["published_date"], values["language"])
        values["published_date"] = filter_number_by_language(milliseconds_to_datetime(values["published_date"]), values["language"])

        return values
    
    class Config:
        extra = "allow"
    

class SheetsResponse(BaseModel):
    sheets: List[SheetModel]
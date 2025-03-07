from typing import List, Dict, Union

from pydantic import BaseModel, model_validator
from ..constants import filter_number_by_language, get_value_from_dict, time_passed
from .sheets_models import Source, Text, Media

class Publisher(BaseModel):
    id: str
    name: str
    profile_url: str
    image_url: str

class CreateSheetRequest(BaseModel):
    titles: Dict[str, str]
    summaries: Dict[str, str]
    source: List[Union[Source, Text, Media]]
    publisher_id: str
    topic_id: List[str]


class SheetModel(BaseModel):
    id: str
    title: str
    summary: str
    published_date: str
    views: str
    topics: List[str]
    published_time: str
    publisher: Publisher
    language: str

    @model_validator(mode = "before")
    @classmethod
    def filter_model_language(cls, values):
        values["topics"] = [get_value_from_dict(topic, values["language"]) for topic in values["topics"]]
        values["views"] = filter_number_by_language(values["views"], values["language"]) if values["language"] == "bo" else values["views"]
        values["date"] = filter_number_by_language(values["date"], values["language"]) if values["language"] == "bo" else values["date"]

        values["published_time"] = time_passed(values["published_time"], values["language"])
        
        return values
    
    class Config:
        extra = "allow"
    

class SheetsResponse(BaseModel):
    sheets: List[SheetModel]
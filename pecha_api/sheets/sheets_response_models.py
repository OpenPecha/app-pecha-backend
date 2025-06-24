from __future__ import annotations

from typing import List, Union, Optional

from pydantic import BaseModel, model_validator

from pecha_api.utils import Utils

from pecha_api.texts.segments.segments_models import SegmentType

class Source(BaseModel):
    position: int
    type: SegmentType
    content: str

class Content(BaseModel):
    position: int
    type: SegmentType
    content: str

class Media(BaseModel):
    position: int
    type: SegmentType
    content: str

class Like(BaseModel):
    username: str
    name: str
    
class CreateSheetRequest(BaseModel):
    title: str
    source: List[Union[Source, Content, Media]]

class Publisher(BaseModel):
    id: str
    name: str
    profile_url: str | None
    image_url: str | None


class CreateSheetResponse(BaseModel):
    _id: str
    titles: str
    summaries: str
    source: List[Union[Source, Content, Media]]
    publisher_id: str
    creation_date: str
    modified_date: str
    published_date: int
    views: int
    likes: List[str]
    collection: List[str]
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
        values["topics"] = [Utils.get_value_from_dict(topic, values["language"]) for topic in values["topics"]]
        values["views"] = Utils.get_number_by_language(values["views"], values["language"])
        values["time_passed"] = Utils.time_passed(values["published_date"], values["language"])
        milliseconds_to_date_time = Utils.get_date_time_from_epoch(values["published_date"])
        values["published_date"] = Utils.get_number_by_language(milliseconds_to_date_time, values["language"])

        return values
    
    class Config:
        extra = "allow"
    

class SheetsResponse(BaseModel):
    sheets: List[SheetModel]

class SheetIdRequest(BaseModel):
    id: str

class SheetImageResponse(BaseModel):
    url: str
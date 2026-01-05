from typing import Union
from pydantic import BaseModel


class TextUploadRequest(BaseModel):
    destination_url: str
    openpecha_api_url: str
    text_id: str


class TextUploadResponse(BaseModel):
    message: Union[dict[str, str], str]

from pydantic import BaseModel
from pydantic_core.core_schema import str_schema

class TextUploadRequest(BaseModel):
    destination_url: str
    openpecha_api_url: str
    access_token: str


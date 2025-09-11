from pydantic import BaseModel
from pecha_api.plans.response_message import IMAGE_UPLOAD_SUCCESS

class MediaUploadResponse(BaseModel):
    url: str
    key: str
    path: str
    message: str = IMAGE_UPLOAD_SUCCESS


class Error(BaseModel):
    error: str
    message: str
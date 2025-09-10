from pydantic import BaseModel

class MediaUploadResponse(BaseModel):
    url: str
    key: str
    message: str = "Image uploaded successfully"


class Error(BaseModel):
    error: str
    message: str

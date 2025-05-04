from pydantic import BaseModel

class GroupDTO(BaseModel):
    id: str
    type: str

class CreateGroupRequest(BaseModel):
    type: str
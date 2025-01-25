from typing import  Dict

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class Term(Document,BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    slug: str
    titles:  Dict[str,str]  # Dictionary with language_id as key and title as value

    class Settings:
        # Define the collection name in MongoDB
        collection = "terms"

    class Config:
        # Config for Pydantic to allow alias to be used
        allow_population_by_field_name = True


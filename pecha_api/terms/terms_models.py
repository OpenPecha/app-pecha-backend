from typing import Dict

from beanie import Document, PydanticObjectId
from pydantic import  Field


class Term(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    slug: str
    titles: Dict[str, str]  # Dictionary with language_id as key and title as value

    class Settings:
        # Define the collection name in MongoDB
        collection = "terms"

    class Config:
        # Config for Pydantic to allow alias to be used
        populate_by_name = True

    # Define indexes directly within the model
    class __Indexes__:
        # Create a unique index on the `slug` field
        indexes = [("slug", 1)]

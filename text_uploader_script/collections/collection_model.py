from pydantic import BaseModel

class CollectionPayload(BaseModel):
    pecha_collection_id: str
    slug: str
    titles: dict[str, str]
    descriptions: dict[str, str]
    parent_id: str | None = None
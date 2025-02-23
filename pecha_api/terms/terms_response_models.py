from typing import Dict, List, Optional

from pydantic import BaseModel


class CreateTermRequest(BaseModel):
    slug: str
    titles: Dict[str, str]
    descriptions: Dict[str, str]
    parent_id: Optional[str]

class UpdateTermRequest(BaseModel):
    titles: Dict[str, str]
    descriptions: Dict[str, str]

class TermsModel(BaseModel):
    id: str
    title: str
    description: str
    slug: str
    has_child: bool


class TermsResponse(BaseModel):
    parent: Optional[TermsModel]
    terms: List[TermsModel]
    total: int
    skip: int
    limit: int

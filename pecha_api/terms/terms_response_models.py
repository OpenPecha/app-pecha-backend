from typing import Dict, List

from pydantic import BaseModel


class CreateTermRequest(BaseModel):
    slug: str
    titles: Dict[str, str]
    descriptions: Dict[str, str]

class UpdateTermRequest(BaseModel):
    titles: Dict[str, str]
    descriptions: Dict[str, str]

class TermsModel(BaseModel):
    id: str
    title: str
    description: str
    slug: str


class TermsResponse(BaseModel):
    terms: List[TermsModel]
    total: int
    skip: int
    limit: int

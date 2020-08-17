from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class JurisdictionEnum(str, Enum):
    state = "state"
    municipality = "municipality"
    government = "government"


class PaginationMeta(BaseModel):
    per_page: int
    page: int
    max_page: int
    total_items: int


class Organization(BaseModel):
    id: str
    name: str
    classification: str

    class Config:
        orm_mode = True


class Jurisdiction(BaseModel):
    id: str
    name: str
    classification: JurisdictionEnum
    division_id: Optional[str]
    url: str
    # TODO: add these
    # people_last_updated: Optional[datetime.datetime]
    # bills_last_updated: Optional[datetime.datetime]
    organizations: List[Organization]

    class Config:
        orm_mode = True
